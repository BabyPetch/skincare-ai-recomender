"""
INCIDecoder Scraper — Standalone
pip install undetected-chromedriver selenium webdriver-manager openpyxl pandas requests pillow
python incidecoder_scraper.py
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
    print("⚠️  pip install undetected-chromedriver")

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# ================================================================
# CONFIG
# ================================================================

HEADLESS       = False
MAX_PAGES      = 5
IMG_THUMB_SIZE = (120, 120)
AUTOSAVE_EVERY = 30

OUTPUT_DIR = Path(r"C:\Users\User\Documents\GitHub\skincare-ai-recomender\backend\scraper\data_products")
IMG_DIR    = OUTPUT_DIR / "images"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
IMG_DIR.mkdir(parents=True, exist_ok=True)

timestamp   = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
OUTPUT_XLSX = OUTPUT_DIR / f"incidecoder_{timestamp}.xlsx"
OUTPUT_CSV  = OUTPUT_DIR / f"incidecoder_{timestamp}.csv"

INCI_CATEGORIES = {
    "moisturizer": "https://incidecoder.com/search?query=moisturizer&filters=face-moisturizer",
    "serum":       "https://incidecoder.com/search?query=serum&filters=face-serum",
    "sunscreen":   "https://incidecoder.com/search?query=sunscreen&filters=sunscreen",
    "toner":       "https://incidecoder.com/search?query=toner&filters=face-toner",
    "cleanser":    "https://incidecoder.com/search?query=cleanser&filters=face-cleanser",
    "eye_care":    "https://incidecoder.com/search?query=eye+cream&filters=eye-care",
    "mask":        "https://incidecoder.com/search?query=face+mask&filters=face-mask",
    "exfoliator":  "https://incidecoder.com/search?query=exfoliant&filters=exfoliant",
}

ACTIVE_RULES = {
    "retinol":          ["retinol"],
    "retinal":          ["retinal"],
    "aha":              ["glycolic acid","lactic acid","mandelic acid"],
    "bha":              ["salicylic acid"],
    "pha":              ["gluconolactone"],
    "vitamin_c":        ["ascorb","ascorbyl"],
    "niacinamide":      ["niacinamide"],
    "peptide":          ["peptide"],
    "ceramide":         ["ceramide"],
    "zinc_oxide":       ["zinc oxide"],
    "titanium_dioxide": ["titanium dioxide"],
}

FUNCTION_RULES = {
    "brightening":   ["ascorb","niacinamide","arbutin"],
    "anti_aging":    ["retinol","retinal","peptide"],
    "acne_control":  ["salicylic acid"],
    "calming":       ["centella","allantoin"],
    "barrier_repair":["ceramide"],
    "hydrating":     ["hyaluronic","glycerin"],
    "exfoliating":   ["glycolic","salicylic","lactic"],
}

# ================================================================
# +++ SKINTYPE RULES (เพิ่มใหม่) +++
# ================================================================

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
        "centella asiatica", "madecassoside", "madecassic acid",
        "asiaticoside", "allantoin", "bisabolol", "aloe barbadensis",
        "aloe vera", "panthenol", "oat", "avena sativa",
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

def clean(t): return " ".join(str(t).split()).strip()

def detect_tags(text, rules):
    t = text.lower()
    return sorted(tag for tag, kws in rules.items() if any(k in t for k in kws))

# +++ เพิ่มใหม่ +++
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
        c = any(k in t for k in ["avobenzone","octinoxate","octocrylene"])
        return "hybrid_sunscreen" if m and c else ("mineral_sunscreen" if m else "chemical_sunscreen")
    if "retinal"        in t: return "retinal_serum"
    if "retinol"        in t: return "retinol_serum"
    if "salicylic acid" in t: return "bha_exfoliator"
    if "glycolic acid"  in t: return "aha_exfoliator"
    if "lactic acid"    in t: return "aha_exfoliator"
    return cat

def close_extra_tabs(driver):
    try:
        handles = driver.window_handles
        if len(handles) > 1:
            main = handles[0]
            for h in handles[1:]:
                driver.switch_to.window(h)
                driver.close()
            driver.switch_to.window(main)
    except: pass

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
        except: pass
        return False

# ================================================================
# IMAGE DOWNLOAD
# ================================================================

def download_image(img_url: str) -> Path | None:
    if not img_url or img_url.startswith("data:"):
        return None
    try:
        img_hash  = hashlib.md5(img_url.encode()).hexdigest()[:12]
        save_path = IMG_DIR / f"{img_hash}.jpg"
        if save_path.exists():
            return save_path
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Referer":    "https://incidecoder.com/",
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
        if HEADLESS: opts.add_argument("--headless=new")
        opts.add_argument("--window-size=1440,900")
        opts.add_argument("--disable-blink-features=AutomationControlled")
        opts.add_experimental_option("excludeSwitches", ["enable-automation"])
        opts.add_experimental_option("useAutomationExtension", False)
        opts.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/122 Safari/537.36")
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=opts)
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument",
            {"source": "Object.defineProperty(navigator,'webdriver',{get:()=>undefined})"})
        return driver

# ================================================================
# GET PRODUCT LINKS
# ================================================================

def get_product_links(driver, search_url, category, max_pages) -> list:
    links = []
    page  = 1
    while True:
        if not ensure_window(driver): break
        close_extra_tabs(driver)
        url = search_url if page == 1 else f"{search_url}&page={page}"
        print(f"  📄 page {page} → {url[:75]}")
        try:
            driver.get(url)
            time.sleep(2)
            close_extra_tabs(driver)
            try:
                WebDriverWait(driver, 20).until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, ".search-results-item, .simpletextlistitem, a[href*='/products/']")
                ))
            except TimeoutException:
                print(f"  ⚠️  Timeout page {page}"); break
            time.sleep(1.5)
            close_extra_tabs(driver)
            found = driver.execute_script("""
                return [...new Set(
                    Array.from(document.querySelectorAll("a[href]"))
                        .map(a => a.href)
                        .filter(h => /incidecoder\\.com\\/products\\/[^\\/\\?#]+$/.test(h))
                )];
            """) or []
            if not found:
                print(f"  ⚠️  No links page {page}"); break
            new = [l for l in found if l not in links]
            links.extend(new)
            print(f"     +{len(new)} links  (total: {len(links)})")
            has_next = driver.execute_script("""
                return !!(document.querySelector("a[rel='next']") ||
                          document.querySelector(".pagination .next a") ||
                          document.querySelector(`a[href*='page=${arguments[0]+1}']`));
            """, page)
            if not has_next or (max_pages and page >= max_pages): break
            page += 1
            time.sleep(random.uniform(1.5, 3.0))
        except Exception as e:
            print(f"  ❌ {e}"); ensure_window(driver); break
    return links

# ================================================================
# SCRAPE PRODUCT DETAIL
# ================================================================

def scrape_product(driver, url, category):
    for attempt in range(3):
        try:
            close_extra_tabs(driver)
            driver.get(url)
            time.sleep(1)
            close_extra_tabs(driver)
            WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.TAG_NAME, "h1")))
            driver.execute_script("window.scrollTo(0, 400);")
            time.sleep(1)

            data = driver.execute_script("""
                const get = sel => (document.querySelector(sel)?.innerText || "").trim();
                const name  = get("h1");
                const brand = get(".product-brand-title a") || get(".brand-name a");
                const price = get(".product-price") || get(".price-value");
                const rating = (get(".rating-value") || get("[itemprop='ratingValue']")).replace(/[^\\d.]/g,"");
                const ratingCount = (get("[itemprop='reviewCount']") || get(".rating-count")).replace(/[^\\d]/g,"");

                let imgUrl = "";
                for (const sel of [
                    ".product-image-main img",".product-image img",
                    "[class*='product-image'] img","img[class*='product']",
                    ".hero-image img","img[itemprop='image']"
                ]) {
                    const img = document.querySelector(sel);
                    if (img) {
                        imgUrl = img.getAttribute("data-src") || img.src || "";
                        if (imgUrl && !imgUrl.startsWith("data:") && imgUrl.length > 10) break;
                    }
                }
                if (!imgUrl) {
                    let maxArea = 0;
                    document.querySelectorAll("img").forEach(img => {
                        const src = img.getAttribute("data-src") || img.src || "";
                        const area = (img.naturalWidth||img.width)*(img.naturalHeight||img.height);
                        if (area > maxArea && src && !src.startsWith("data:")
                            && !src.includes("icon") && !src.includes("logo")) {
                            maxArea = area; imgUrl = src;
                        }
                    });
                }
                const ingrs = [...document.querySelectorAll(
                    "a.ingred-link,.ingredlist a,#ingredlist a,.ingredient-item"
                )].map(e => e.innerText.trim()).filter(Boolean);
                return {name,brand,price,rating,ratingCount,imgUrl,ingrs};
            """)

            name       = clean(data.get("name",""))
            brand      = clean(data.get("brand",""))
            price      = clean(data.get("price",""))
            rating     = clean(data.get("rating",""))
            rating_cnt = clean(data.get("ratingCount",""))
            img_url    = clean(data.get("imgUrl",""))
            ingr_list  = [clean(i) for i in (data.get("ingrs") or []) if i.strip()]
            ingr_raw   = clean(", ".join(ingr_list))
            img_local  = download_image(img_url)

            # +++ เพิ่มใหม่: คำนวณ skintype ตั้งแต่ scrape +++
            function_tags = ",".join(detect_tags(ingr_raw, FUNCTION_RULES))
            skintype      = detect_skintype(ingr_raw, function_tags)

            return {
                "product_url":      url,
                "name":             name,
                "brand":            brand,
                "major_category":   category,
                "subtype":          detect_subtype(name, ingr_raw, category),
                "price":            price,
                "rating":           rating,
                "rating_count":     rating_cnt,
                "active_tags":      ",".join(detect_tags(ingr_raw, ACTIVE_RULES)),
                "function_tags":    function_tags,
                "skintype":         skintype,       # +++ เพิ่มใหม่ +++
                "ingredients_raw":  ingr_raw,
                "ingredients_list": ",".join(ingr_list),
                "image_url":        img_url,
                "image_local":      str(img_local) if img_local else "",
            }
        except Exception as e:
            print(f"    ⚠️  Retry {attempt+1}: {e}")
            ensure_window(driver)
            time.sleep(2 ** attempt)
    return None

# ================================================================
# EXCEL BUILDER
# ================================================================

NAVY="1B3A5C"; TEAL="2D7D9A"; WHITE="FFFFFF"; LIGHT="EBF4F8"
CAT_COLORS={
    "moisturizer":("E3F2FD","BBDEFB"),"serum":("E8F5E9","C8E6C9"),
    "sunscreen":("FFF9C4","FFF3A0"),"toner":("E0F7FA","B2EBF2"),
    "cleanser":("FBE9E7","FFCCBC"),"eye_care":("FCE4EC","F8BBD0"),
    "mask":("F3E5F5","E1BEE7"),"exfoliator":("E8EAF6","C5CAE9"),
}

def _b():
    s = Side(style="thin", color="C8D8E4")
    return Border(left=s,right=s,top=s,bottom=s)

def _h(ws,r,c,v,bg=NAVY,fg=WHITE,sz=10):
    cell=ws.cell(row=r,column=c,value=v)
    cell.font=Font(name="Arial",bold=True,size=sz,color=fg)
    cell.fill=PatternFill("solid",fgColor=bg)
    cell.alignment=Alignment(horizontal="center",vertical="center",wrap_text=True)
    cell.border=_b()

def _d(ws,r,c,v,bg=WHITE,bold=False,wrap=False,align="left",color="1A1A1A"):
    cell=ws.cell(row=r,column=c,value=v)
    cell.font=Font(name="Arial",size=10,bold=bold,color=color)
    cell.fill=PatternFill("solid",fgColor=bg)
    cell.alignment=Alignment(horizontal=align,vertical="center",wrap_text=wrap)
    cell.border=_b()

# +++ เพิ่ม Skintype column ในตาราง +++
COLUMNS=[
    ("Image",16,"_image"), ("#",5,"_num"), ("Brand",18,"brand"),
    ("Product Name",40,"name"), ("Category",14,"major_category"),
    ("Subtype",22,"subtype"), ("Skin Type",18,"skintype"),
    ("Price",10,"price"), ("Rating",10,"rating"),
    ("Reviews",10,"rating_count"), ("Active Tags",30,"active_tags"),
    ("Functions",28,"function_tags"), ("URL",42,"product_url"),
    ("Image URL",42,"image_url"), ("Ingredients",90,"ingredients_raw"),
]

def build_excel(products, filepath):
    print(f"\n📊 Building Excel …")
    wb = Workbook()

    # Sheet 1: Products
    ws = wb.active; ws.title="Products"
    ws.sheet_view.showGridLines=False; ws.freeze_panes="B3"

    ws.merge_cells(f"A1:{get_column_letter(len(COLUMNS))}1")
    t=ws["A1"]
    t.value=f"✨  INCIDecoder Skincare Database  —  {len(products):,} products  ✨"
    t.font=Font(name="Arial",bold=True,size=13,color=WHITE)
    t.fill=PatternFill("solid",fgColor=NAVY)
    t.alignment=Alignment(horizontal="center",vertical="center")
    ws.row_dimensions[1].height=32

    for ci,(label,width,_) in enumerate(COLUMNS,1):
        _h(ws,2,ci,label,bg=TEAL)
        ws.column_dimensions[get_column_letter(ci)].width=width
    ws.row_dimensions[2].height=28

    for ri,p in enumerate(products,1):
        er=ri+2
        cat=p.get("major_category","unknown")
        c1,c2=CAT_COLORS.get(cat,(WHITE,LIGHT))
        bg=c2 if ri%2==0 else c1
        ws.row_dimensions[er].height=90

        for ci,(_,_,key) in enumerate(COLUMNS,1):
            cl=get_column_letter(ci)
            if key=="_image":
                img_local=p.get("image_local","")
                if img_local and Path(img_local).exists():
                    try:
                        xl_img=XLImage(img_local)
                        xl_img.width=88; xl_img.height=88
                        ws.add_image(xl_img,f"{cl}{er}")
                    except: _d(ws,er,ci,"📷",bg=bg,align="center")
                else: _d(ws,er,ci,"",bg=bg)
            elif key=="_num":
                _d(ws,er,ci,ri,bg=bg,align="center",bold=True)
            elif key=="major_category":
                _d(ws,er,ci,str(p.get(key,"")).upper(),bg=bg,align="center",bold=True,color=TEAL)
            elif key=="skintype":
                _d(ws,er,ci,p.get(key,"all"),bg=bg,align="center",bold=True,color="1B3A5C")
            elif key in("product_url","image_url"):
                val=p.get(key,"")
                cell=ws.cell(row=er,column=ci,value=val)
                if val: cell.hyperlink=val
                cell.font=Font(name="Arial",size=9,color="0563C1",underline="single")
                cell.fill=PatternFill("solid",fgColor=bg)
                cell.alignment=Alignment(horizontal="left",vertical="center")
                cell.border=_b()
            elif key=="ingredients_raw":
                _d(ws,er,ci,p.get(key,""),bg=bg,wrap=True)
            else:
                _d(ws,er,ci,p.get(key,""),bg=bg)

    ws.auto_filter.ref=f"A2:{get_column_letter(len(COLUMNS))}{len(products)+2}"

    # Sheet 2: Summary
    ws2=wb.create_sheet("Summary"); ws2.sheet_view.showGridLines=False
    ws2.merge_cells("A1:D1"); t2=ws2["A1"]
    t2.value="Summary Statistics"
    t2.font=Font(name="Arial",bold=True,size=13,color=WHITE)
    t2.fill=PatternFill("solid",fgColor=NAVY)
    t2.alignment=Alignment(horizontal="center",vertical="center")
    ws2.row_dimensions[1].height=30
    for ci,lbl in enumerate(["Category","Count","Active Tag","Count"],1):
        _h(ws2,2,ci,lbl,bg=TEAL)
        ws2.column_dimensions[get_column_letter(ci)].width=22
    ws2.row_dimensions[2].height=24

    cat_c=Counter(p.get("major_category","?") for p in products)
    tag_c=Counter(t.strip() for p in products for t in p.get("active_tags","").split(",") if t.strip())
    cats=sorted(cat_c.items(),key=lambda x:-x[1])
    tags=sorted(tag_c.items(),key=lambda x:-x[1])
    for i in range(max(len(cats),len(tags))):
        r=i+3; bg=LIGHT if i%2==0 else WHITE
        if i<len(cats): _d(ws2,r,1,cats[i][0],bg=bg); _d(ws2,r,2,cats[i][1],bg=bg,align="center",bold=True)
        if i<len(tags): _d(ws2,r,3,tags[i][0],bg=bg); _d(ws2,r,4,tags[i][1],bg=bg,align="center",bold=True)
        ws2.row_dimensions[r].height=20
    tr=max(len(cats),len(tags))+3
    _h(ws2,tr,1,"TOTAL",bg=NAVY); _h(ws2,tr,2,len(products),bg=NAVY)

    # +++ Sheet 3: Skintype Summary (เพิ่มใหม่) +++
    ws_skin=wb.create_sheet("Skintype Summary"); ws_skin.sheet_view.showGridLines=False
    ws_skin.merge_cells("A1:B1"); t_skin=ws_skin["A1"]
    t_skin.value="Skintype Distribution"
    t_skin.font=Font(name="Arial",bold=True,size=13,color=WHITE)
    t_skin.fill=PatternFill("solid",fgColor=NAVY)
    t_skin.alignment=Alignment(horizontal="center",vertical="center")
    ws_skin.row_dimensions[1].height=30
    for ci,lbl in enumerate(["Skin Type","Count"],1):
        _h(ws_skin,2,ci,lbl,bg=TEAL)
        ws_skin.column_dimensions[get_column_letter(ci)].width=22
    skin_c=Counter(
        s.strip()
        for p in products
        for s in p.get("skintype","all").split(",")
        if s.strip()
    )
    for i,(skin,cnt) in enumerate(sorted(skin_c.items(),key=lambda x:-x[1])):
        r=i+3; bg=LIGHT if i%2==0 else WHITE
        _d(ws_skin,r,1,skin,bg=bg,bold=True)
        _d(ws_skin,r,2,cnt,bg=bg,align="center",bold=True)
        ws_skin.row_dimensions[r].height=20

    # Sheet 4: Ingredient Index
    ws3=wb.create_sheet("Ingredient Index"); ws3.sheet_view.showGridLines=False
    ws3.merge_cells("A1:C1"); t3=ws3["A1"]
    t3.value="Ingredient Frequency Index  (Top 200)"
    t3.font=Font(name="Arial",bold=True,size=13,color=WHITE)
    t3.fill=PatternFill("solid",fgColor=NAVY)
    t3.alignment=Alignment(horizontal="center",vertical="center")
    ws3.row_dimensions[1].height=30
    ws3.column_dimensions["A"].width=44
    ws3.column_dimensions["B"].width=13
    ws3.column_dimensions["C"].width=14
    for ci,lbl in enumerate(["Ingredient","# Products","% Coverage"],1):
        _h(ws3,2,ci,lbl,bg=TEAL)
    ws3.row_dimensions[2].height=24

    all_ingr=Counter()
    for p in products:
        for ingr in p.get("ingredients_list","").split(","):
            ingr=ingr.strip()
            if ingr: all_ingr[ingr]+=1
    total=max(len(products),1)
    for i,(ingr,cnt) in enumerate(all_ingr.most_common(200)):
        r=i+3; bg=LIGHT if i%2==0 else WHITE
        _d(ws3,r,1,ingr,bg=bg)
        _d(ws3,r,2,cnt,bg=bg,align="center",bold=True)
        _d(ws3,r,3,f"{cnt/total*100:.1f}%",bg=bg,align="center")
        ws3.row_dimensions[r].height=18
    ws3.auto_filter.ref=f"A2:C{min(200,len(all_ingr))+2}"

    wb.save(filepath)
    print(f"✅ Excel saved → {filepath}")

# ================================================================
# MAIN
# ================================================================

def run():
    print("="*60)
    print("  🔬  INCIDecoder Scraper  —  Standalone")
    print(f"  📁  {OUTPUT_DIR}")
    print("="*60)

    driver=make_driver(); products=[]

    try:
        print("\n🌐 Loading INCIDecoder …")
        driver.get("https://incidecoder.com")
        time.sleep(random.uniform(3,5))
        close_extra_tabs(driver)
        print("  ✅ Ready\n")

        for cat, search_url in INCI_CATEGORIES.items():
            print(f"\n{'='*50}")
            print(f"📂  {cat.upper()}")
            print(f"{'='*50}")

            if not ensure_window(driver):
                print("  ❌ Window lost — stopping"); break

            links=get_product_links(driver, search_url, cat, MAX_PAGES)
            print(f"\n  📋 {len(links)} products to scrape")

            for i, link in enumerate(links):
                if not ensure_window(driver):
                    print("  ❌ Window lost"); break

                print(f"  [{i+1:3d}/{len(links)}] ", end="", flush=True)
                p=scrape_product(driver, link, cat)

                if p:
                    products.append(p)
                    icon="🖼️ " if p.get("image_local") else "📷 "
                    print(f"{icon}{p['brand']} — {p['name'][:45]}  [{p['skintype']}]")
                else:
                    print(f"❌ FAILED")

                if len(products) % AUTOSAVE_EVERY == 0 and products:
                    pd.DataFrame(products).to_csv(
                        OUTPUT_DIR/"autosave_inci.csv", index=False, encoding="utf-8-sig")
                    print(f"  💾 Autosaved {len(products)} products")

                time.sleep(random.uniform(0.8,1.8))

    finally:
        try: driver.quit()
        except: pass

    if not products:
        print("\n❌ No data scraped"); return

    print(f"\n{'='*60}")
    print(f"💾 Saving {len(products):,} products …")
    df=pd.DataFrame(products)
    df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8-sig")
    print(f"  📄 CSV  → {OUTPUT_CSV}")
    build_excel(products, OUTPUT_XLSX)
    img_ok=sum(1 for p in products if p.get("image_local"))
    print(f"\n{'='*60}")
    print(f"✅  DONE")
    print(f"   Products  : {len(products):,}")
    print(f"   Images    : {img_ok:,} / {len(products):,}")
    print(f"   📊 Excel  → {OUTPUT_XLSX}")
    print(f"   📄 CSV    → {OUTPUT_CSV}")
    print(f"   🖼️  Images → {IMG_DIR}")
    print(f"{'='*60}")

if __name__ == "__main__":
    run()