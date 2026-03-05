"""
thai_mapping.py
---------------
แปลงคำภาษาไทยที่ user พิมพ์ → ค่าที่ recommender เข้าใจ

Import และใช้งาน:
    from thai_mapping import parse_thai_input

    skin_type, concerns, category = parse_thai_input("หน้ามัน สิว เซรั่ม")
    # → ("oily", ["acne_control"], "serum")
"""

# ================================================================
# SKIN TYPE MAPPING
# ================================================================

SKINTYPE_MAP = {
    # แห้ง
    "แห้ง":         "dry",
    "หน้าแห้ง":     "dry",
    "ผิวแห้ง":      "dry",
    "ขาดน้ำ":       "dry",
    "ผิวขาดน้ำ":    "dry",
    "หน้าลอก":      "dry",
    "ผิวลอก":       "dry",

    # มัน
    "มัน":          "oily",
    "หน้ามัน":      "oily",
    "ผิวมัน":       "oily",
    "มันเยิ้ม":     "oily",
    "รูขุมขนกว้าง": "oily",

    # แพ้ง่าย / บอบบาง
    "แพ้ง่าย":      "sensitive",
    "ผิวแพ้ง่าย":   "sensitive",
    "บอบบาง":       "sensitive",
    "ผิวบอบบาง":    "sensitive",
    "แดง":          "sensitive",
    "ผิวแดง":       "sensitive",
    "ระคายเคือง":   "sensitive",
    "แพ้":          "sensitive",

    # ผสม
    "ผสม":          "combination",
    "ผิวผสม":       "combination",
    "หน้าผสม":      "combination",
    "มันบางส่วน":   "combination",
    "ทีโซน":        "combination",
    "t-zone":       "combination",

    # ทุกสภาพผิว
    "ทุกสภาพผิว":   "all",
    "ทุกผิว":       "all",
    "ผิวปกติ":      "all",
    "ปกติ":         "all",
}

# ================================================================
# CONCERN / FUNCTION TAG MAPPING
# ================================================================

CONCERN_MAP = {
    # สิว
    "สิว":              "acne_control",
    "หน้าสิว":          "acne_control",
    "สิวอุดตัน":        "acne_control",
    "สิวอักเสบ":        "acne_control",
    "สิวหัวดำ":         "acne_control",
    "สิวหัวขาว":        "acne_control",
    "รักษาสิว":         "acne_control",
    "ลดสิว":            "acne_control",

    # ฝ้า / กระ / จุดด่างดำ
    "ฝ้า":              "brightening",
    "กระ":              "brightening",
    "จุดด่างดำ":        "brightening",
    "รอยดำ":            "brightening",
    "ริ้วรอยดำ":        "brightening",
    "หน้าหมอง":         "brightening",
    "ผิวหมอง":          "brightening",
    "ผิวไม่สม่ำเสมอ":  "brightening",
    "ผิวกระจ่างใส":     "brightening",
    "กระจ่างใส":        "brightening",
    "ลดฝ้า":            "brightening",
    "ลดกระ":            "brightening",

    # ริ้วรอย / ต่อต้านวัย
    "ริ้วรอย":          "anti_aging",
    "ลดริ้วรอย":        "anti_aging",
    "ต่อต้านวัย":       "anti_aging",
    "ชะลอวัย":          "anti_aging",
    "หน้าแก่":          "anti_aging",
    "ผิวหย่อนคล้อย":    "anti_aging",
    "กระชับผิว":        "anti_aging",
    "คอลลาเจน":         "anti_aging",

    # ความชุ่มชื้น
    "ขาดความชุ่มชื้น":  "hydrating",
    "ให้ความชุ่มชื้น":  "hydrating",
    "เพิ่มความชุ่มชื้น":"hydrating",
    "หน้าแห้งตึง":      "hydrating",
    "ผิวตึง":           "hydrating",
    "ความชุ่มชื้น":     "hydrating",

    # ผิวแพ้ / อักเสบ
    "ผิวอักเสบ":        "calming",
    "ลดการอักเสบ":      "calming",
    "ผิวแดง":           "calming",
    "ระคายเคือง":       "calming",
    "ผิวระคายเคือง":    "calming",
    "ผ่อนคลายผิว":      "calming",
    "ปลอบประโลม":       "calming",

    # เสริมเกราะผิว
    "เกราะผิว":         "barrier_repair",
    "เสริมเกราะ":       "barrier_repair",
    "ซ่อมแซมผิว":       "barrier_repair",
    "ผิวเสีย":          "barrier_repair",

    # ผลัดเซลล์ผิว
    "ผลัดเซลล์":        "exfoliating",
    "ผลัดผิว":          "exfoliating",
    "ขัดผิว":           "exfoliating",
    "เซลล์ผิวเก่า":     "exfoliating",

    # ต้านอนุมูลอิสระ
    "อนุมูลอิสระ":      "antioxidant",
    "ต้านอนุมูล":       "antioxidant",
    "วิตามินซี":        "brightening",
    "วิตามินอี":        "antioxidant",
    "เรตินอล":          "anti_aging",
    "เนียซินาไมด์":     "brightening",
    "ไฮยา":             "hydrating",
    "ไฮยาลูโรนิค":     "hydrating",
    "เซราไมด์":         "barrier_repair",
}

# ================================================================
# PRODUCT CATEGORY MAPPING
# ================================================================

CATEGORY_MAP = {
    # มอยส์เจอไรเซอร์
    "มอยส์เจอไรเซอร์":  "moisturizer",
    "ครีม":              "moisturizer",
    "ครีมบำรุง":         "moisturizer",
    "ครีมหน้า":          "moisturizer",
    "โลชั่น":            "moisturizer",
    "บำรุงผิว":          "moisturizer",

    # เซรั่ม
    "เซรั่ม":            "serum",
    "เซรั่มหน้า":        "serum",
    "แอมพูล":            "serum",

    # ยันแดด / กันแดด
    "ยันแดด":            "sunscreen",
    "กันแดด":            "sunscreen",
    "ครีมกันแดด":        "sunscreen",
    "spf":               "sunscreen",

    # โทนเนอร์
    "โทนเนอร์":          "toner",
    "โทนเนอร์หน้า":      "toner",
    "น้ำตบ":             "toner",
    "สกินวอเตอร์":       "toner",

    # คลีนเซอร์
    "คลีนเซอร์":         "cleanser",
    "โฟมล้างหน้า":       "cleanser",
    "ล้างหน้า":          "cleanser",
    "เจลล้างหน้า":       "cleanser",
    "ครีมล้างหน้า":      "cleanser",
    "น้ำยาล้างหน้า":     "cleanser",
    "ไมเซล่า":           "cleanser",

    # มาส์ก
    "มาส์ก":             "mask",
    "แผ่นมาส์ก":         "mask",
    "มาส์กหน้า":         "mask",
    "ชีทมาส์ก":          "mask",

    # เอ็กซ์โฟเลียเตอร์
    "เอ็กซ์โฟเลียเตอร์": "exfoliator",
    "สครับ":             "exfoliator",
    "ผลัดเซลล์":         "exfoliator",
    "พีลลิ่ง":           "exfoliator",

    # ครีมบำรุงรอบดวงตา
    "ครีมตา":            "eye_care",
    "บำรุงรอบดวงตา":     "eye_care",
    "อายครีม":           "eye_care",
}

# ================================================================
# PARSE FUNCTION
# ================================================================

def parse_thai_input(text: str):
    """
    รับข้อความภาษาไทย (หรือ mixed) จาก user
    คืนค่า (skin_type, concerns, category)

    skin_type : str  เช่น "oily"  (ถ้าไม่พบ → "")
    concerns  : list เช่น ["acne_control", "brightening"]
    category  : str  เช่น "serum" (ถ้าไม่พบ → "")
    """
    words = text.strip().split()
    # ลองทั้งคำเดี่ยวและ bigram
    tokens = set(words)
    for i in range(len(words) - 1):
        tokens.add(words[i] + words[i+1])
        tokens.add(words[i] + " " + words[i+1])

    skin_type = ""
    concerns  = []
    category  = ""

    for token in tokens:
        t = token.strip()
        if not skin_type and t in SKINTYPE_MAP:
            skin_type = SKINTYPE_MAP[t]
        if t in CONCERN_MAP:
            tag = CONCERN_MAP[t]
            if tag not in concerns:
                concerns.append(tag)
        if not category and t in CATEGORY_MAP:
            category = CATEGORY_MAP[t]

    return skin_type, concerns, category


# ================================================================
# QUICK TEST
# ================================================================

if __name__ == "__main__":
    tests = [
        "หน้ามัน สิว",
        "ผิวแห้ง ขาดความชุ่มชื้น เซรั่ม",
        "ผิวแพ้ง่าย ผิวแดง ครีมบำรุง",
        "ฝ้า กระ ริ้วรอย กันแดด",
        "ผิวผสม จุดด่างดำ โทนเนอร์",
        "สิวอุดตัน รูขุมขนกว้าง ล้างหน้า",
    ]

    print("=" * 55)
    print("  Thai Mapping Test")
    print("=" * 55)
    for t in tests:
        st, concerns, cat = parse_thai_input(t)
        print(f"\n  input    : {t}")
        print(f"  skintype : {st or '(ไม่พบ)'}")
        print(f"  concerns : {concerns or '(ไม่พบ)'}")
        print(f"  category : {cat or '(ไม่พบ)'}")