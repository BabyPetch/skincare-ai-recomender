"""
INCIDecoder Scraper — 5000 products
เปลี่ยนจากเดิม 2 จุด:
  1. INCI_CATEGORIES เพิ่มจาก 8 → 20 categories
  2. MAX_PAGES 5 → 15
  
วาง file นี้แทน incidecoder_scraper.py เดิมได้เลย
"""

import time, random, datetime, re, hashlib
from io import BytesIO
from pathlib import Path
from collections import Counter

import requests as req_lib
import pandas as pd
from PIL import Image as PILImage
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.drawing.image import Image as XLImage

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
from selenium.common.exceptions import TimeoutException

# ================================================================
# CONFIG  ← แก้ตรงนี้
# ================================================================

HEADLESS       = False
MAX_PAGES      = 15          # เดิม 5 → เพิ่มเป็น 15
IMG_THUMB_SIZE = (120, 120)
AUTOSAVE_EVERY = 50
TARGET         = 5000

OUTPUT_DIR = Path(r"C:\Users\Petch\Desktop\Projectskin\skincare-ai-recomender\backend\scraper\data_products")
IMG_DIR    = OUTPUT_DIR / "images"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
IMG_DIR.mkdir(parents=True, exist_ok=True)

timestamp   = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
OUTPUT_XLSX = OUTPUT_DIR / f"incidecoder_{timestamp}.xlsx"
OUTPUT_CSV  = OUTPUT_DIR / f"incidecoder_{timestamp}.csv"

# ← เพิ่มจาก 8 → 20 categories
INCI_CATEGORIES = {
    "moisturizer":   "https://incidecoder.com/search?query=moisturizer&filters=face-moisturizer",
    "serum":         "https://incidecoder.com/search?query=serum&filters=face-serum",
    "sunscreen":     "https://incidecoder.com/search?query=sunscreen&filters=sunscreen",
    "toner":         "https://incidecoder.com/search?query=toner&filters=face-toner",
    "cleanser":      "https://incidecoder.com/search?query=cleanser&filters=face-cleanser",
    "eye_care":      "https://incidecoder.com/search?query=eye+cream&filters=eye-care",
    "mask":          "https://incidecoder.com/search?query=face+mask&filters=face-mask",
    "exfoliator":    "https://incidecoder.com/search?query=exfoliant&filters=exfoliant",
    # ---- เพิ่มใหม่ ----
    "essence":       "https://incidecoder.com/search?query=essence&filters=face-essence",
    "ampoule":       "https://incidecoder.com/search?query=ampoule&filters=face-serum",
    "oil":           "https://incidecoder.com/search?query=face+oil&filters=face-oil",
    "mist":          "https://incidecoder.com/search?query=face+mist&filters=face-mist",
    "eye_serum":     "https://incidecoder.com/search?query=eye+serum&filters=eye-care",
    "lip_care":      "https://incidecoder.com/search?query=lip+balm&filters=lip-care",
    "body_lotion":   "https://incidecoder.com/search?query=body+lotion&filters=body-moisturizer",
    "body_wash":     "https://incidecoder.com/search?query=body+wash&filters=body-cleanser",
    "hair_care":     "https://incidecoder.com/search?query=shampoo&filters=shampoo",
    "retinol":       "https://incidecoder.com/search?query=retinol",
    "vitamin_c":     "https://incidecoder.com/search?query=vitamin+c+serum",
    "niacinamide":   "https://incidecoder.com/search?query=niacinamide",
}

ACTIVE_RULES = {
    "retinol":["retinol"], "retinal":["retinal"],
    "aha":["glycolic acid","lactic acid","mandelic acid"],
    "bha":["salicylic acid"], "pha":["gluconolactone"],
    "vitamin_c":["ascorb","ascorbyl"], "niacinamide":["niacinamide"],
    "peptide":["peptide"], "ceramide":["ceramide"],
    "zinc_oxide":["zinc oxide"], "titanium_dioxide":["titanium dioxide"],
}
FUNCTION_RULES = {
    "brightening":    ["ascorb","niacinamide","arbutin","kojic","tranexamic"],
    "anti_aging":     ["retinol","retinal","peptide","bakuchiol","adenosine"],
    "acne_control":   ["salicylic acid","benzoyl peroxide","zinc"],
    "calming":        ["centella","allantoin","madecassoside","bisabolol","panthenol"],
    "barrier_repair": ["ceramide","cholesterol","fatty acid","sphingolipid"],
    "hydrating":      ["hyaluronic","sodium hyaluronate","glycerin","sorbitol","squalane"],
    "exfoliating":    ["glycolic acid","lactic acid","salicylic acid","mandelic acid"],
    "antioxidant":    ["tocopherol","resveratrol","ferulic","green tea","ascorbyl"],
    "moisturizing":   ["petrolatum","dimethicone","shea butter","jojoba","argan"],
}
SKINTYPE_RULES = {
    "oily":        ["salicylic acid","niacinamide","zinc oxide","kaolin","bentonite","witch hazel"],
    "dry":         ["ceramide","shea butter","squalane","hyaluronic acid","sodium hyaluronate","glycerin","petrolatum","urea"],
    "sensitive":   ["centella asiatica","madecassoside","allantoin","bisabolol","aloe","panthenol","oat","chamomile"],
    "combination": ["glycolic acid","lactic acid","azelaic acid","retinol","retinal"],
}

# ================================================================
# HELPERS (เหมือนเดิมทุกอย่าง)
# ================================================================

def clean(t): return " ".join(str(t).split()).strip()

def detect_tags(text, rules):
    t = text.lower()
    return sorted(tag for tag, kws in rules.items() if any(k in t for k in kws))

def detect_subtype(name, ingr, cat):
    t = (name + " " + ingr).lower()
    if cat == "sunscreen":
        m = "zinc oxide" in t or "titanium dioxide" in t
        c = any(k in t for k in ["avobenzone","octinoxate","octocrylene"])
        return "hybrid_sunscreen" if m and c else ("mineral_sunscreen" if m else "chemical_sunscreen")
    if "retinal" in t: return "retinal_serum"
    if "retinol" in t: return "retinol_serum"
    if "salicylic acid" in t: return "bha_exfoliator"
    if "glycolic acid" in t: return "aha_exfoliator"
    if "lactic acid" in t: return "aha_exfoliator"
    return cat

def detect_skintype(ingr, ftags=""):
    ingr_lower = str(ingr).lower()
    scores = {st: sum(1 for kw in kws if kw in ingr_lower)
              for st, kws in SKINTYPE_RULES.items()}
    mx = max(scores.values())
    if mx > 0:
        return ",".join(st for st, sc in scores.items() if sc == mx)
    return "all"

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
    try:
        _ = driver.current_url; return True
    except:
        try:
            h = driver.window_handles
            if h: driver.switch_to.window(h[0]); return True
        except: pass
        return False

def download_image(img_url):
    if not img_url or img_url.startswith("data:"): return None
    try:
        img_hash  = hashlib.md5(img_url.encode()).hexdigest()[:12]
        save_path = IMG_DIR / f"{img_hash}.jpg"
        if save_path.exists(): return save_path
        headers = {"User-Agent":"Mozilla/5.0","Referer":"https://incidecoder.com/"}
        resp = req_lib.get(img_url, headers=headers, timeout=10)
        if resp.status_code != 200: return None
        img = PILImage.open(BytesIO(resp.content)).convert("RGB")
        img.thumbnail(IMG_THUMB_SIZE, PILImage.LANCZOS)
        img.save(save_path, "JPEG", quality=85)
        return save_path
    except: return None

def make_driver():
    if USE_UC:
        opts = uc.ChromeOptions()
        if HEADLESS: opts.add_argument("--headless=new")
        opts.add_argument("--window-size=1440,900")
        opts.add_argument("--lang=en-US")
        return uc.Chrome(options=opts, version_main=None)
    else:
        opts = Options()
        if HEADLESS: opts.add_argument("--headless=new")
        opts.add_argument("--window-size=1440,900")
        opts.add_argument("--disable-blink-features=AutomationControlled")
        opts.add_experimental_option("excludeSwitches",["enable-automation"])
        opts.add_experimental_option("useAutomationExtension",False)
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=opts)
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument",
            {"source":"Object.defineProperty(navigator,'webdriver',{get:()=>undefined})"})
        return driver

def get_product_links(driver, search_url, category, max_pages):
    links = []; page = 1
    while True:
        if not ensure_window(driver): break
        close_extra_tabs(driver)
        # ↓ แก้ตรงนี้
        if page == 1:
            url = search_url
        else:
            base   = search_url.split("?")[0]
            params = search_url.split("?")[1] if "?" in search_url else ""
            url    = f"{base}?{params}&activetab=products&ppage={page}"
        print(f"  📄 page {page} → {url[:70]}")
        try:
            driver.get(url); time.sleep(2); close_extra_tabs(driver)
            try:
                WebDriverWait(driver,20).until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR,".search-results-item,.simpletextlistitem,a[href*='/products/']")))
            except TimeoutException:
                print(f"  ⚠️  Timeout"); break
            time.sleep(1.5); close_extra_tabs(driver)
            found = driver.execute_script("""
                return [...new Set(
                    Array.from(document.querySelectorAll("a[href]"))
                        .map(a=>a.href)
                        .filter(h=>/incidecoder\\.com\\/products\\/[^\\/\\?#]+$/.test(h))
                )];
            """) or []
            if not found: print(f"  ⚠️  No links"); break
            new = [l for l in found if l not in links]
            links.extend(new)
            print(f"     +{len(new)} links  (total={len(links)})")
            # ↓ แก้ตรงนี้ด้วย
            has_next = driver.execute_script("""
                return !!(document.querySelector("a[rel='next']") ||
                          document.querySelector(".pagination .next a") ||
                          document.querySelector(`a[href*='ppage=${arguments[0]+1}']`));
            """, page)
            if not has_next or page >= max_pages: break
            page += 1; time.sleep(random.uniform(1.5,3.0))
        except Exception as e:
            print(f"  ❌ {e}"); ensure_window(driver); break
    return links

def scrape_product(driver, url, category):
    for attempt in range(3):
        try:
            close_extra_tabs(driver); driver.get(url)
            time.sleep(1); close_extra_tabs(driver)
            WebDriverWait(driver,15).until(EC.presence_of_element_located((By.TAG_NAME,"h1")))
            driver.execute_script("window.scrollTo(0,400);"); time.sleep(1)
            data = driver.execute_script("""
                const get=sel=>(document.querySelector(sel)?.innerText||"").trim();
                const name=get("h1");
                const brand=get(".product-brand-title a")||get(".brand-name a");
                const price=get(".product-price")||get(".price-value");
                const rating=(get(".rating-value")||get("[itemprop='ratingValue']")).replace(/[^\\d.]/g,"");
                const ratingCount=(get("[itemprop='reviewCount']")||get(".rating-count")).replace(/[^\\d]/g,"");
                let imgUrl="";
                for(const sel of[".product-image-main img",".product-image img","[class*='product-image'] img","img[itemprop='image']"]){
                    const img=document.querySelector(sel);
                    if(img){imgUrl=img.getAttribute("data-src")||img.src||"";
                    if(imgUrl&&!imgUrl.startsWith("data:")&&imgUrl.length>10)break;}
                }
                const ingrs=[...document.querySelectorAll("a.ingred-link,.ingredlist a,#ingredlist a,.ingredient-item")]
                    .map(e=>e.innerText.trim()).filter(Boolean);
                return{name,brand,price,rating,ratingCount,imgUrl,ingrs};
            """)
            name=clean(data.get("name",""))
            brand=clean(data.get("brand",""))
            ingr_list=[clean(i) for i in (data.get("ingrs") or []) if i.strip()]
            ingr_raw=clean(", ".join(ingr_list))
            img_url=clean(data.get("imgUrl",""))
            img_local=download_image(img_url)
            return {
                "product_url":      url,
                "name":             name,
                "brand":            brand,
                "major_category":   category,
                "subtype":          detect_subtype(name, ingr_raw, category),
                "price":            clean(data.get("price","")),
                "rating":           clean(data.get("rating","")),
                "rating_count":     clean(data.get("ratingCount","")),
                "active_tags":      ",".join(detect_tags(ingr_raw, ACTIVE_RULES)),
                "function_tags":    ",".join(detect_tags(ingr_raw, FUNCTION_RULES)),
                "ingredients_raw":  ingr_raw,
                "ingredients_list": ",".join(ingr_list),
                "image_url":        img_url,
                "image_local":      str(img_local) if img_local else "",
                "skintype":         detect_skintype(ingr_raw),
            }
        except Exception as e:
            print(f"    ⚠️  Retry {attempt+1}: {e}")
            ensure_window(driver); time.sleep(2**attempt)
    return None

# ================================================================
# MAIN
# ================================================================

def run():
    print("="*60)
    print(f"  🔬  INCIDecoder Scraper  —  Target: {TARGET:,} products")
    print(f"  📁  {OUTPUT_DIR}")
    print("="*60)

    driver = make_driver()
    products = []
    seen_urls = set()

    try:
        print("\n🌐 Loading INCIDecoder …")
        driver.get("https://incidecoder.com")
        time.sleep(random.uniform(3,5))
        close_extra_tabs(driver)
        print("  ✅ Ready\n")

        for cat, search_url in INCI_CATEGORIES.items():
            if len(products) >= TARGET:
                print(f"\n🎯 Target {TARGET:,} reached — stopping")
                break

            print(f"\n{'='*50}")
            print(f"📂  {cat.upper()}  (collected so far: {len(products):,})")
            print(f"{'='*50}")

            if not ensure_window(driver):
                print("  ❌ Window lost"); break

            links = get_product_links(driver, search_url, cat, MAX_PAGES)
            # กรอง duplicate ข้าม category
            links = [l for l in links if l not in seen_urls]
            seen_urls.update(links)
            print(f"\n  📋 {len(links)} new products to scrape")

            for i, link in enumerate(links):
                if len(products) >= TARGET:
                    break
                if not ensure_window(driver): break

                print(f"  [{i+1:3d}/{len(links)}] ", end="", flush=True)
                p = scrape_product(driver, link, cat)
                if p:
                    products.append(p)
                    icon = "🖼️ " if p.get("image_local") else "  "
                    print(f"{icon}{p['brand'][:15]} — {p['name'][:40]}")
                else:
                    print(f"❌ FAILED")

                if len(products) % AUTOSAVE_EVERY == 0 and products:
                    pd.DataFrame(products).to_csv(
                        OUTPUT_DIR/"autosave_inci.csv", index=False, encoding="utf-8-sig")
                    print(f"\n  💾 Autosaved {len(products):,} products\n")

                time.sleep(random.uniform(0.8, 1.8))

    finally:
        try: driver.quit()
        except: pass

    if not products:
        print("\n❌ No data"); return

    print(f"\n{'='*60}")
    print(f"💾 Saving {len(products):,} products …")
    df = pd.DataFrame(products).drop_duplicates(subset="product_url")
    df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8-sig")
    print(f"✅ {len(df):,} products → {OUTPUT_CSV.name}")
    print(f"   Images: {sum(1 for p in products if p.get('image_local')):,}")

if __name__ == "__main__":
    run()