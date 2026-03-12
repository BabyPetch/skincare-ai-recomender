"""
Paula's Choice Thailand Scraper
================================
Source: https://paulaschoice.th/
pip install undetected-chromedriver selenium webdriver-manager pandas pillow requests
python paulaschoice_scraper.py
"""

import time, random, datetime, re, hashlib, math
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
from selenium.common.exceptions import TimeoutException

# ================================================================
# CONFIG
# ================================================================

HEADLESS       = False
IMG_THUMB_SIZE = (120, 120)
AUTOSAVE_EVERY = 20
DELAY_MIN      = 1.0
DELAY_MAX      = 2.0
MAX_REVIEW_PAGES = 5   # ดึงรีวิวสูงสุดกี่หน้าต่อสินค้า

OUTPUT_DIR = Path(__file__).parent / "data_products"
IMG_DIR    = OUTPUT_DIR / "images"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
IMG_DIR.mkdir(parents=True, exist_ok=True)

timestamp    = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
OUTPUT_CSV   = OUTPUT_DIR / f"paulaschoice_th_{timestamp}.csv"
REVIEWS_CSV  = OUTPUT_DIR / f"paulaschoice_th_reviews_{timestamp}.csv"

BASE = "https://paulaschoice.th"

PC_CATEGORIES = {
    "cleanser":    f"{BASE}/collections/cleansers",
    "toner":       f"{BASE}/collections/toners",
    "exfoliator":  f"{BASE}/collections/exfoliate",
    "serum":       f"{BASE}/collections/face-serum-treatment",
    "moisturizer": f"{BASE}/collections/moisturizers",
    "sunscreen":   f"{BASE}/collections/sunscreen",
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
        p = IMG_DIR / f"pc_{h}.jpg"
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
        opts.add_argument("--lang=en-US")
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
        "[data-testid='modal-close']","[data-testid='close-button']",
        ".modal__close",".modal-close",
        "[class*='CloseButton']","[class*='close-button']","[class*='closeButton']",
        "#onetrust-accept-btn-handler",".onetrust-close-btn-handler",
        ".popup-close","[class*='popup'] button",
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
# GET PRODUCT LINKS
# ================================================================

def get_product_links(driver, category_url, category):
    """Shopify pagination: ?page=2, ?page=3 ..."""
    links = []
    page  = 1

    while True:
        url = category_url if page == 1 else f"{category_url}?page={page}"
        print(f"  📄 page {page} → {url}")
        close_extra_tabs(driver)

        try:
            driver.get(url)
            time.sleep(2.5)
            dismiss_popups(driver)
            time.sleep(1)

            # รอให้มี product link ขึ้น
            try:
                WebDriverWait(driver, 15).until(
                    lambda d: len(d.find_elements(By.CSS_SELECTOR, "a[href*='/products/']")) > 0
                )
            except TimeoutException:
                print(f"  ⚠️  Timeout — no products found")
                sample = driver.execute_script(
                    "return Array.from(document.querySelectorAll('a[href]')).map(a=>a.href).slice(0,6);"
                )
                print(f"     Sample hrefs: {sample}")
                break

            found = driver.execute_script("""
                return [...new Set(
                    Array.from(document.querySelectorAll("a[href*='/products/']"))
                        .map(a => a.href)
                        .filter(h => /paulaschoice\\.th\\/products\\/[\\w-]+$/.test(h))
                )];
            """) or []

            new_links = [l for l in found if l not in links]
            if not new_links:
                print(f"  ✅ No new links — end of category")
                break

            links.extend(new_links)
            print(f"     +{len(new_links)} links  (total: {len(links)})")

            # เช็ค next page
            has_next = driver.execute_script("""
                return !!(
                    document.querySelector('a[rel="next"]') ||
                    document.querySelector('.pagination__next:not([aria-disabled])') ||
                    document.querySelector('a[href*="?page="]')
                );
            """)
            if not has_next:
                print(f"  ✅ Last page")
                break

            page += 1
            time.sleep(random.uniform(DELAY_MIN, DELAY_MAX))

        except Exception as e:
            print(f"  ❌ {e}")
            break

    return links

# ================================================================
# SCRAPE REVIEWS
# ================================================================

def scrape_reviews(driver, product_url, product_name):
    """ดึงรีวิวจาก product page — รองรับ Shopify review apps (Stamped, Judge.me, Okendo)"""
    reviews = []

    for page in range(1, MAX_REVIEW_PAGES + 1):
        # ลอง scroll ไปที่ review section
        if page == 1:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight * 0.7);")
            time.sleep(2)

            # ลองคลิก Load More reviews ถ้ามี
            try:
                load_more = driver.find_elements(By.XPATH,
                    "//*[contains(translate(text(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'load more review') or "
                    "contains(translate(text(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'show more review')]"
                )
                for btn in load_more:
                    if btn.is_displayed():
                        driver.execute_script("arguments[0].click();", btn)
                        time.sleep(1.5)
                        break
            except: pass

        # ดึงรีวิวจาก DOM
        raw_reviews = driver.execute_script("""
            const reviews = [];

            // Stamped.io
            document.querySelectorAll(".stamped-review, [class*='stamped-review']").forEach(r => {
                const author = (r.querySelector("[class*='author'], .stamped-review-author")?.innerText || "").trim();
                const rating = (r.querySelector("[data-rating], [class*='rating']")?.getAttribute("data-rating") ||
                                r.querySelectorAll("[class*='star--on'], [class*='filled']").length || "").toString();
                const title  = (r.querySelector("[class*='review-title'], .stamped-review-header-title")?.innerText || "").trim();
                const body   = (r.querySelector("[class*='review-body'], .stamped-review-content-body")?.innerText || "").trim();
                const date   = (r.querySelector("[class*='date'], time")?.innerText || "").trim();
                if (body || title) reviews.push({author, rating, title, body, date});
            });

            // Judge.me
            if (!reviews.length) {
                document.querySelectorAll(".jdgm-rev, [class*='jdgm-review']").forEach(r => {
                    const author = (r.querySelector(".jdgm-rev__author")?.innerText || "").trim();
                    const rating = (r.querySelector("[data-score]")?.getAttribute("data-score") || "").trim();
                    const title  = (r.querySelector(".jdgm-rev__title")?.innerText || "").trim();
                    const body   = (r.querySelector(".jdgm-rev__body")?.innerText || "").trim();
                    const date   = (r.querySelector(".jdgm-rev__timestamp")?.getAttribute("data-content") || "").trim();
                    if (body || title) reviews.push({author, rating, title, body, date});
                });
            }

            // Okendo
            if (!reviews.length) {
                document.querySelectorAll(".okeReviews-review, [class*='oke-review']").forEach(r => {
                    const author = (r.querySelector("[class*='reviewer'], [class*='author']")?.innerText || "").trim();
                    const rating = (r.querySelectorAll("[class*='star'][class*='full'], [class*='filled']").length || "").toString();
                    const title  = (r.querySelector("[class*='review-title']")?.innerText || "").trim();
                    const body   = (r.querySelector("[class*='review-body'], [class*='review-text']")?.innerText || "").trim();
                    const date   = (r.querySelector("time, [class*='date']")?.innerText || "").trim();
                    if (body || title) reviews.push({author, rating, title, body, date});
                });
            }

            // Generic fallback
            if (!reviews.length) {
                document.querySelectorAll("[class*='review-item'], [class*='review_item'], [class*='ReviewItem']").forEach(r => {
                    const author = (r.querySelector("[class*='author'], [class*='name']")?.innerText || "Anonymous").trim();
                    const rating = r.querySelectorAll("[class*='star'][class*='fill'], [class*='active']").length.toString();
                    const body   = (r.querySelector("[class*='body'], [class*='content'], [class*='text'], p")?.innerText || "").trim();
                    const date   = (r.querySelector("time, [class*='date']")?.innerText || "").trim();
                    if (body) reviews.push({author, rating, title: "", body, date});
                });
            }

            return reviews;
        """) or []

        if not raw_reviews:
            break

        for r in raw_reviews:
            reviews.append({
                "product_url":   product_url,
                "product_name":  product_name,
                "brand":         "Paula's Choice",
                "author":        clean(r.get("author","") or "Anonymous"),
                "rating":        r.get("rating",""),
                "title":         clean(r.get("title","") or ""),
                "body":          clean(r.get("body","") or ""),
                "date":          clean(r.get("date","") or ""),
                "source":        "paulaschoice",
            })

        # ลอง next page reviews
        clicked_next = False
        try:
            next_btns = driver.find_elements(By.XPATH,
                "//*[@class and (contains(@class,'next') or contains(@class,'Next'))]"
                "[contains(translate(text(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'next') or @aria-label='Next']"
            )
            for btn in next_btns:
                if btn.is_displayed() and btn.is_enabled():
                    driver.execute_script("arguments[0].click();", btn)
                    time.sleep(1.5)
                    clicked_next = True
                    break
        except: pass

        if not clicked_next:
            break

    return reviews

# ================================================================
# SCRAPE PRODUCT DETAIL
# ================================================================

def scrape_product(driver, url, category):
    for attempt in range(3):
        try:
            close_extra_tabs(driver)
            driver.get(url)
            time.sleep(1.5)
            dismiss_popups(driver)

            WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.TAG_NAME, "h1")))
            driver.execute_script("window.scrollTo(0, 400);")
            time.sleep(1)

            data = driver.execute_script("""
                const get = sel => (document.querySelector(sel)?.innerText || "").trim();

                const name = get("h1") || get(".product__title") || get("[class*='product-title']");

                const price = (
                    get(".price__current .money") ||
                    get(".product__price .money") ||
                    get(".price .money") ||
                    get("[class*='price'] .money") ||
                    get(".money")
                ).replace(/[^\\d.]/g, "");

                // Rating จาก review widget
                const rating = (
                    get("[data-rating]") ||
                    get(".stamped-badge-starrating") ||
                    get(".jdgm-prev-badge__stars") ||
                    get("[class*='rating-value']") ||
                    document.querySelector("[data-rating]")?.getAttribute("data-rating") ||
                    ""
                ).replace(/[^\\d.]/g, "");

                const ratingCount = (
                    get(".stamped-badge-caption") ||
                    get(".jdgm-prev-badge__count") ||
                    get("[class*='review-count']") ||
                    ""
                ).replace(/[^\\d]/g, "");

                // Image
                let imgUrl = "";
                for (const sel of [
                    ".product__media img",
                    ".product-single__photo img",
                    ".product-featured-media",
                    ".featured-image img",
                    "[class*='ProductImage'] img",
                ]) {
                    const img = document.querySelector(sel);
                    if (img) {
                        imgUrl = img.getAttribute("data-src") ||
                                 (img.getAttribute("srcset")||"").split(" ")[0] ||
                                 img.src || "";
                        if (imgUrl && !imgUrl.startsWith("data:")) break;
                    }
                }
                if (imgUrl && imgUrl.startsWith("//")) imgUrl = "https:" + imgUrl;

                // Ingredients
                let ingredients = "";
                const allEls = Array.from(document.querySelectorAll("*"));
                for (const el of allEls) {
                    const txt = (el.innerText || "").trim();
                    if (/^ingredients[:\\s]/i.test(txt) && txt.length > 100) {
                        ingredients = txt.replace(/^ingredients[:\\s]*/i,"").trim();
                        break;
                    }
                }
                if (!ingredients) {
                    for (const el of document.querySelectorAll("p,div,li")) {
                        const txt = (el.innerText||"").trim();
                        if (txt.includes("Water") && txt.split(",").length > 5
                            && txt.length > 100 && txt.length < 5000) {
                            ingredients = txt; break;
                        }
                    }
                }

                return {name, price, rating, ratingCount, imgUrl, ingredients};
            """)

            name       = clean(data.get("name",""))
            price_raw  = clean(data.get("price",""))
            rating     = clean(data.get("rating",""))
            rating_cnt = clean(data.get("ratingCount",""))
            img_url    = clean(data.get("imgUrl",""))
            ingr_raw   = clean(data.get("ingredients",""))

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

            # ดึงรีวิว
            reviews = scrape_reviews(driver, url, name)

            product = {
                "product_url":      url,
                "name":             name,
                "brand":            "Paula's Choice",
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
                "source":           "paulaschoice",
            }
            return product, reviews

        except Exception as e:
            print(f"    ⚠️  Retry {attempt+1}: {e}")
            ensure_window(driver)
            time.sleep(2 ** attempt)
    return None, []

def _try_ingredients_tab(driver):
    try:
        for tab in driver.find_elements(By.CSS_SELECTOR, "summary,[role='tab'],button,details>*:first-child"):
            if "ingredient" in (tab.text or "").lower():
                driver.execute_script("arguments[0].click();", tab)
                time.sleep(1.5)
                break
        content = driver.execute_script("""
            for (const el of document.querySelectorAll(
                "details[open],details[open] *,[aria-expanded='true']+*,.tab-pane.active"
            )) {
                if (el.innerText && el.innerText.length > 50) return el.innerText.trim();
            }
            return "";
        """)
        return clean(content or "")
    except: return ""

# ================================================================
# SAVE
# ================================================================

def _save_csv(products, path):
    df = pd.DataFrame(products)
    for col in df.columns:
        df[col] = df[col].apply(safe_val)
    df.to_csv(path, index=False, encoding="utf-8-sig")
    print(f"  📄 Saved → {path.name}")

# ================================================================
# MAIN
# ================================================================

def run():
    print("=" * 60)
    print("  🌿  Paula's Choice TH Scraper  (+ Reviews)")
    print(f"  📁  {OUTPUT_DIR}")
    print("=" * 60)

    driver   = make_driver()
    products = []
    all_reviews = []

    try:
        print("\n🌐 Loading paulaschoice.th ...")
        driver.get(BASE)
        time.sleep(5)
        dismiss_popups(driver)
        time.sleep(1)
        print("  ✅ Ready\n")

        for cat_name, cat_url in PC_CATEGORIES.items():
            print(f"\n{'='*50}")
            print(f"📂  {cat_name.upper()}")
            print(f"{'='*50}")

            if not ensure_window(driver):
                print("  ❌ Window lost — stopping"); break

            links = get_product_links(driver, cat_url, cat_name)
            print(f"\n  📋 {len(links)} products to scrape")

            for i, link in enumerate(links):
                if not ensure_window(driver): break
                if any(p["product_url"] == link for p in products):
                    print(f"  [{i+1:3d}/{len(links)}] ⏭️  Duplicate")
                    continue

                print(f"  [{i+1:3d}/{len(links)}] ", end="", flush=True)
                product, reviews = scrape_product(driver, link, cat_name)

                if product:
                    products.append(product)
                    all_reviews.extend(reviews)
                    icon = "🖼️ " if product.get("image_local") else "📷 "
                    rev_txt = f"  💬{len(reviews)}" if reviews else ""
                    print(f"{icon}{product['name'][:50]}  [{product['skintype']}]{rev_txt}")
                else:
                    print("❌ FAILED")

                if len(products) % AUTOSAVE_EVERY == 0 and products:
                    _save_csv(products, OUTPUT_DIR / "autosave_pc.csv")
                    if all_reviews:
                        _save_csv(all_reviews, OUTPUT_DIR / "autosave_pc_reviews.csv")
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
    rev_ok = sum(1 for p in products if p.get("rating_count"))

    print(f"\n{'='*60}")
    print(f"✅  DONE")
    print(f"   Products : {len(products):,}")
    print(f"   Reviews  : {len(all_reviews):,}")
    print(f"   Images   : {img_ok:,} / {len(products):,}")
    print(f"   📄 Products CSV → {OUTPUT_CSV.name}")
    if all_reviews:
        print(f"   💬 Reviews CSV  → {REVIEWS_CSV.name}")
    print(f"\n   Category breakdown:")
    for cat, cnt in sorted(cat_c.items(), key=lambda x: -x[1]):
        print(f"     {cat:<20} {cnt:>4}")
    print(f"{'='*60}")

if __name__ == "__main__":
    run()