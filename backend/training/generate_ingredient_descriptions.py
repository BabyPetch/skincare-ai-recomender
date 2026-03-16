"""
generate_ingredient_descriptions.py
=====================================
ใช้ Claude API generate description สำหรับ 210 active ingredients
แล้ว save เป็น ingredient_descriptions.json

pip install anthropic pandas
python generate_ingredient_descriptions.py
"""

import json, time
from pathlib import Path
import pandas as pd
import anthropic

BASE     = Path(__file__).parent
PROJECT  = BASE.parent
DATA_DIR = PROJECT / "scraper" / "data_products"
OUT_FILE = BASE / "model" / "ingredient_descriptions.json"
OUT_FILE.parent.mkdir(exist_ok=True)

ACTIVE_CSV = DATA_DIR / "incidecoder_20260314_130516 - Active_group.csv"

CATEGORIES = {
    'acne':         'ลดสิว/รักษาสิว',
    'whitening':    'ลดหมองคล้ำ/ฝ้า/กระ',
    'wrinkle':      'ลดริ้วรอย/ชะลอวัย',
    'exfoliation':  'ผลัดเซลล์ผิว',
    'hydration':    'ให้ความชุ่มชื้น',
    'barrierrepair':'เสริมเกราะผิว',
    'soothing':     'ลดการอักเสบ/ปลอบประโลม',
    'oilcontrol':   'ควบคุมความมัน',
    'antioxidant':  'ต้านอนุมูลอิสระ',
}

def generate_descriptions(ingredients_df):
    client = anthropic.Anthropic(api_key="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")
    descriptions = {}

    # โหลด cache ถ้ามีอยู่แล้ว
    if OUT_FILE.exists():
        with open(OUT_FILE, encoding="utf-8") as f:
            descriptions = json.load(f)
        print(f"📂 Loaded {len(descriptions)} cached descriptions")

    total = len(ingredients_df)
    for i, row in ingredients_df.iterrows():
        ingr = row['ingredient'].strip()
        key  = ingr.lower()

        if key in descriptions:
            continue  # skip ถ้ามีแล้ว

        cats_raw = [c.strip() for c in str(row['category']).split(',')]
        cats_th  = [CATEGORIES.get(c, c) for c in cats_raw if c in CATEGORIES]
        cats_str = ', '.join(cats_th)

        prompt = f"""You are a skincare ingredient expert. Explain the ingredient "{ingr}" in Thai language.

This ingredient belongs to these skincare benefit categories: {cats_str}

Write a SHORT explanation (2-3 sentences max) in Thai that:
1. What this ingredient is (briefly)
2. How it helps the skin (specific to the categories above)
3. Who should use it (skin type/concern)

Format: plain text only, no bullet points, no markdown.
Keep it concise and easy for Thai consumers to understand."""

        try:
            msg = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=200,
                messages=[{"role": "user", "content": prompt}]
            )
            desc = msg.content[0].text.strip()
            descriptions[key] = {
                "ingredient": ingr,
                "categories": cats_raw,
                "description_th": desc,
            }
            idx = list(ingredients_df.index).index(i) + 1
            print(f"  [{idx:3d}/{total}] ✅ {ingr[:40]}")
            print(f"         {desc[:80]}...")

            # save ทุก 10 ตัว
            if idx % 10 == 0:
                with open(OUT_FILE, "w", encoding="utf-8") as f:
                    json.dump(descriptions, f, ensure_ascii=False, indent=2)
                print(f"  💾 Saved {len(descriptions)} descriptions")

            time.sleep(0.3)  # rate limit

        except Exception as e:
            print(f"  [{i}] ❌ {ingr}: {e}")
            time.sleep(2)

    # final save
    with open(OUT_FILE, "w", encoding="utf-8") as f:
        json.dump(descriptions, f, ensure_ascii=False, indent=2)

    print(f"\n✅ Done — {len(descriptions)} descriptions saved → {OUT_FILE}")
    return descriptions

if __name__ == "__main__":
    print("="*55)
    print("  Generate Ingredient Descriptions")
    print("="*55)

    df = pd.read_csv(ACTIVE_CSV)
    df['ingredient'] = df['ingredient'].str.strip()
    print(f"📋 {len(df)} ingredients to describe\n")

    descriptions = generate_descriptions(df)

    # Preview
    print("\n📖 Sample descriptions:")
    for key, val in list(descriptions.items())[:3]:
        print(f"\n  {val['ingredient']}")
        print(f"  Categories: {', '.join(val['categories'])}")
        print(f"  {val['description_th']}")


# ================================================================
# PATCH ai_engine_v2.py — เพิ่ม description เข้า explanation
# ================================================================
# ใน _build_explanation() แก้ตรงนี้:
#
# เดิม:
#   reasons.append(f"ช่วย{label}: {', '.join(ingr_examples)}")
#
# แก้เป็น:
#   for ing in ingr_examples[:2]:
#       desc = INGR_DESC.get(ing.lower(), {}).get('description_th', '')
#       if desc:
#           reasons.append(f"ช่วย{label} — {ing}: {desc[:60]}...")
#       else:
#           reasons.append(f"ช่วย{label}: {ing}")
# ================================================================