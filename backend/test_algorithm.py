"""
test_algorithm.py
=================
ASA — Algorithm Test Cases
รัน: python3 test_algorithm.py

ทดสอบ 3 เคสหลัก แล้วพิมพ์ผลลัพธ์แบบ clean table
เปรียบเทียบ: สินค้าที่ algorithm แนะนำ vs สิ่งที่คาดหวัง (expected)
"""

import requests
import json
from tabulate import tabulate   # pip install tabulate

BASE_URL = "http://127.0.0.1:5000/api"

# ─────────────────────────────────────────
# TEST CASES
# ─────────────────────────────────────────
TEST_CASES = [
    {
        "id": "TC1",
        "name": "วัยรุ่น ผิวมัน สิว",
        "payload": {
            "skin_type": "oily",
            "concerns":  ["acne_control", "exfoliating"],
            "price_range": "low",
            "context": {
                "age":          "teen",
                "gender":       "other",
                "hydration":    "oily",
                "environment":  "hot_humid",
                "experience":   "beginner",
                "routine_time": "morning",
            },
        },
        # สิ่งที่คาดหวัง: สินค้าต้องมี keyword เหล่านี้ใน name หรือ function_tags
        "expected_keywords": ["salicylic", "bha", "acne", "exfol"],
        "expected_skin":     "oily",
    },
    {
        "id": "TC2",
        "name": "วัยทำงาน ผิวแห้ง ริ้วรอย",
        "payload": {
            "skin_type": "dry",
            "concerns":  ["anti_aging", "hydrating"],
            "price_range": "medium",
            "context": {
                "age":          "adult",
                "gender":       "female",
                "hydration":    "very_dry",
                "environment":  "ac_all_day",
                "experience":   "intermediate",
                "routine_time": "both",
            },
        },
        "expected_keywords": ["hyaluronic", "ceramide", "retinol", "hydrat", "moistur"],
        "expected_skin":     "dry",
    },
    {
        "id": "TC3",
        "name": "วัยกลางคน ผิวแพ้ง่าย ฝ้า",
        "payload": {
            "skin_type": "sensitive",
            "concerns":  ["brightening", "barrier_repair"],
            "price_range": "high",
            "context": {
                "age":          "mature",
                "gender":       "female",
                "hydration":    "dry",
                "environment":  "pollution",
                "experience":   "advanced",
                "routine_time": "both",
            },
        },
        "expected_keywords": ["niacinamide", "vitamin c", "tranexamic", "ceramide", "brightening"],
        "expected_skin":     "sensitive",
    },
]


# ─────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────
def call_api(payload: dict) -> dict:
    r = requests.post(f"{BASE_URL}/recommend-all", json=payload, timeout=30)
    r.raise_for_status()
    return r.json()


def check_keyword(product: dict, keywords: list[str]) -> bool:
    """ตรวจว่าสินค้ามี keyword ใดๆ ใน name / function_tags / brand"""
    haystack = " ".join([
        str(product.get("name", "")),
        str(product.get("function_tags", "")),
        str(product.get("brand", "")),
    ]).lower()
    return any(kw.lower() in haystack for kw in keywords)


def check_skin(product: dict, expected: str) -> bool:
    skin = str(product.get("skintype", "")).lower()
    return expected.lower() in skin or "all" in skin


def score_breakdown(product: dict) -> str:
    expl = product.get("explanation", {})
    bd   = expl.get("score_breakdown", {}) if isinstance(expl, dict) else {}
    if not bd:
        fs = product.get("final_score", "-")
        return f"final={fs}"
    return (
        f"concern={bd.get('concern', {}).get('score', '-'):.3f} | "
        f"cosine={bd.get('tfidf', {}).get('score', '-'):.3f} | "
        f"context={bd.get('context', {}).get('score', '-'):.3f} | "
        f"final={bd.get('final', '-'):.4f}"
    )


# ─────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────
def run_tests():
    all_results = []
    summary     = []

    for tc in TEST_CASES:
        print(f"\n{'='*70}")
        print(f"  {tc['id']} — {tc['name']}")
        print(f"{'='*70}")
        print(f"  Input: skin={tc['payload']['skin_type']}  "
              f"concerns={tc['payload']['concerns']}  "
              f"price={tc['payload']['price_range']}")
        print(f"  Context: {tc['payload']['context']}\n")

        try:
            data = call_api(tc["payload"])
        except Exception as e:
            print(f"  [ERROR] ไม่สามารถเรียก API ได้: {e}")
            summary.append([tc["id"], tc["name"], "ERROR", "-", "-"])
            continue

        products = data.get("recommend", [])
        routine  = data.get("routine",  [])

        if not products:
            print("  [WARNING] API ตอบกลับแต่ไม่มี recommend ใดๆ")
            summary.append([tc["id"], tc["name"], "NO RESULT", "-", "-"])
            continue

        # ── ตาราง Top 5 Recommend ──
        rows = []
        passed_count = 0
        for i, p in enumerate(products[:5], 1):
            kw_ok   = check_keyword(p, tc["expected_keywords"])
            skin_ok = check_skin(p, tc["expected_skin"])
            passed  = kw_ok or skin_ok
            if passed:
                passed_count += 1
            rows.append([
                i,
                f"{p.get('brand','-')} — {p.get('name','-')[:40]}",
                p.get("major_category", "-"),
                f"฿{int(p.get('price', 0)):,}",
                score_breakdown(p),
                "✓" if kw_ok   else "✗",
                "✓" if skin_ok else "✗",
                "PASS" if passed else "FAIL",
            ])

        headers = ["#", "สินค้า", "ประเภท", "ราคา", "Score Breakdown", "Keyword", "Skin", "ผล"]
        print(tabulate(rows, headers=headers, tablefmt="simple"))

        # ── Routine ──
        if routine:
            print(f"\n  Routine ({len(routine)} steps):")
            r_rows = [[p.get("step",""), p.get("step_label",""), p.get("brand",""), p.get("name","")[:40]] for p in routine]
            print(tabulate(r_rows, headers=["Step","Label","Brand","สินค้า"], tablefmt="simple"))

        # ── Verdict ──
        total   = min(len(products), 5)
        rate    = passed_count / total * 100 if total else 0
        verdict = "PASS" if rate >= 60 else "FAIL"
        print(f"\n  Verdict: {verdict}  ({passed_count}/{total} ผ่าน, {rate:.0f}%)")

        summary.append([tc["id"], tc["name"], verdict, f"{passed_count}/{total}", f"{rate:.0f}%"])
        all_results.append({"tc": tc["id"], "data": data})

    # ── Summary ──
    print(f"\n{'='*70}")
    print("  SUMMARY")
    print(f"{'='*70}")
    print(tabulate(summary, headers=["ID","Test Case","Verdict","ผ่าน","Rate"], tablefmt="simple"))

    return all_results


if __name__ == "__main__":
    results = run_tests()