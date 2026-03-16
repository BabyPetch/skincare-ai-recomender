"""
เพิ่มตรงนี้ใน ai_engine_v2.py ส่วน import/global
"""
import json
from pathlib import Path

# โหลด ingredient descriptions
_DESC_PATH = Path(__file__).parent.parent / "training" / "model" / "ingredient_descriptions.json"
INGR_DESC = {}
if _DESC_PATH.exists():
    with open(_DESC_PATH, encoding="utf-8") as f:
        INGR_DESC = json.load(f)
    print(f"✅ Ingredient descriptions loaded: {len(INGR_DESC)}")
else:
    print("⚠️  ingredient_descriptions.json ไม่พบ — explanation จะไม่มี description")


# แก้ _build_explanation() — ส่วน concern match
# แทนที่:
#   if ingr_examples:
#       reasons.append(f"ช่วย{label}: {', '.join(ingr_examples)}")

# ด้วย:
def _format_concern_reason(label, ingr_examples):
    parts = []
    for ing in ingr_examples[:2]:
        desc = INGR_DESC.get(ing.lower(), {}).get('description_th', '')
        if desc:
            # ตัดให้สั้น ไม่เกิน 60 ตัวอักษร
            short = desc[:60] + '...' if len(desc) > 60 else desc
            parts.append(f"{ing} ({short})")
        else:
            parts.append(ing)
    if parts:
        return f"ช่วย{label}: " + " | ".join(parts)
    return f"ช่วย{label}"