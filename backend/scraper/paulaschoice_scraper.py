"""
Paula's Choice Scraper
======================
Scrapes products from paulaschoice.com
Output CSV มี format เดียวกับ incidecoder CSV เพื่อ import เข้า DB ได้เลย

pip install undetected-chromedriver selenium webdriver-manager pandas openpyxl pillow requests
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
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# ================================================================
# CONFIG
# ================================================================

HEADLESS       = False
MAX_PAGES      = 20         # หน้าสูงสุดต่อ category (None = ทั้งหมด)
IMG_THUMB_SIZE = (120, 120)
AUTOSAVE_EVERY = 30
DELAY_MIN      = 1.0
DELAY_MAX      = 2.5

OUTPUT_DIR = Path(r"C:\Users\User\Documents\GitHub\skincare-ai-recomender\backend\scraper\data_products")
IMG_DIR    = OUTPUT_DIR / "images"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
IMG_DIR.mkdir(parents=True, exist_ok=True)

timestamp  = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
OUTPUT_CSV = OUTPUT_DIR / f"paulaschoice_{timestamp}.csv"

# Paula's Choice category URLs
PC_CATEGORIES = {
    "moisturizer": "https://www.paulaschoice.com/skin-care/moisturizers",
    "serum":       "https://www.paulaschoice.com/skin-care/serums-boosters",
    "sunscreen":   "https://www.paulaschoice.com/skin-care/sunscreens",
    "cleanser":    "https://www.paulaschoice.com/skin-care/cleansers",
    "toner":       "https://www.paulaschoice.com/skin-care/toners",
    "eye_care":    "https://www.paulaschoice.com/skin-care/eye-creams",
    "exfoliator":  "https://www.paulaschoice.com/skin-care/exfoliants",
    "mask":        "https://www.paulaschoice.com/skin-care/masks",
    "treatment":   "https://www.paulaschoice.com/skin-care/treatments",
}

# ================================================================
# TAG RULES (เหมือน INCIDecoder)
# ================================================================

ACTIVE_RULES = {
    "retinol":          ["retinol"],
    "retinal":          ["retinal"],
    "aha":              ["glycolic acid", "lactic acid", "mandelic acid"],
    "bha":              ["salicylic acid"],
    "pha":              ["gluconolactone"],
    "vitamin_c":        ["ascorb", "ascorbyl"],
    "niacinamide":      ["niacinamide"],
    "peptide":          ["peptide"],
    "ceramide":         ["ceramide"],
    "zinc_oxide":       ["zinc oxide"],
    "titanium_dioxide": ["titanium dioxide"],
}

FUNCTION_RULES = {
    "brightening":    ["ascorb", "niacinamide", "arbutin", "kojic", "tranexamic",
                       "glutathione", "vitamin c", "licorice", "belides"],
    "anti_aging":     ["retinol", "retinal", "peptide", "bakuchiol", "ubiquinone",
                       "coenzyme q", "adenosine", "argireline", "matrixyl"],
    "acne_control":   ["salicylic acid", "benzoyl peroxide", "sulfur", "zinc",
                       "tea tree", "witch hazel"],
    "calming":        ["centella", "allantoin", "madecassoside", "asiaticoside",
                       "bisabolol", "aloe", "chamomile", "oat", "avena",
                       "panthenol", "licorice root", "dipotassium glycyrrhizate"],
    "barrier_repair": ["ceramide", "cholesterol", "fatty acid", "sphingolipid",
                       "phytosterol", "phospholipid"],
    "hydrating":      ["hyaluronic", "sodium hyaluronate", "glycerin", "glycerine",
                       "sorbitol", "urea", "sodium pca", "betaine",
                       "trehalose", "squalane", "sodium lactate"],
    "exfoliating":    ["glycolic acid", "lactic acid", "mandelic acid",
                       "salicylic acid", "gluconolactone", "citric acid"],
    "antioxidant":    ["tocopherol", "vitamin e", "resveratrol", "ferulic",
                       "ubiquinone", "green tea", "camellia", "ascorbyl"],
    "moisturizing":   ["petrolatum", "dimethicone", "shea butter", "jojoba",
                       "squalane", "caprylic", "triglyceride"],
}

SKINTYPE_RULES = {
    "oily": [
        "salicylic acid", "niacinamide", "zinc oxide", "kaolin", "bentonite",
        "clay", "witch hazel", "tea tree", "sulfur", "zinc pca",
    ],
    "dry": [
        "ceramide", "shea butter", "squalane", "hyaluronic acid",
        "sodium hyaluronate", "glycerin", "glycerine", "petrolatum",
        "lanolin", "urea", "cholesterol", "fatty acid",
    ],
    "sensitive": [
        "centella asiatica", "madecassoside", "allantoin", "bisabolol",
        "aloe barbadensis", "aloe vera", "panthenol", "oat", "avena sativa",
        "chamomile", "licorice root", "dipotassium glycyrrhizate",
    ],
    "combination": [
        "glycolic acid", "lactic acid", "mandelic acid",
        "azelaic acid", "retinol", "retinal",
    ],
}

FUNCTION_TAG_HINTS = {
    "acne_control":   "oily",
    "exfoliating":    "combination",
    "barrier_repair": "dry",
    "calming":        "sensitive",
    "hydrating":      "dry",
    "brightening":    "combination",
    "anti_aging":     "combination",
}

# ================================================================
# HELPERS
# ================================================================

def clean(t):
    return " ".join(str(t).split()).strip()

def detect_tags(text, rules):
    t = text.lower()
    return sorted(tag for tag, kws in rules.items() if any(k in t for k in kws))

def detect_skintype(ingredients: str, function_tags: str) -> str:
    ingr_lower = str(ingredients).lower()
    tags_lower = str(function_tags).lower()

    scores = {st: 0 for st in SKINTYPE_RULES}
    for skintype, keywords in SKINTYPE_RULES.items():
        for kw in keywords:
            if kw in ingr_lower:
                scores[skintype] += 1

    max_score = max(scores.values())
    if max_score > 0:
        winners = [st for st, sc in scores.items() if sc == max_score]
        return ",".join(winners)

    for tag, skintype in FUNCTION_TAG_HINTS.items():
        if tag in tags_lower:
            return skintype

    return "all"

def detect_subtype(name, ingr, cat):
    t = (name + " " + ingr).lower()
    if cat == "sunscreen":
        m = "zinc oxide" in t or "titanium dioxide" in t
        c = any(k in t for k in ["avobenzone", "octinoxate", "octocrylene"])
        return "hybrid_sunscreen" if m and c else ("mineral_sunscreen" if m else "chemical_sunscreen")
    if "retinal"        in t: return "retinal_serum"
    if "retinol"        in t: return "retinol_serum"
    if "salicylic acid" in t: return "bha_exfoliator"
    if "glycolic acid"  in t: return "aha_exfoliator"
    if "lactic acid"    in t: return "aha_exfoliator"
    return cat

def safe_val(val):
    """แปลง nan/inf → None"""
    if val is None:
        return None
    if isinstance(val, float) and (math.isnan(val) or math.isinf(val)):
        return None
    return val

# ================================================================
# IMAGE DOWNLOAD
# ================================================================

def download_image(img_url: str) -> Path | None:
    if not img_url or img_url.startswith("data:"):
        return None
    try:
        img_hash  = hashlib.md5(img_url.encode()).hexdigest()[:12]
        save_path = IMG_DIR / f"pc_{img_hash}.jpg"
        if save_path.exists():
            return save_path
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Referer":    "https://www.paulaschoice.com/",
        }
        resp = req_lib.get(img_url, headers=headers, timeout=10)
        if resp.status_code != 200:
            return None
        img = PILImage.open(BytesIO(resp.content)).convert("RGB")
        img.thumbnail(IMG_THUMB_SIZE, PILImage.LANCZOS)
        img.save(save_path, "JPEG", quality=85)
        return save_path
    except:
        return None

# ================================================================
# DRIVER
# ================================================================

def make_driver():
    if USE_UC:
        opts = uc.ChromeOptions()
        if HEADLESS:
            opts.add_argument("--headless=new")
        opts.add_argument("--window-size=1440,900")
        opts.add_argument("--lang=en-US")
        opts.add_argument("--no-sandbox")
        opts.add_argument("--disable-dev-shm-usage")
        return uc.Chrome(options=opts, version_main=None)
    else:
        opts = Options()
        if HEADLESS:
            opts.add_argument("--headless=new")
        opts.add_argument("--window-size=1440,900")
        opts.add_argument("--disable-blink-features=AutomationControlled")
        opts.add_experimental_option("excludeSwitches", ["enable-automation"])
        opts.add_experimental_option("useAutomationExtension", False)
        opts.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/122 Safari/537.36")
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=opts)
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument",
            {"source": "Object.defineProperty(navigator,'webdriver',{get:()=>undefined})"})
        return driver

def close_extra_tabs(driver):
    try:
        handles = driver.window_handles
        if len(handles) > 1:
            main = handles[0]
            for h in handles[1:]:
                driver.switch_to.window(h)
                driver.close()
            driver.switch_to.window(main)
    except:
        pass

def ensure_window(driver):
    try:
        _ = driver.current_url
        return True
    except:
        try:
            h = driver.window_handles
            if h:
                driver.switch_to.window(h[0])
                return True
        except:
            pass
        return False

# ================================================================
# GET PRODUCT LINKS
# ================================================================

def get_product_links(driver, category_url: str, category: str, max_pages: int) -> list:
    """ดึง links สินค้าทั้งหมดจาก category page"""
    links = []
    page  = 1

    while True:
        if not ensure_window(driver):
            break
        close_extra_tabs(driver)

        # Paula's Choice ใช้ ?start=N สำหรับ pagination
        url = category_url if page == 1 else f"{category_url}?start={(page-1)*24}"
        print(f"  📄 page {page} → {url[:80]}")

        try:
            driver.get(url)
            time.sleep(2.5)
            close_extra_tabs(driver)

            # รอให้ product grid โหลด
            try:
                WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, ".product-tile, .product-grid-tile, [class*='product-tile'], a[href*='/skin-care/']")
                    )
                )
            except TimeoutException:
                print(f"  ⚠️  Timeout page {page}")
                break

            time.sleep(1.5)

            # ดึง product links
            found = driver.execute_script("""
                return [...new Set(
                    Array.from(document.querySelectorAll("a[href]"))
                        .map(a => a.href)
                        .filter(h => /paulaschoice\\.com\\/[\\w-]+\\/[\\w-]+\\.html/.test(h)
                                  || /paulaschoice\\.com\\/skin-care\\/[^?#]+\\.html/.test(h))
                )];
            """) or []

            # กรองเฉพาะ product page (ไม่ใช่ category)
            product_links = [
                l for l in found
                if l not in links
                and not any(cat in l for cat in [
                    "/moisturizers", "/serums", "/sunscreens", "/cleansers",
                    "/toners", "/eye-creams", "/exfoliants", "/masks",
                    "/treatments", "/sets", "/kits", "/regimens",
                    "/skin-types", "/concerns", "/ingredients"
                ])
                and ".html" in l
            ]

            if not product_links:
                print(f"  ⚠️  No new product links on page {page}")
                break

            links.extend(product_links)
            print(f"     +{len(product_links)} links  (total: {len(links)})")

            # เช็คว่ามีหน้าถัดไปไหม
            has_next = driver.execute_script("""
                const btns = document.querySelectorAll(
                    '.pagination-next:not([disabled]), [aria-label="Next"], .show-more-btn, button[class*="more"]'
                );
                return btns.length > 0 && !btns[0].disabled;
            """)

            # เช็คว่ายังมีสินค้าใหม่ไหม (บางเว็บ load more แทน pagination)
            if not has_next:
                # ลอง load more button
                try:
                    more_btn = driver.find_element(By.CSS_SELECTOR,
                        "button[class*='more'], .show-more, [data-action='show-more']")
                    if more_btn.is_displayed():
                        driver.execute_script("arguments[0].click();", more_btn)
                        time.sleep(2)
                        page += 1
                        continue
                except:
                    pass
                break

            if max_pages and page >= max_pages:
                break

            page += 1
            time.sleep(random.uniform(DELAY_MIN, DELAY_MAX))

        except Exception as e:
            print(f"  ❌ {e}")
            ensure_window(driver)
            break

    return links

# ================================================================
# SCRAPE PRODUCT DETAIL
# ================================================================

def scrape_product(driver, url: str, category: str) -> dict | None:
    """ดึงข้อมูล product จาก detail page"""
    for attempt in range(3):
        try:
            close_extra_tabs(driver)
            driver.get(url)
            time.sleep(1.5)
            close_extra_tabs(driver)

            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.TAG_NAME, "h1"))
            )
            driver.execute_script("window.scrollTo(0, 600);")
            time.sleep(1)

            data = driver.execute_script("""
                const get = sel => (document.querySelector(sel)?.innerText || "").trim();

                // Name
                const name = get("h1") || get(".product-name") || get("[itemprop='name']");

                // Brand — Paula's Choice มีแค่ brand เดียว
                const brand = "Paula's Choice";

                // Price
                const price = (
                    get("[itemprop='price']") ||
                    get(".product-price .sales .value") ||
                    get(".price-sales") ||
                    get(".product-price")
                ).replace(/[^\\d.]/g, "");

                // Rating
                const rating = (
                    get("[itemprop='ratingValue']") ||
                    get(".bv-rating-stars-container .bv-rating") ||
                    get(".rating-value") ||
                    ""
                ).replace(/[^\\d.]/g, "");

                const ratingCount = (
                    get("[itemprop='reviewCount']") ||
                    get(".bv-rating-count") ||
                    get(".review-count") ||
                    ""
                ).replace(/[^\\d]/g, "");

                // Image
                let imgUrl = "";
                const imgSelectors = [
                    ".primary-image img",
                    ".product-image-container img",
                    "[class*='product-image'] img",
                    ".carousel-item.active img",
                    "img[itemprop='image']",
                    ".pdp-image img"
                ];
                for (const sel of imgSelectors) {
                    const img = document.querySelector(sel);
                    if (img) {
                        imgUrl = img.getAttribute("data-src") || img.src || "";
                        if (imgUrl && !imgUrl.startsWith("data:") && imgUrl.length > 10) break;
                    }
                }

                // Ingredients — Paula's Choice มักอยู่ใน tab หรือ accordion
                let ingredients = "";
                const ingSelectors = [
                    "[data-tab='ingredients'] .tab-content",
                    "#ingredients",
                    ".ingredients-content",
                    "[class*='ingredient']",
                    ".pdp-ingredients",
                    "[aria-label*='Ingredient'] + *",
                    ".ingredient-list"
                ];
                for (const sel of ingSelectors) {
                    const el = document.querySelector(sel);
                    if (el && el.innerText.length > 20) {
                        ingredients = el.innerText.trim();
                        break;
                    }
                }

                // ถ้าไม่พบลอง find by text content
                if (!ingredients) {
                    const allEls = document.querySelectorAll("p, div, section");
                    for (const el of allEls) {
                        const txt = el.innerText || "";
                        if (txt.includes("Water") && txt.includes(",") && txt.length > 100) {
                            if (!txt.includes("\\n\\n") || txt.split(",").length > 5) {
                                ingredients = txt.trim();
                                break;
                            }
                        }
                    }
                }

                return {name, brand, price, rating, ratingCount, imgUrl, ingredients};
            """)

            name       = clean(data.get("name", ""))
            brand      = "Paula's Choice"
            price_raw  = clean(data.get("price", ""))
            rating     = clean(data.get("rating", ""))
            rating_cnt = clean(data.get("ratingCount", ""))
            img_url    = clean(data.get("imgUrl", ""))
            ingr_raw   = clean(data.get("ingredients", ""))

            # ถ้า ingredients ยังว่าง ลองคลิก tab
            if not ingr_raw or len(ingr_raw) < 20:
                ingr_raw = _try_click_ingredients_tab(driver)

            # parse ingredients list
            ingr_list = [
                i.strip() for i in re.split(r",\s*", ingr_raw)
                if i.strip() and len(i.strip()) > 1
            ]
            ingr_clean = clean(", ".join(ingr_list))

            # แปลงราคา
            try:
                price = float(price_raw) if price_raw else None
            except:
                price = None

            # Tags
            function_tags = ",".join(detect_tags(ingr_clean, FUNCTION_RULES))
            active_tags   = ",".join(detect_tags(ingr_clean, ACTIVE_RULES))
            skintype      = detect_skintype(ingr_clean, function_tags)
            subtype       = detect_subtype(name, ingr_clean, category)

            # Download image
            img_local = download_image(img_url)

            return {
                "product_url":      url,
                "name":             name,
                "brand":            brand,
                "major_category":   category,
                "subtype":          subtype,
                "price":            price,
                "rating":           rating if rating else None,
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

        except Exception as e:
            print(f"    ⚠️  Retry {attempt+1}: {e}")
            ensure_window(driver)
            time.sleep(2 ** attempt)

    return None


def _try_click_ingredients_tab(driver) -> str:
    """ลองคลิก ingredients tab/accordion แล้วดึงข้อความ"""
    try:
        # หา tab หรือ accordion ที่มีคำว่า ingredients
        tabs = driver.find_elements(By.CSS_SELECTOR,
            "[role='tab'], button, .accordion-header, .tab-link, [data-toggle]")
        for tab in tabs:
            txt = (tab.text or tab.get_attribute("aria-label") or "").lower()
            if "ingredient" in txt:
                driver.execute_script("arguments[0].click();", tab)
                time.sleep(1.5)
                break

        # ดึงเนื้อหา
        content = driver.execute_script("""
            const els = document.querySelectorAll(
                ".tab-pane.active, .accordion-body, [aria-expanded='true'] + *, .ingredients-tab"
            );
            for (const el of els) {
                if (el.innerText && el.innerText.length > 50) return el.innerText.trim();
            }
            return "";
        """)
        return clean(content or "")
    except:
        return ""

# ================================================================
# MAIN
# ================================================================

def run():
    print("=" * 60)
    print("  🌿  Paula's Choice Scraper")
    print(f"  📁  {OUTPUT_DIR}")
    print("=" * 60)

    driver   = make_driver()
    products = []

    try:
        print("\n🌐 Loading paulaschoice.com ...")
        driver.get("https://www.paulaschoice.com")
        time.sleep(random.uniform(3, 5))

        # ปิด popup ถ้ามี
        for sel in [
            "button[aria-label='Close']",
            ".modal-close",
            "[data-dismiss='modal']",
            "#onetrust-accept-btn-handler",
            ".accept-cookies"
        ]:
            try:
                btn = driver.find_element(By.CSS_SELECTOR, sel)
                btn.click()
                time.sleep(0.5)
            except:
                pass

        print("  ✅ Ready\n")

        for cat_name, cat_url in PC_CATEGORIES.items():
            print(f"\n{'='*50}")
            print(f"📂  {cat_name.upper()}")
            print(f"{'='*50}")

            if not ensure_window(driver):
                print("  ❌ Window lost — stopping")
                break

            links = get_product_links(driver, cat_url, cat_name, MAX_PAGES)
            print(f"\n  📋 {len(links)} products to scrape")

            for i, link in enumerate(links):
                if not ensure_window(driver):
                    print("  ❌ Window lost")
                    break

                # เช็ค duplicate
                if any(p["product_url"] == link for p in products):
                    print(f"  [{i+1:3d}/{len(links)}] ⏭️  Duplicate — skip")
                    continue

                print(f"  [{i+1:3d}/{len(links)}] ", end="", flush=True)
                p = scrape_product(driver, link, cat_name)

                if p:
                    products.append(p)
                    icon = "🖼️ " if p.get("image_local") else "📷 "
                    print(f"{icon}{p['brand']} — {p['name'][:50]}  [{p['skintype']}]")
                else:
                    print(f"❌ FAILED")

                # Autosave
                if len(products) % AUTOSAVE_EVERY == 0 and products:
                    _save_csv(products, OUTPUT_DIR / "autosave_pc.csv")
                    print(f"  💾 Autosaved {len(products)} products")

                time.sleep(random.uniform(DELAY_MIN, DELAY_MAX))

    finally:
        try:
            driver.quit()
        except:
            pass

    if not products:
        print("\n❌ No data scraped")
        return

    print(f"\n{'='*60}")
    print(f"💾 Saving {len(products):,} products ...")
    _save_csv(products, OUTPUT_CSV)

    # Stats
    cat_c = Counter(p.get("major_category", "?") for p in products)
    img_ok = sum(1 for p in products if p.get("image_local"))
    print(f"\n{'='*60}")
    print(f"✅  DONE")
    print(f"   Products : {len(products):,}")
    print(f"   Images   : {img_ok:,} / {len(products):,}")
    print(f"   📄 CSV   → {OUTPUT_CSV}")
    print(f"\n   Category breakdown:")
    for cat, cnt in sorted(cat_c.items(), key=lambda x: -x[1]):
        print(f"     {cat:<20} {cnt:>4}")
    print(f"{'='*60}")
    print(f"\n👉 Import เข้า DB:")
    print(f"   แก้ CSV_PATH ใน db.py ให้ชี้ไฟล์นี้")
    print(f"   หรือรัน patch_brand.py / patch_function_tags.py ก่อน")


def _save_csv(products: list, path: Path):
    df = pd.DataFrame(products)
    # clean nan
    for col in df.columns:
        df[col] = df[col].apply(safe_val)
    df.to_csv(path, index=False, encoding="utf-8-sig")
    print(f"  📄 CSV saved → {path}")


if __name__ == "__main__":
    run()