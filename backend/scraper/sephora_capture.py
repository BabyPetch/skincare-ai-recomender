"""
Sephora API Capture
เปิด browser → ดัก network request อัตโนมัติ → print endpoint + headers

python sephora_capture.py
"""

import json, time, re
from pathlib import Path

try:
    import undetected_chromedriver as uc
except ImportError:
    print("pip install undetected-chromedriver"); exit(1)

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ── เปิด Chrome พร้อม performance logging ────────────────────────
opts = uc.ChromeOptions()
opts.add_argument("--window-size=1440,900")
opts.add_argument("--lang=en-US")
opts.set_capability("goog:loggingPrefs", {"performance": "ALL"})

print("🚀 Opening browser...")
driver = uc.Chrome(options=opts, version_main=None)

URL = "https://www.sephora.com/shop/moisturizing-cream-oils-mists"

try:
    # ── Load page ────────────────────────────────────────────────
    driver.get("https://www.sephora.com")
    time.sleep(4)

    # ปิด popup
    for sel in ["button[aria-label='Close']","[data-at='close_button']","#onetrust-accept-btn-handler"]:
        try:
            driver.find_element(By.CSS_SELECTOR, sel).click()
            time.sleep(1); break
        except: pass

    print(f"📄 Loading: {URL}")
    driver.get(URL)
    time.sleep(3)

    # ปิด geo-block popup
    for sel in ["a[href*='sephora.com']", "button[aria-label='Close']"]:
        try:
            els = driver.find_elements(By.CSS_SELECTOR, sel)
            for el in els:
                txt = (el.text or "").lower()
                if "continue" in txt:
                    el.click(); print("✅ Dismissed geo-block"); time.sleep(2); break
        except: pass

    # Inject fetch/XHR interceptor ก่อน scroll
    driver.execute_script("""
        window.__captured = [];
        const _fetch = window.fetch;
        window.fetch = function(...args) {
            const url = typeof args[0] === 'string' ? args[0] : (args[0]?.url || '');
            const opts = args[1] || {};
            window.__captured.push({
                type: 'fetch',
                url,
                method: opts.method || 'GET',
                headers: opts.headers || {}
            });
            return _fetch.apply(this, args);
        };
        const _open = XMLHttpRequest.prototype.open;
        const _setHeader = XMLHttpRequest.prototype.setRequestHeader;
        XMLHttpRequest.prototype.open = function(method, url) {
            this._url = url; this._method = method; this._headers = {};
            return _open.apply(this, arguments);
        };
        XMLHttpRequest.prototype.setRequestHeader = function(k, v) {
            this._headers = this._headers || {};
            this._headers[k] = v;
            return _setHeader.apply(this, arguments);
        };
        const _send = XMLHttpRequest.prototype.send;
        XMLHttpRequest.prototype.send = function() {
            window.__captured.push({
                type: 'xhr', url: this._url,
                method: this._method, headers: this._headers || {}
            });
            return _send.apply(this, arguments);
        };
    """)

    # Scroll ช้าๆ เพื่อ trigger API calls
    print("📜 Scrolling to trigger API calls...")
    for i in range(10):
        driver.execute_script(f"window.scrollTo(0, {i * 500});")
        time.sleep(1.2)

    time.sleep(3)

    # ── ดึง captured requests ─────────────────────────────────────
    captured = driver.execute_script("return window.__captured || [];")

    # ── ดึง performance logs ด้วย ─────────────────────────────────
    perf_urls = []
    try:
        for entry in driver.get_log("performance"):
            msg = json.loads(entry["message"])["message"]
            if msg.get("method") == "Network.requestWillBeSent":
                req = msg["params"].get("request", {})
                url = req.get("url","")
                hdrs = req.get("headers", {})
                if url:
                    perf_urls.append({"url": url, "method": req.get("method","GET"),
                                       "headers": hdrs, "type": "perf"})
    except: pass

    all_requests = captured + perf_urls

    # ── Filter เฉพาะ API ที่น่าสนใจ ──────────────────────────────
    API_KEYWORDS = [
        "catalog", "product", "search", "browse", "category",
        "api.", "/api/", "graphql", "gateway", "v1", "v2",
        "pageSize", "currentPage", "categoryId", "skus"
    ]

    print(f"\n{'='*65}")
    print(f"📡 Captured {len(all_requests)} total requests")
    print(f"{'='*65}")

    seen    = set()
    api_hits = []

    for r in all_requests:
        url = r.get("url","")
        if not url or url in seen: continue
        if not any(k.lower() in url.lower() for k in API_KEYWORDS): continue
        if any(x in url for x in [".css",".js",".png",".jpg",".gif",".woff","favicon","analytics","gtm","segment","hotjar"]): continue

        seen.add(url)
        api_hits.append(r)

        print(f"\n🔗 [{r.get('type','?').upper()}] {r.get('method','GET')}")
        print(f"   URL: {url[:120]}")
        hdrs = r.get("headers", {})
        important_headers = {k:v for k,v in hdrs.items()
                             if any(x in k.lower() for x in
                                   ["auth","key","token","client","x-","accept","content"])}
        if important_headers:
            print(f"   Headers:")
            for k,v in list(important_headers.items())[:8]:
                print(f"     {k}: {v[:80]}")

    # ── Save ─────────────────────────────────────────────────────
    out = Path("sephora_api_config.json")
    out.write_text(json.dumps({
        "captured_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "api_requests": [
            {"url": r["url"], "method": r.get("method","GET"), "headers": r.get("headers",{})}
            for r in api_hits
        ]
    }, indent=2, ensure_ascii=False))

    print(f"\n{'='*65}")
    print(f"✅ Found {len(api_hits)} API endpoints")
    print(f"💾 Saved → sephora_api_config.json")

    if not api_hits:
        print("\n⚠️  ไม่เจอ API — อาจเป็นเพราะ:")
        print("   1. Sephora ใช้ GraphQL (ดูใน captured ทั้งหมด)")
        print("   2. Request ถูก block")
        print("\n📋 All captured URLs (top 30):")
        for r in list(seen)[:30]:
            print(f"   {r[:100]}")

finally:
    print("\n⏸  Browser ยังเปิดอยู่ — กด Enter เพื่อปิด")
    input()
    try: driver.quit()
    except: pass