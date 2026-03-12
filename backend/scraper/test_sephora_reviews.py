"""
TEST: ดึง reviews ผ่าน swat_reviews config + bfd endpoint
python test_sephora_reviews.py
"""
import requests, json, re

BV_ID = "thailand-16106-156998"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Referer": "https://www.sephora.co.th/",
    "Bv-Bfd-Token": "19416,main_site,th_TH",
    "Accept": "application/json, */*",
    "Origin": "https://www.sephora.co.th",
}

# ---- Step 1: ดู config ว่ามี API endpoint อะไรบ้าง ----
print("=" * 60)
print("STEP 1: swat_reviews config")
cfg_url = "https://apps.bazaarvoice.com/deployments/sephora-au/main_site/production/th_TH/swat_reviews-config.js"
r = requests.get(cfg_url, headers={"User-Agent": HEADERS["User-Agent"]}, timeout=10)
print(f"Status: {r.status_code}")
# หา URL patterns ใน config
urls_found = re.findall(r'https://[^\s\'"]+', r.text)
api_urls = [u for u in urls_found if 'bfd' in u or 'api' in u or 'review' in u.lower()]
print(f"API URLs in config: {api_urls[:10]}")
print(f"Config snippet: {r.text[:600]}")

# ---- Step 2: ลอง bfd endpoint ที่เจอใน Network (bfd/v1 + filter) ----
print("\n" + "=" * 60)
print("STEP 2: bfd bulk data endpoint")

# จาก network log เจอ: bfd/v1/clients/sephora-au/...filter=id:thailand-16106-156998
# ลองเปลี่ยน path เป็น reviews
test_urls = [
    # path เดิมจาก network แต่เปลี่ยนเป็น reviews
    f"https://apps.bazaarvoice.com/bfd/v1/clients/sephora-au/api-products/cv2/resources/data/display/0.2alpha/product/reviews?productid={BV_ID}&Limit=10&Sort=SubmissionTime%3Adesc&contentlocale=th_TH%2Cen_TH%2Cen_US",
    # ลอง swat reviews endpoint (ชื่อเหมือน JS bundle)
    f"https://apps.bazaarvoice.com/bfd/v1/clients/sephora-au/main_site/production/th_TH/swat_reviews/reviews.json?Filter=ProductId:{BV_ID}&Limit=10&Sort=SubmissionTime:desc",
    # ลอง path แบบ apiVersion 5.5 + displaycode
    f"https://apps.bazaarvoice.com/bfd/v1/clients/sephora-au/main_site/th_TH/reviews.json?Filter=ProductId:{BV_ID}&Limit=10&Sort=SubmissionTime:desc&apiversion=5.5",
    # ลอง path แบบ production ไม่มี main_site
    f"https://apps.bazaarvoice.com/bfd/v1/clients/sephora-au/production/th_TH/reviews.json?Filter=ProductId:{BV_ID}&Limit=10&Sort=SubmissionTime:desc&apiversion=5.5",
    # ลอง bfd v2
    f"https://apps.bazaarvoice.com/bfd/v2/clients/sephora-au/main_site/production/th_TH/reviews.json?Filter=ProductId:{BV_ID}&Limit=10&Sort=SubmissionTime:desc",
    # ลอง path ที่เจอใน Network สำหรับ reviews (display/0.2alpha แต่ path reviews)
    f"https://apps.bazaarvoice.com/bfd/v1/clients/sephora-au/api-products/cv2/resources/data/display/0.2alpha/reviews?productid={BV_ID}&Limit=10&Sort=SubmissionTime%3Adesc&contentlocale=th_TH",
]

for i, url in enumerate(test_urls):
    print(f"\n  [{i+1}] {url[:95]}...")
    try:
        r = requests.get(url, headers=HEADERS, timeout=8)
        print(f"  Status: {r.status_code} | Size: {len(r.text)}")
        if r.status_code == 200 and len(r.text) > 200:
            try:
                d = r.json()
                print(f"  ✅ JSON keys: {list(d.keys())[:6]}")
                for key in ["Results","reviews","data","ReviewList","content","items"]:
                    if key in d and d[key]:
                        print(f"  ✅ '{key}': {len(d[key])} items")
                        rv = d[key][0]
                        print(f"     Sample: rating={rv.get('Rating') or rv.get('rating')}, author={rv.get('UserNickname') or rv.get('author','?')}")
                        break
            except:
                print(f"  Raw: {r.text[:150]}")
    except Exception as e:
        print(f"  Error: {e}")