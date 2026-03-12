"""
TEST: Reviews Pass 2 — แค่ 3 products
python test_reviews_pass2.py --csv data_products/sephora_th_20260312_160147.csv
"""
import time, argparse, sys
from pathlib import Path
import pandas as pd

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
from selenium.webdriver.common.keys import Keys

TEST_LIMIT  = 3
SCROLL_PAUSE = 1.0

def make_driver():
    if USE_UC:
        opts = uc.ChromeOptions()
        opts.add_argument("--window-size=1440,900")
        return uc.Chrome(options=opts, version_main=None)
    else:
        opts = Options()
        opts.add_argument("--window-size=1440,900")
        opts.add_argument("--disable-blink-features=AutomationControlled")
        opts.add_experimental_option("excludeSwitches", ["enable-automation"])
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=opts)
        return driver

def dismiss(driver):
    try: driver.find_element(By.TAG_NAME,"body").send_keys(Keys.ESCAPE)
    except: pass
    for sel in ["button[aria-label='Close']","#onetrust-accept-btn-handler"]:
        try:
            for el in driver.find_elements(By.CSS_SELECTOR, sel):
                if el.is_displayed(): driver.execute_script("arguments[0].click();",el); time.sleep(0.3)
        except: pass

def scroll_and_wait(driver, index):
    page_h = driver.execute_script("return document.body.scrollHeight")
    step = max(300, page_h // 12)
    
    for y in range(0, page_h + step, step):
        driver.execute_script(f"window.scrollTo(0, {y});")
        time.sleep(SCROLL_PAUSE)
        
        # ลองดึงข้อมูลด้วย Selector เดิมไปก่อน
        found = driver.execute_script("return document.querySelectorAll('section[id^=\"bv-review-\"]').length")
        if found > 0:
            print(f"    ✅ BV loaded at y={y} ({found} reviews)")
            time.sleep(1.5)
            return found

    # ถ้ายึกยักแล้วยังไม่เจอ ให้ลอง scroll ไปจุดล่างสุดอีกรอบ
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight - 1000);")
    time.sleep(3)
    found = driver.execute_script("return document.querySelectorAll('section[id^=\"bv-review-\"]').length")
    
    if found == 0:
        # 📸 ท่าไม้ตาย: ถ่ายรูปหน้าจอมาดูว่า Bot เห็นอะไร!
        screenshot_name = f"debug_product_{index}.png"
        driver.save_screenshot(screenshot_name)
        print(f"    📸 ไม่พบรีวิว! เซฟภาพหน้าจอไว้ที่ {screenshot_name} ลองเปิดดูว่าเว็บโหลดถึงส่วนรีวิวไหม")
        
        # ลองหา div ที่มีคำว่า review เผื่อเขาเปลี่ยน class
        backup_found = driver.execute_script("return document.querySelectorAll('[class*=\"review\" i]').length")
        print(f"    🔍 (Debug) พบ Element ที่มีคำว่า 'review' ใน class: {backup_found} จุด")

    return found

def extract(driver, url, bv_id):
    return driver.execute_script("""
        const out = [];
        document.querySelectorAll('section[id^="bv-review-"]').forEach(sec => {
            const author = (sec.querySelector('[class*="dWWqxa"]')?.innerText||"").trim();
            let rating = null;
            const ra = sec.querySelector('[role="img"][aria-label]');
            if (ra) { const m=ra.getAttribute("aria-label").match(/(\\d+)\\s*จาก\\s*5/); if(m) rating=+m[1]; }
            const title = (sec.querySelector('h3')?.innerText||"").trim();
            const body  = (sec.querySelector('div[id^="bv-review-text-"]')?.innerText||"").trim();
            const date  = (sec.querySelector('[class*="jolJQc"]')?.innerText||"").trim();
            if (body) out.push({author,rating,title,body,date});
        });
        return out;
    """) or []

parser = argparse.ArgumentParser()
parser.add_argument("--csv", required=False)
args = parser.parse_args()

OUTPUT_DIR = Path(__file__).parent / "data_products"
if args.csv:
    csv_path = Path(args.csv)
else:
    csvs = sorted(OUTPUT_DIR.glob("sephora_th_2*.csv"), reverse=True)
    if not csvs: print("❌ ไม่พบ CSV"); sys.exit(1)
    csv_path = csvs[0]

print(f"📂 CSV: {csv_path.name}")
df = pd.read_csv(csv_path)
df = df[df["bv_product_id"].notna() & (df["bv_product_id"] != "")].reset_index(drop=True)

# เลือก 3 products ที่มี rating_count สูงสุด (น่าจะมี reviews)
if "rating_count" in df.columns:
    df = df.sort_values("rating_count", ascending=False)
sample = df.head(TEST_LIMIT)

print(f"\n🧪 Testing {TEST_LIMIT} products:")
for _, row in sample.iterrows():
    print(f"   • {row.get('name','')[:50]}  (bv={row['bv_product_id']}, count={row.get('rating_count','?')})")

driver = make_driver()
results = []

try:
    driver.get("https://www.sephora.co.th")
    time.sleep(4); dismiss(driver)

    for i, (_, row) in enumerate(sample.iterrows()):
        url   = row["product_url"]
        bv_id = row["bv_product_id"]
        name  = str(row.get("name",""))[:45]
        print(f"\n[{i+1}/{TEST_LIMIT}] {name}")
        print(f"  URL: {url}")

        driver.get(url)
        time.sleep(3); dismiss(driver)

        count = scroll_and_wait(driver, i)
        print(f"  BV sections found: {count}")

        if count > 0:
            revs = extract(driver, url, bv_id)
            results.extend(revs)
            print(f"  ✅ {len(revs)} reviews extracted")
            for r in revs[:2]:
                print(f"     ⭐{r['rating']} | {r['author']} | {r['title'][:40]}")
                print(f"     {r['body'][:80]}...")
        else:
            print(f"  ❌ No reviews loaded")

        time.sleep(2)

finally:
    try: driver.quit()
    except: pass

print(f"\n{'='*50}")
print(f"✅ Total reviews extracted: {len(results)}")
if results:
    print("🎉 Pass 2 works! Ready to run full sephora_reviews_scraper.py")
else:
    print("❌ No reviews — ต้อง debug เพิ่ม")