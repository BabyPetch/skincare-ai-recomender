import psycopg2
import os
import pandas as pd
import math

DB_CONFIG = {
    "dbname": "skincareCollectionDB",
    "user": "postgres",
    "password": "1234",
    "host": "127.0.0.1",
    "port": "5432"
}

CSV_PATH = os.path.join(
    os.path.dirname(__file__), "..",
    "scraper", "data_products",
    "incidecoder_20260225_143616_patched.csv"
)

PRODUCT_COLUMNS = [
    "product_url", "name", "brand", "major_category", "subtype",
    "price", "rating", "rating_count",
    "active_tags", "function_tags",
    "ingredients_raw", "ingredients_list",
    "image_url", "image_local", "skintype",
]


def get_connection():
    print("🔗 Connecting to DB...")
    return psycopg2.connect(**DB_CONFIG)


def init_database():
    conn = get_connection()
    try:
        cur = conn.cursor()
        schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
        with open(schema_path, "r", encoding="utf-8") as f:
            cur.execute(f.read())
        conn.commit()
        print("✅ Database schema ready.")

        cur.execute("SELECT COUNT(*) FROM products")
        count = cur.fetchone()[0]

        if count > 0:
            print(f"✅ Products พร้อมแล้ว ({count} รายการ) — ข้าม import")
        else:
            print("⚠️  ไม่พบ products — เริ่ม import CSV...")
            _import_products(cur, conn)
    finally:
        conn.close()


def _safe(val):
    """แปลงค่าให้ปลอดภัยสำหรับ PostgreSQL — nan/inf → None"""
    if val is None:
        return None
    if isinstance(val, float) and (math.isnan(val) or math.isinf(val)):
        return None
    return val


def _import_products(cur, conn):
    csv_path = os.path.normpath(CSV_PATH)

    if not os.path.exists(csv_path):
        print(f"❌ ไม่พบไฟล์ CSV: {csv_path}")
        print("   วาง CSV ที่ scraper/data_products/ แล้ว restart ใหม่")
        return

    df = pd.read_csv(csv_path)
    df.columns = [c.strip().lower() for c in df.columns]
    cols = [c for c in PRODUCT_COLUMNS if c in df.columns]
    df = df[cols]

    placeholders = ", ".join(["%s"] * len(cols))
    sql = f"INSERT INTO products ({', '.join(cols)}) VALUES ({placeholders})"

    rows = [tuple(_safe(v) for v in row) for row in df.itertuples(index=False, name=None)]

    cur.executemany(sql, rows)
    conn.commit()
    print(f"✅ Import สำเร็จ! {len(rows)} products")