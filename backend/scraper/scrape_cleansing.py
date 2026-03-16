"""
Scrape cleansing ~300 products แล้ว merge กับ CSV เดิม
python scrape_cleansing.py
"""
import time, random, datetime, hashlib
from io import BytesIO
from pathlib import Path

import requests as req_lib
import pandas as pd
from PIL import Image as PILImage

try:
    import undetected_chromedriver as uc
    USE_UC = True
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

OUTPUT_DIR = Path(r"C:\Users\Petch\Desktop\Projectskin\skincare-ai-recomender\backend\scraper\data_products")
IMG_DIR    = OUTPUT_DIR / "images"
IMG_DIR.mkdir(exist_ok=True)

MAIN_CSV   = OUTPUT_DIR / "incidecoder_20260314_130516.csv"
TARGET     = 300
MAX_PAGES  = 8

CLEANSING_QUERIES = [
    "https://incidecoder.com/search?query=cleansing+balm&filters=face-cleanser",
    "https://incidecoder.com/search?query=cleansing+oil&filters=face-cleanser",
    "https://incidecoder.com/search?query=micellar+water&filters=face-cleanser",
    "https://incidecoder.com/search?query=cleansing+milk&filters=face-cleanser",
]

ACTIVE_RULES = {
    "retinol":["retinol"],"retinal":["retinal"],
    "aha":["glycolic acid","lactic acid","mandelic acid"],
    "bha":["salicylic acid"],"pha":["gluconolactone"],
    "vitamin_c":["ascorb","ascorbyl"],"niacinamide":["niacinamide"],
    "peptide":["peptide"],"ceramide":["ceramide"],
    "zinc_oxide":["zinc oxide"],"titanium_dioxide":["titanium dioxide"],
}
FUNCTION_RULES = {
    "brightening":    ["ascorb","niacinamide","arbutin","kojic","tranexamic"],
    "anti_aging":     ["retinol","retinal","peptide","bakuchiol","adenosine"],
    "acne_control":   ["salicylic acid","benzoyl peroxide","zinc"],
    "calming":        ["centella","allantoin","madecassoside","bisabolol","panthenol"],
    "barrier_repair": ["ceramide","cholesterol","fatty acid"],
    "hydrating":      ["hyaluronic","sodium hyaluronate","glycerin","squalane"],
    "exfoliating":    ["glycolic acid","lactic acid","salicylic acid"],
    "antioxidant":    ["tocopherol","resveratrol","ferulic","green tea"],
    "moisturizing":   ["petrolatum","dimethicone","shea butter","jojoba"],
}
SKINTYPE_RULES = {
    "oily":        ["salicylic acid","niacinamide","zinc oxide","kaolin","witch hazel"],
    "dry":         ["ceramide","shea butter","squalane","hyaluronic acid","glycerin","petrolatum"],
    "sensitive":   ["centella asiatica","madecassoside","allantoin","bisabolol","aloe","panthenol"],
    "combination": ["glycolic acid","lactic acid","retinol"],
}

def clean(t): return " ".join(str(t).split()).strip()
def detect_tags(text, rules):
    t = text.lower()
    return sorted(tag for tag, kws in rules.items() if any(k in t for k in kws))
def detect_skintype(ingr):
    ingr_lower = str(ingr).lower()
    scores = {st: sum(1 for kw in kws if kw in ingr_lower) for st, kws in SKINTYPE_RULES.items()}
    mx = max(scores.values())
    return ",".join(st for st, sc in scores.items() if sc == mx) if mx > 0 else "all"

def download_image(img_url):
    if not img_url or img_url.startswith("data:"): return None
    try:
        save_path = IMG_DIR / f"{hashlib.md5(img_url.encode()).hexdigest()[:12]}.jpg"
        if save_path.exists(): return save_path
        resp = req_lib.get(img_url, headers={"User-Agent":"Mozilla/5.0","Referer":"https://incidecoder.com/"}, timeout=15)
        if resp.status_code != 200: return None
        img = PILImage.open(BytesIO(resp.content)).convert("RGB")
        img.thumbnail((300,300), PILImage.LANCZOS)
        img.save(save_path, "JPEG", quality=90)
        return save_path
    except: return None

def make_driver():
    if USE_UC:
        opts = uc.ChromeOptions()
        opts.add_argument("--window-size=1440,900")
        return uc.Chrome(options=opts, version_main=None)
    else:
        opts = Options()
        opts.add_argument("--window-size=1440,900")
        opts.add_argument("--disable-blink-features=AutomationControlled")
        opts.add_experimental_option("excludeSwitches",["enable-automation"])
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=opts)
        return driver

def close_extra_tabs(driver):
    try:
        handles = driver.window_handles
        if len(handles) > 1:
            main = handles[0]
            for h in handles[1:]: driver.switch_to.window(h); driver.close()
            driver.switch_to.window(main)
    except: pass

def get_links(driver, search_url, existing_urls, max_pages):
    links = []; page = 1
    while page <= max_pages:
        if page == 1: url = search_url
        else:
            base = search_url.split("?")[0]
            params = search_url.split("?")[1] if "?" in search_url else ""
            url = f"{base}?{params}&activetab=products&ppage={page}"
        print(f"  📄 page {page}", end=" ... ", flush=True)
        try:
            driver.get(url); time.sleep(2); close_extra_tabs(driver)
            WebDriverWait(driver,15).until(EC.presence_of_element_located(
                (By.CSS_SELECTOR,"a[href*='/products/']")))
            time.sleep(1)
            found = driver.execute_script("""
                return [...new Set(Array.from(document.querySelectorAll("a[href]"))
                    .map(a=>a.href)
                    .filter(h=>/incidecoder\\.com\\/products\\/[^\\/\\?#]+$/.test(h)))];
            """) or []
            new = [l for l in found if l not in links and l not in existing_urls]
            links.extend(new)
            print(f"+{len(new)} (total={len(links)})")
            has_next = driver.execute_script(f"""
                return !!(document.querySelector("a[rel='next']") ||
                          document.querySelector(`a[href*='ppage={page+1}']`));
            """)
            if not has_next: break
            page += 1; time.sleep(random.uniform(1.5,2.5))
        except Exception as e:
            print(f"❌ {e}"); break
    return links

def scrape_product(driver, url):
    for attempt in range(3):
        try:
            close_extra_tabs(driver); driver.get(url); time.sleep(1)
            WebDriverWait(driver,15).until(EC.presence_of_element_located((By.TAG_NAME,"h1")))
            driver.execute_script("window.scrollTo(0,600);"); time.sleep(1.5)
            data = driver.execute_script("""
                const get = sel => (document.querySelector(sel)?.innerText||"").trim();
                const name  = get("h1 #product-title")||get("h1");
                const brand = get("#product-brand-title a")||get(".brand-name a");
                const price = get(".product-price")||"";
                let imgUrl = "";
                const pic = document.querySelector("#product-main-image picture");
                if (pic) {
                    const imgEl = pic.querySelector("img");
                    if (imgEl) imgUrl = imgEl.src||imgEl.getAttribute("data-src")||"";
                }
                const ingrs = [...document.querySelectorAll(
                    "#showmore-section-ingredlist-short a.ingred-link,a.ingred-link.black"
                )].map(e=>e.innerText.trim()).filter(Boolean);
                const keySection = document.querySelector(
                    "#ingredlist-highlights-section .ingredlist-by-function-block");
                const keyIngrs = keySection
                    ? [...keySection.querySelectorAll("a.ingred-link")].map(e=>e.innerText.trim()).filter(Boolean)
                    : [];
                const keyFuncs = [];
                if (keySection) {
                    keySection.querySelectorAll("div").forEach(div => {
                        const f = div.querySelector("a.func-link");
                        const i = [...div.querySelectorAll("a.ingred-link")].map(e=>e.innerText.trim());
                        if (f && i.length) keyFuncs.push(f.innerText.trim()+": "+i.join(", "));
                    });
                }
                const hashtags = [...document.querySelectorAll(".hashtag")].map(e=>e.innerText.trim()).filter(Boolean);
                return {name,brand,price,imgUrl,ingrs,keyIngrs,keyFuncs,hashtags};
            """)
            ingr_list = [clean(i) for i in (data.get("ingrs") or []) if i.strip()]
            ingr_raw  = ", ".join(ingr_list)
            key_ingrs = [clean(i) for i in (data.get("keyIngrs") or []) if i.strip()]
            key_funcs = [clean(i) for i in (data.get("keyFuncs") or []) if i.strip()]
            hashtags  = [clean(h) for h in (data.get("hashtags") or []) if h.strip()]
            img_url   = clean(data.get("imgUrl",""))
            img_local = download_image(img_url)
            return {
                "product_url":      url,
                "name":             clean(data.get("name","")),
                "brand":            clean(data.get("brand","")),
                "major_category":   "cleansing",
                "subtype":          "cleansing",
                "price":            clean(data.get("price","")),
                "rating":           "",
                "rating_count":     "",
                "active_tags":      ",".join(detect_tags(ingr_raw, ACTIVE_RULES)),
                "function_tags":    ",".join(detect_tags(ingr_raw, FUNCTION_RULES)),
                "ingredients_raw":  ingr_raw,
                "ingredients_list": ",".join(ingr_list),
                "image_url":        img_url,
                "image_local":      Path(img_local).name if img_local else "",
                "skintype":         detect_skintype(ingr_raw),
                "free_from":        ", ".join(hashtags) if hashtags else "NA",
                "key_ingredients":  ", ".join(key_ingrs),
                "key_functions":    " | ".join(key_funcs),
            }
        except Exception as e:
            print(f"    ⚠️  Retry {attempt+1}: {e}")
            time.sleep(2**attempt)
    return None

# ================================================================
# MAIN
# ================================================================
print("📂 Loading existing CSV …")
df_old = pd.read_csv(MAIN_CSV)
existing_urls = set(df_old["product_url"].tolist())
print(f"   {len(df_old):,} products already in CSV")

driver = make_driver()
products = []

try:
    driver.get("https://incidecoder.com")
    time.sleep(3)

    for search_url in CLEANSING_QUERIES:
        if len(products) >= TARGET: break
        q = search_url.split("query=")[1].split("&")[0]
        print(f"\n🔍 {q}")
        links = get_links(driver, search_url, existing_urls, MAX_PAGES)
        print(f"  📋 {len(links)} new links")

        for i, link in enumerate(links):
            if len(products) >= TARGET: break
            print(f"  [{i+1:3d}/{len(links)}] ", end="", flush=True)
            p = scrape_product(driver, link)
            if p:
                products.append(p)
                print(f"{'🖼️' if p['image_local'] else '  '} {p['brand'][:15]} — {p['name'][:38]}")
            else:
                print("❌")
            time.sleep(random.uniform(0.8,1.8))

finally:
    try: driver.quit()
    except: pass

if not products:
    print("❌ No products scraped"); exit()

print(f"\n✅ {len(products)} cleansing products scraped")

# Merge กับ CSV เดิม
df_new  = pd.DataFrame(products)
df_all  = pd.concat([df_old, df_new], ignore_index=True).drop_duplicates(subset="product_url")
df_all.to_csv(MAIN_CSV, index=False, encoding="utf-8-sig")
print(f"💾 Merged → {MAIN_CSV.name}  ({len(df_all):,} total products)")