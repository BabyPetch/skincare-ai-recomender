"""
test_algorithm.py
=================
ASA — Algorithm Test Cases
รัน: python3 test_algorithm.py

ทดสอบ 3 เคสหลัก แล้วพิมพ์ผลลัพธ์แบบ clean table
เปรียบเทียบ: สินค้าที่ algorithm แนะนำ vs สิ่งที่คาดหวัง (expected)
"""

import requests
from tabulate import tabulate   # pip install tabulate

BASE_URL = "http://127.0.0.1:5000/api"

# ─────────────────────────────────────────
# แปลภาษา
# ─────────────────────────────────────────
SKIN_TH = {
    "oily":        "หน้ามัน",
    "dry":         "หน้าแห้ง",
    "sensitive":   "แพ้ง่าย",
    "normal":      "ผิวธรรมดา",
    "combination": "ผิวผสม",
}
# ตรงกับ CONCERN_LABEL ใน ai_engine_v2.py และ StepConcerns.jsx
CONCERN_TH = {
    "acne_control":   "สิว",
    "brightening":    "หมองคล้ำ/ฝ้า",
    "anti_aging":     "ริ้วรอย",
    "hydrating":      "แห้งกร้าน",
    "barrier_repair": "ผิวเสีย/แพ้ง่าย",
    "calming":        "ผิวแดง/อักเสบ",
    "exfoliating":    "รูขุมขนกว้าง",
    "antioxidant":    "ริ้วรอยดำ/กระ",
}

# ตรงกับ StepPrice.jsx
PRICE_TH = {
    "low":    "ประหยัด (< 500 บาท)",
    "medium": "ปานกลาง (500–1,500 บาท)",
    "high":   "พรีเมียม (> 1,500 บาท)",
    "any":    "ไม่จำกัดงบ",
}

# ตรงกับ StepAge.jsx
AGE_TH = {
    "teen":   "วัยรุ่น (13–19 ปี)",
    "young":  "วัยหนุ่มสาว (20–29 ปี)",
    "adult":  "วัยทำงาน (30–39 ปี)",
    "mature": "วัยกลางคน (40–49 ปี)",
    "senior": "วัยผู้ใหญ่ (50+ ปี)",
}

# ตรงกับ StepGender.jsx
GENDER_TH = {"female": "หญิง", "male": "ชาย", "other": "ไม่ระบุ"}

# ตรงกับ StepHydration.jsx
HYD_TH = {
    "very_dry": "แห้งตึงมาก",
    "dry":      "ค่อนข้างแห้ง",
    "normal":   "โอเค",
    "oily":     "มันเยิ้ม",
}

# ตรงกับ StepEnvironment.jsx
ENV_TH = {
    "hot_humid":  "ร้อนชื้น",
    "ac_all_day": "แอร์ตลอดวัน",
    "mixed":      "ผสมผสาน",
    "pollution":  "มลภาวะสูง",
    "tropical":   "ชายทะเล/ป่า",
}

# ตรงกับ StepExperience.jsx
EXP_TH = {
    "beginner":     "มือใหม่",
    "intermediate": "ใช้อยู่แล้ว",
    "advanced":     "สกินแคร์จริงจัง",
}

# ตรงกับ StepRoutineTime.jsx
TIME_TH = {
    "morning": "เช้าอย่างเดียว",
    "evening": "เย็นอย่างเดียว",
    "both":    "ทั้งเช้าและเย็น",
}

# ตรงกับ ROUTINE_STEPS ใน ai_engine_v2.py (step_label เป็นภาษาไทยอยู่แล้ว)
# map ไว้เผื่อ API เก่าส่ง key ภาษาอังกฤษมา
STEP_LABEL_TH = {
    "ล้างหน้า":        "ล้างหน้า",
    "โทนเนอร์":        "โทนเนอร์",
    "เซรั่ม":          "เซรั่ม",
    "มอยส์เจอไรเซอร์": "มอยส์เจอไรเซอร์",
    "กันแดด":          "กันแดด",
    # fallback สำหรับ key ภาษาอังกฤษ (backward compat)
    "cleanser":    "ล้างหน้า",
    "toner":       "โทนเนอร์",
    "serum":       "เซรั่ม",
    "moisturizer": "มอยส์เจอไรเซอร์",
    "sunscreen":   "กันแดด",
    "eye_care":    "อายครีม",
    "essence":     "เอสเซนส์",
    "ampoule":     "แอมพูล",
}

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
    {
        "id": "TC4",
        "name": "[Negative] ผิวมัน — แต่ expected สินค้าผิวแห้ง (ตั้งใจให้ไม่ผ่าน)",
        "negative": True,
        "note": "ทดสอบว่า algorithm ไม่แนะนำสินค้าผิวแห้งให้คนผิวมัน → ถ้า FAIL = algorithm ทำงานถูกต้อง",
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
        # ตั้งใจให้ไม่ตรง: input เป็น oily แต่ expected เป็น keyword และ skin ของ dry
        # → ถ้า algorithm ดี ผลควรออกมาเป็น "ไม่ผ่าน" (= algorithm ไม่แนะนำสินค้าผิวแห้งให้คนผิวมัน)
        "expected_keywords": ["hyaluronic acid cream", "rich moisturizer", "ceramide oil", "retinol dry"],
        "expected_skin":     "dry",
    },
    {
        "id": "TC5",
        "name": "ผิวผสม ไม่มี concern (edge case)",
        "payload": {
            "skin_type": "combination",
            "concerns":  [],
            "price_range": "any",
            "context": {
                "age":          "young",
                "gender":       "other",
                "hydration":    "normal",
                "environment":  "mixed",
                "experience":   "beginner",
                "routine_time": "both",
            },
        },
        "expected_keywords": ["cleanser", "moisturizer", "sunscreen", "gentle", "hydrat"],
        "expected_skin":     "combination",
    },
    {
        "id": "TC6",
        "name": "ผิวมัน + ริ้วรอย (concern conflict)",
        "payload": {
            "skin_type": "oily",
            "concerns":  ["anti_aging"],
            "price_range": "high",
            "context": {
                "age":          "adult",
                "gender":       "female",
                "hydration":    "oily",
                "environment":  "ac_all_day",
                "experience":   "advanced",
                "routine_time": "both",
            },
        },
        "expected_keywords": ["retinol", "peptide", "anti-aging", "niacinamide", "vitamin c"],
        "expected_skin":     "oily",
    },
    {
        "id": "TC7",
        "name": "[Hard Negative] ผิวมันสิว — expected สินค้าผิวแห้งคนละโลก",
        "negative": True,
        "note": "ตั้ง expected keyword ให้คนละโลกกับผิวมัน → ถ้า algorithm ดี ต้องไม่ match = ถูกต้อง",
        "payload": {
            "skin_type": "oily",
            "concerns":  ["acne_control"],
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
        "expected_keywords": [
            "ultra rich cream",
            "intensive repair balm",
            "deep nourishing oil",
            "anti-aging night cream",
            "wrinkle lifting",
        ],
        "expected_skin": "dry",
    },
]


# ─────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────
def call_api(payload: dict) -> dict:
    r = requests.post(f"{BASE_URL}/recommend-all", json=payload, timeout=30)
    r.raise_for_status()
    return r.json()


def check_keyword(product: dict, keywords: list) -> bool:
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
        p   = tc["payload"]
        ctx = p["context"]

        skin_th     = SKIN_TH.get(p["skin_type"], p["skin_type"])
        concerns_th = [CONCERN_TH.get(c, c) for c in p["concerns"]]
        price_th    = PRICE_TH.get(p["price_range"], p["price_range"])
        ctx_th = {
            "อายุ":         AGE_TH.get(ctx.get("age", ""), ctx.get("age", "")),
            "เพศ":          GENDER_TH.get(ctx.get("gender", ""), ctx.get("gender", "")),
            "ความชุ่มชื้น": HYD_TH.get(ctx.get("hydration", ""), ctx.get("hydration", "")),
            "สภาพแวดล้อม":  ENV_TH.get(ctx.get("environment", ""), ctx.get("environment", "")),
            "ประสบการณ์":   EXP_TH.get(ctx.get("experience", ""), ctx.get("experience", "")),
            "ช่วงเวลา":     TIME_TH.get(ctx.get("routine_time", ""), ctx.get("routine_time", "")),
        }

        is_negative = tc.get("negative", False)

        print(f"\n{'='*70}")
        print(f"  {tc['id']} — {tc['name']}")
        print(f"{'='*70}")
        if is_negative:
            print(f"  ⚠️  หมายเหตุ: {tc['note']}")
        print(f"  Input: ผิว={skin_th}  ปัญหา={concerns_th}  ราคา={price_th}")
        print(f"  บริบท: {ctx_th}\n")

        try:
            data = call_api(p)
        except Exception as e:
            print(f"  [ผิดพลาด] ไม่สามารถเรียก API ได้: {e}")
            summary.append([tc["id"], tc["name"], "ผิดพลาด", "-", "-"])
            continue

        products = data.get("recommend", [])
        routine  = data.get("routine",  [])

        if not products:
            print("  [แจ้งเตือน] API ตอบกลับแต่ไม่มีสินค้าแนะนำ")
            summary.append([tc["id"], tc["name"], "ไม่มีผล", "-", "-"])
            continue

        # ── ตาราง Top 5 Recommend ──
        rows = []
        passed_count = 0
        for i, prod in enumerate(products[:5], 1):
            kw_ok   = check_keyword(prod, tc["expected_keywords"])
            skin_ok = check_skin(prod, tc["expected_skin"])

            if is_negative:
                # negative: "ผ่าน" = ระบบ ไม่ match expected ผิวแห้ง = ถูกต้อง
                passed = not (kw_ok or skin_ok)
                row_label = "✓ ถูกต้อง" if passed else "✗ แนะนำผิด"
            else:
                passed = kw_ok or skin_ok
                row_label = "ผ่าน" if passed else "ไม่ผ่าน"

            if passed:
                passed_count += 1
            rows.append([
                i,
                f"{prod.get('brand','-')} — {prod.get('name','-')[:40]}",
                prod.get("major_category", "-"),
                f"฿{int(prod.get('price', 0)):,}",
                score_breakdown(prod),
                "✓" if kw_ok   else "✗",
                "✓" if skin_ok else "✗",
                row_label,
            ])

        headers = ["#", "สินค้า", "ประเภท", "ราคา", "Score Breakdown", "Keyword", "ผิว", "ผล"]
        print(tabulate(rows, headers=headers, tablefmt="simple"))

        # ── Routine ──
        if routine:
            print(f"\n  Routine ({len(routine)} ขั้นตอน):")
            r_rows = []
            for prod in routine:
                label_raw = prod.get("step_label", "")
                label_th  = STEP_LABEL_TH.get(label_raw, label_raw)
                r_rows.append([
                    prod.get("step", ""),
                    label_th,
                    prod.get("brand", ""),
                    prod.get("name", "")[:40],
                ])
            print(tabulate(r_rows, headers=["ขั้น", "ประเภท", "แบรนด์", "สินค้า"], tablefmt="simple"))

        # ── Verdict ──
        total   = min(len(products), 5)
        rate    = passed_count / total * 100 if total else 0

        if is_negative:
            # Negative TC: ถ้า algorithm ดี ควรไม่ผ่าน (passed_count ต่ำ) = algorithm ถูกต้อง
            algo_correct = rate < 60
            verdict      = "✓ Algorithm ถูกต้อง" if algo_correct else "✗ Algorithm แนะนำผิด"
            print(f"\n  ผลลัพธ์: {verdict}  (ตรงกับ expected ผิวแห้ง {passed_count}/{total} รายการ, {rate:.0f}%)")
            print(f"  → ถ้า algorithm ดี ควรแนะนำสินค้าผิวมัน ไม่ใช่ผิวแห้ง")
        else:
            verdict = "ผ่าน" if rate >= 60 else "ไม่ผ่าน"
            print(f"\n  ผลลัพธ์: {verdict}  ({passed_count}/{total} รายการผ่าน, {rate:.0f}%)")

        summary.append([tc["id"], tc["name"], verdict, f"{passed_count}/{total}", f"{rate:.0f}%"])
        all_results.append({"tc": tc["id"], "data": data})

    # ── Summary ──
    print(f"\n{'='*70}")
    print("  สรุปผลการทดสอบ")
    print(f"{'='*70}")
    print(tabulate(summary, headers=["ID", "เคสทดสอบ", "ผลลัพธ์", "ผ่าน", "อัตรา"], tablefmt="simple"))

    return all_results


if __name__ == "__main__":
    results = run_tests()