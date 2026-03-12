"""
Sephora Thailand Scraper  (with Bazaarvoice reviews)
=====================================================
Source: https://www.sephora.co.th/
pip install undetected-chromedriver selenium webdriver-manager pandas pillow requests
python sephora_th_scraper.py
"""

import time, random, datetime, re, hashlib, math, json
from io import BytesIO
from pathlib import Path
from collections import Counter

import requests as req_lib
import pandas as pd
from PIL import Image as PILImage

try:
    import undetected_chromedriver as uc
    USE_UC = True
    print("✅ Using undetected-chromedriver")
except ImportError:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from webdriver_manager.chrome import ChromeDriverManager
    USE_UC = False

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# ================================================================
# CONFIG
# ================================================================

HEADLESS        = False
IMG_THUMB_SIZE  = (120, 120)
AUTOSAVE_EVERY  = 30
DELAY_MIN       = 1.2
DELAY_MAX       = 2.2
MAX_REVIEWS     = 20        # reviews per product (0 = skip reviews)

OUTPUT_DIR = Path(__file__).parent / "data_products"
IMG_DIR    = OUTPUT_DIR / "images"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
IMG_DIR.mkdir(parents=True, exist_ok=True)

timestamp    = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
OUTPUT_CSV   = OUTPUT_DIR / f"sephora_th_{timestamp}.csv"
REVIEWS_CSV  = OUTPUT_DIR / f"sephora_th_reviews_{timestamp}.csv"

BASE = "https://www.sephora.co.th"

# category URL → (major_category, total_pages)
SEPHORA_CATEGORIES = {
    "cleanser":    ("https://www.sephora.co.th/categories/clean/clean-skincare/cleanser-and-exfoliator", 2),
    "toner":       ("https://www.sephora.co.th/categories/clean/clean-skincare/toner",                  1),
    "moisturizer": ("https://www.sephora.co.th/categories/clean/clean-skincare/moisturiser",            3),
    "mask":        ("https://www.sephora.co.th/categories/clean/clean-skincare/masks-and-treatments",   4),
    "sunscreen":   ("https://www.sephora.co.th/categories/clean/clean-skincare/sun-care",               1),
}

# ================================================================
# TAG RULES
# ================================================================

ACTIVE_RULES = {
    "retinol":["retinol"],"retinal":["retinal"],
    "aha":["glycolic acid","lactic acid","mandelic acid"],
    "bha":["salicylic acid"],"pha":["gluconolactone"],
    "vitamin_c":["ascorb","ascorbyl"],"niacinamide":["niacinamide"],
    "peptide":["peptide"],"ceramide":["ceramide"],
    "zinc_oxide":["zinc oxide"],"titanium_dioxide":["titanium dioxide"],
}
FUNCTION_RULES = {
    "brightening":["ascorb","niacinamide","arbutin","kojic","tranexamic","licorice"],
    "anti_aging":["retinol","retinal","peptide","bakuchiol","adenosine","matrixyl"],
    "acne_control":["salicylic acid","benzoyl peroxide","sulfur","zinc","tea tree"],
    "calming":["centella","allantoin","bisabolol","aloe","chamomile","panthenol"],
    "barrier_repair":["ceramide","cholesterol","fatty acid","phospholipid"],
    "hydrating":["hyaluronic","sodium hyaluronate","glycerin","squalane","urea"],
    "exfoliating":["glycolic acid","lactic acid","mandelic acid","salicylic acid","gluconolactone"],
    "antioxidant":["tocopherol","ferulic","resveratrol","green tea","ascorbyl"],
    "moisturizing":["petrolatum","dimethicone","shea butter","jojoba","caprylic"],
}
SKINTYPE_RULES = {
    "oily":["salicylic acid","niacinamide","zinc oxide","kaolin","clay","witch hazel","tea tree"],
    "dry":["ceramide","shea butter","squalane","hyaluronic acid","sodium hyaluronate","glycerin","petrolatum","urea"],
    "sensitive":["centella asiatica","allantoin","bisabolol","aloe barbadensis","aloe vera","panthenol","oat","chamomile","dipotassium glycyrrhizate"],
    "combination":["glycolic acid","lactic acid","mandelic acid","azelaic acid","retinol","retinal"],
}
FUNCTION_TAG_HINTS = {
    "acne_control":"oily","exfoliating":"combination","barrier_repair":"dry",
    "calming":"sensitive","hydrating":"dry","brightening":"combination","anti_aging":"combination",
}

def clean(t): return " ".join(str(t).split()).strip()

def detect_tags(text, rules):
    t = text.lower()
    return sorted(tag for tag, kws in rules.items() if any(k in t for k in kws))

def detect_skintype(ingredients, function_tags):
    ingr = str(ingredients).lower()
    tags = str(function_tags).lower()
    scores = {st: sum(1 for kw in kws if kw in ingr) for st, kws in SKINTYPE_RULES.items()}
    max_s = max(scores.values())
    if max_s > 0:
        return ",".join(st for st, sc in scores.items() if sc == max_s)
    for tag, st in FUNCTION_TAG_HINTS.items():
        if tag in tags: return st
    return "all"

def detect_subtype(name, ingr, cat):
    t = (name + " " + ingr).lower()
    if cat == "sunscreen":
        m = "zinc oxide" in t or "titanium dioxide" in t
        c = any(k in t for k in ["avobenzone","octinoxate","octocrylene"])
        return "hybrid_sunscreen" if m and c else ("mineral_sunscreen" if m else "chemical_sunscreen")
    if "retinal" in t: return "retinal_serum"
    if "retinol" in t: return "retinol_serum"
    if "salicylic acid" in t: return "bha_exfoliator"
    if "glycolic acid" in t or "lactic acid" in t: return "aha_exfoliator"
    return cat

def safe_val(val):
    if val is None: return None
    if isinstance(val, float) and (math.isnan(val) or math.isinf(val)): return None
    return val

# ================================================================
# IMAGE DOWNLOAD
# ================================================================

def download_image(img_url):
    if not img_url or img_url.startswith("data:"): return None
    if img_url.startswith("//"): img_url = "https:" + img_url
    try:
        h = hashlib.md5(img_url.encode()).hexdigest()[:12]
        p = IMG_DIR / f"sep_{h}.jpg"
        if p.exists(): return p
        r = req_lib.get(img_url, headers={"User-Agent":"Mozilla/5.0","Referer":BASE+"/"}, timeout=10)
        if r.status_code != 200: return None
        img = PILImage.open(BytesIO(r.content)).convert("RGB")
        img.thumbnail(IMG_THUMB_SIZE, PILImage.LANCZOS)
        img.save(p, "JPEG", quality=85)
        return p
    except: return None

# ================================================================
# DRIVER
# ================================================================

def make_driver():
    if USE_UC:
        opts = uc.ChromeOptions()
        if HEADLESS: opts.add_argument("--headless=new")
        opts.add_argument("--window-size=1440,900")
        opts.add_argument("--lang=th-TH")
        opts.add_argument("--no-sandbox")
        return uc.Chrome(options=opts, version_main=None)
    else:
        opts = Options()
        if HEADLESS: opts.add_argument("--headless=new")
        opts.add_argument("--window-size=1440,900")
        opts.add_argument("--disable-blink-features=AutomationControlled")
        opts.add_experimental_option("excludeSwitches",["enable-automation"])
        opts.add_experimental_option("useAutomationExtension",False)
        opts.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/122 Safari/537.36")
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()),options=opts)
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument",
            {"source":"Object.defineProperty(navigator,'webdriver',{get:()=>undefined})"})
        return driver

def close_extra_tabs(driver):
    try:
        handles = driver.window_handles
        if len(handles) > 1:
            main = handles[0]
            for h in handles[1:]:
                driver.switch_to.window(h); driver.close()
            driver.switch_to.window(main)
    except: pass

def ensure_window(driver):
    try: _ = driver.current_url; return True
    except:
        try:
            h = driver.window_handles
            if h: driver.switch_to.window(h[0]); return True
        except: pass
        return False

def dismiss_popups(driver):
    selectors = [
        "button[aria-label='Close']","button[aria-label='close']",
        "[class*='modal'] button[class*='close']",
        "[class*='popup'] button[class*='close']",
        ".modal-close","[data-dismiss='modal']",
        "#onetrust-accept-btn-handler",
    ]
    for sel in selectors:
        try:
            for el in driver.find_elements(By.CSS_SELECTOR, sel):
                if el.is_displayed():
                    driver.execute_script("arguments[0].click();", el)
                    time.sleep(0.4)
        except: pass
    try:
        driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
        time.sleep(0.3)
    except: pass

# ================================================================
# GET PRODUCT LINKS FROM CATEGORY PAGE
# ================================================================

def get_product_links_from_page(driver):
    return driver.execute_script("""
        return [...new Set(
            Array.from(document.querySelectorAll(".product-card a.product-card-image-link, .product-card a.product-card-description"))
                .map(a => a.href)
                .filter(h => h.includes("/products/"))
        )];
    """) or []

def get_all_product_links(driver, base_url, total_pages, category):
    all_links = []
    for page in range(1, total_pages + 1):
        url = base_url if page == 1 else f"{base_url}?page={page}"
        print(f"  📄 page {page}/{total_pages} → {url}")
        close_extra_tabs(driver)
        try:
            driver.get(url)
            time.sleep(3)
            dismiss_popups(driver)
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".products-card-container, .product-card"))
            )
            time.sleep(1.5)
            for scroll_y in [300, 600, 900, 1200, 2000]:
                driver.execute_script(f"window.scrollTo(0, {scroll_y});")
                time.sleep(0.4)
            links = get_product_links_from_page(driver)
            new   = [l for l in links if l not in all_links]
            all_links.extend(new)
            print(f"     +{len(new)} links  (total: {len(all_links)})")
        except TimeoutException:
            print(f"  ⚠️  Timeout page {page}")
        except Exception as e:
            print(f"  ❌ {e}")
        time.sleep(random.uniform(DELAY_MIN, DELAY_MAX))
    return all_links

# ================================================================
# SCRAPE REVIEWS (Bazaarvoice)
# ================================================================

def scrape_reviews_bv(driver, product_url, bv_product_id):
    """
    ดึง reviews จาก Bazaarvoice widget
    selectors จาก HTML ที่ผู้ใช้ส่งมา:
      - section[id^="bv-review-"]           → แต่ละ review
      - [role="img"][aria-label]             → rating เช่น "5 จาก 5 ดาว"
      - h3.bv-rnr__sc-16dr7i1-17            → review title
      - div[id^="bv-review-text-"]           → review body
      - span.bv-rnr__sc-1r4hv38-0           → author
      - span.bv-rnr__g3jej5-1               → date
    """
    if not bv_product_id or MAX_REVIEWS == 0:
        return []

    reviews = []
    try:
        # scroll ลงไปที่ reviews section ก่อน
        driver.execute_script("""
            const el = document.querySelector('#reviews_container, [data-bv-show="reviews"]');
            if (el) el.scrollIntoView({behavior:'smooth', block:'center'});
        """)
        time.sleep(2)
        dismiss_popups(driver)

        # รอ Bazaarvoice widget โหลด
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'section[id^="bv-review-"]'))
            )
            time.sleep(1)
        except TimeoutException:
            return []   # ไม่มี reviews

        raw = driver.execute_script("""
            const reviews = [];
            document.querySelectorAll('section[id^="bv-review-"]').forEach(sec => {
                // author
                const author = (sec.querySelector('[class*="sc-1r4hv38-0"], [class*="dWWqxa"]')?.innerText || "").trim();

                // rating — จาก aria-label เช่น "5 จาก 5 ดาว" หรือ "4 จาก 5 ดาว"
                let rating = null;
                const ratingEl = sec.querySelector('[role="img"][aria-label]');
                if (ratingEl) {
                    const m = (ratingEl.getAttribute("aria-label") || "").match(/(\\d+)\\s*จาก\\s*5/);
                    if (m) rating = parseInt(m[1]);
                }
                // fallback: abbr title
                if (!rating) {
                    const abbr = sec.querySelector('abbr[title]');
                    if (abbr) {
                        const m2 = (abbr.getAttribute("title") || "").match(/(\\d+)\\s*จาก\\s*5/);
                        if (m2) rating = parseInt(m2[1]);
                    }
                }

                // title — h3
                const title = (sec.querySelector('h3')?.innerText || "").trim();

                // body — div id="bv-review-text-..."
                const body = (sec.querySelector('div[id^="bv-review-text-"]')?.innerText || "").trim();

                // date
                const date = (sec.querySelector('[class*="g3jej5-1"], [class*="jolJQc"]')?.innerText || "").trim();

                reviews.push({author, rating, title, body, date});
            });
            return reviews;
        """)

        for r in (raw or []):
            if not r.get("body"): continue
            reviews.append({
                "product_url": product_url,
                "bv_product_id": bv_product_id,
                "author":  clean(r.get("author","")),
                "rating":  r.get("rating"),
                "title":   clean(r.get("title","")),
                "body":    clean(r.get("body","")),
                "date":    clean(r.get("date","")),
                "source":  "bazaarvoice",
            })
            if len(reviews) >= MAX_REVIEWS:
                break

    except Exception as e:
        print(f"    ⚠️  Reviews error: {e}")

    return reviews

# ================================================================
# SCRAPE PRODUCT DETAIL
# ================================================================

def scrape_product(driver, url, category):
    for attempt in range(3):
        try:
            close_extra_tabs(driver)
            driver.get(url)
            time.sleep(2)
            dismiss_popups(driver)

            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.TAG_NAME, "h1"))
            )
            driver.execute_script("window.scrollTo(0, 600);")
            time.sleep(1)

            data = driver.execute_script("""
                const get  = sel => (document.querySelector(sel)?.innerText || "").trim();

                const name  = get("h1.product-name, h1, [class*='product-name']");
                const brand = get(".product-brand a, .product-brand, [class*='brand-name']");

                const price = get(".sell-price, .product-price .sell-price, [class*='sell-price']")
                    .replace(/[^\\d.]/g, "");

                // Rating จาก .stars CSS var --highlightedPercentage
                let rating = "";
                const starsEl = document.querySelector(".stars, [class*='stars']");
                if (starsEl) {
                    const style = starsEl.getAttribute("style") || "";
                    const m = style.match(/--highlightedPercentage:\\s*([\\d.]+)%/);
                    if (m) rating = (parseFloat(m[1]) / 20).toFixed(1);
                }

                // Rating count
                const ratingCount = get(".reviews-count, [class*='reviews-count']")
                    .replace(/[^\\d]/g, "");

                // Bazaarvoice product ID จาก data-bv-product-id
                let bvProductId = "";
                const bvEl = document.querySelector("[data-bv-product-id]");
                if (bvEl) bvProductId = bvEl.getAttribute("data-bv-product-id") || "";

                // Image
                let imgUrl = "";
                for (const sel of [
                    ".product-image-zoom img",
                    ".product-images img",
                    "[class*='product-image'] img",
                    ".swiper-slide.swiper-slide-active img",
                    "img.product-card-image"
                ]) {
                    const img = document.querySelector(sel);
                    if (img) {
                        imgUrl = img.getAttribute("data-src") || img.src || "";
                        if (imgUrl && !imgUrl.startsWith("data:")) break;
                    }
                }

                // Ingredients
                let ingredients = "";
                const allEls = Array.from(document.querySelectorAll("*"));
                for (const el of allEls) {
                    const txt = (el.innerText || "").trim();
                    if ((txt.toLowerCase().startsWith("ingredient") || txt.startsWith("ส่วนผสม"))
                        && txt.length > 80 && txt.includes(",")) {
                        ingredients = txt.replace(/^(ingredients|ส่วนผสม)[:\\s]*/i, "").trim();
                        break;
                    }
                }
                if (!ingredients) {
                    for (const el of document.querySelectorAll("p,div,span,li")) {
                        const txt = (el.innerText || "").trim();
                        if (txt.includes("Water") && txt.split(",").length > 5
                            && txt.length > 100 && txt.length < 6000) {
                            ingredients = txt; break;
                        }
                    }
                }

                return {name, brand, price, rating, ratingCount, bvProductId, imgUrl, ingredients};
            """)

            name         = clean(data.get("name",""))
            brand        = clean(data.get("brand",""))
            price_raw    = clean(data.get("price",""))
            rating       = clean(data.get("rating",""))
            rating_cnt   = clean(data.get("ratingCount",""))
            bv_pid       = clean(data.get("bvProductId",""))
            img_url      = clean(data.get("imgUrl",""))
            ingr_raw     = clean(data.get("ingredients",""))

            if len(ingr_raw) < 20:
                ingr_raw = _try_ingredients_tab(driver)

            ingr_list  = [i.strip() for i in re.split(r",\s*", ingr_raw) if i.strip() and len(i.strip()) > 1]
            ingr_clean = clean(", ".join(ingr_list))

            try: price = float(price_raw) if price_raw else None
            except: price = None

            function_tags = ",".join(detect_tags(ingr_clean, FUNCTION_RULES))
            active_tags   = ",".join(detect_tags(ingr_clean, ACTIVE_RULES))
            skintype      = detect_skintype(ingr_clean, function_tags)
            img_local     = download_image(img_url)

            # ดึง reviews (scroll ลงหน้าเดียวกัน)
            reviews = scrape_reviews_bv(driver, url, bv_pid)

            return {
                "product": {
                    "product_url":      url,
                    "name":             name,
                    "brand":            brand,
                    "major_category":   category,
                    "subtype":          detect_subtype(name, ingr_clean, category),
                    "price":            price,
                    "rating":           rating or None,
                    "rating_count":     int(rating_cnt) if rating_cnt.isdigit() else None,
                    "active_tags":      active_tags,
                    "function_tags":    function_tags,
                    "skintype":         skintype,
                    "ingredients_raw":  ingr_clean,
                    "ingredients_list": ",".join(ingr_list),
                    "image_url":        img_url,
                    "image_local":      str(img_local) if img_local else "",
                    "source":           "sephora_th",
                    "bv_product_id":    bv_pid,
                },
                "reviews": reviews,
            }

        except Exception as e:
            print(f"    ⚠️  Retry {attempt+1}: {e}")
            ensure_window(driver)
            time.sleep(2 ** attempt)
    return None

def _try_ingredients_tab(driver):
    try:
        for tab in driver.find_elements(By.CSS_SELECTOR,
            "[role='tab'], button, summary, [class*='tab-item'], [class*='accordion']"):
            txt = (tab.text or "").lower()
            if "ingredient" in txt or "ส่วนผสม" in txt:
                driver.execute_script("arguments[0].click();", tab)
                time.sleep(1.5)
                break
        content = driver.execute_script("""
            for (const el of document.querySelectorAll(
                "[aria-selected='true'] + *, .tab-content.active, details[open], [aria-expanded='true'] + *"
            )) {
                if (el.innerText && el.innerText.length > 50) return el.innerText.trim();
            }
            return "";
        """)
        return clean(content or "")
    except: return ""

# ================================================================
# SAVE CSV
# ================================================================

def _save_csv(records, path):
    df = pd.DataFrame(records)
    for col in df.columns:
        df[col] = df[col].apply(safe_val)
    df.to_csv(path, index=False, encoding="utf-8-sig")
    print(f"  📄 Saved → {path.name}")

# ================================================================
# MAIN
# ================================================================

def run():
    print("=" * 60)
    print("  💄  Sephora Thailand Scraper  (+ Bazaarvoice Reviews)")
    print(f"  📁  {OUTPUT_DIR}")
    print("=" * 60)

    driver   = make_driver()
    products = []
    all_reviews = []

    try:
        print("\n🌐 Loading sephora.co.th ...")
        driver.get(BASE)
        time.sleep(5)
        dismiss_popups(driver)
        time.sleep(1)
        print("  ✅ Ready\n")

        for cat_name, (cat_url, total_pages) in SEPHORA_CATEGORIES.items():
            print(f"\n{'='*50}")
            print(f"📂  {cat_name.upper()}  ({total_pages} pages)")
            print(f"{'='*50}")

            if not ensure_window(driver):
                print("  ❌ Window lost — stopping"); break

            links = get_all_product_links(driver, cat_url, total_pages, cat_name)
            print(f"\n  📋 {len(links)} products to scrape")

            for i, link in enumerate(links):
                if not ensure_window(driver): break
                if any(p["product_url"] == link for p in products):
                    print(f"  [{i+1:3d}/{len(links)}] ⏭️  Duplicate")
                    continue

                print(f"  [{i+1:3d}/{len(links)}] ", end="", flush=True)
                result = scrape_product(driver, link, cat_name)

                if result:
                    p = result["product"]
                    r = result["reviews"]
                    products.append(p)
                    all_reviews.extend(r)

                    rev_icon = f"💬{len(r)}" if r else "  "
                    img_icon = "🖼️ " if p.get("image_local") else "📷 "
                    print(f"{img_icon}{rev_icon}  {p['brand']} — {p['name'][:40]}  [{p['skintype']}]")
                else:
                    print("❌ FAILED")

                if len(products) % AUTOSAVE_EVERY == 0 and products:
                    _save_csv(products, OUTPUT_DIR / "autosave_sephora_th.csv")
                    if all_reviews:
                        _save_csv(all_reviews, OUTPUT_DIR / "autosave_sephora_th_reviews.csv")
                    print(f"  💾 Autosaved {len(products)} products, {len(all_reviews)} reviews")

                time.sleep(random.uniform(DELAY_MIN, DELAY_MAX))

    finally:
        try: driver.quit()
        except: pass

    if not products:
        print("\n❌ No data scraped"); return

    _save_csv(products, OUTPUT_CSV)
    if all_reviews:
        _save_csv(all_reviews, REVIEWS_CSV)

    cat_c  = Counter(p.get("major_category","?") for p in products)
    img_ok = sum(1 for p in products if p.get("image_local"))
    bv_ok  = sum(1 for p in products if p.get("bv_product_id"))

    print(f"\n{'='*60}")
    print(f"✅  DONE  —  {len(products):,} products  |  {len(all_reviews):,} reviews  |  {img_ok:,} images")
    print(f"   📄 Products CSV  → {OUTPUT_CSV.name}")
    if all_reviews:
        print(f"   💬 Reviews CSV   → {REVIEWS_CSV.name}")
    print(f"   🔖 BV IDs found  → {bv_ok}/{len(products)}")
    print(f"\n   Category breakdown:")
    for cat, cnt in sorted(cat_c.items(), key=lambda x: -x[1]):
        print(f"     {cat:<20} {cnt:>4}")
    print(f"{'='*60}")

if __name__ == "__main__":
    run()