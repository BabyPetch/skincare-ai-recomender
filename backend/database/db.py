from flask import app
import psycopg2
import os
import pandas as pd
import math

# ── อ่านจาก env ถ้ามี DATABASE_URL (Render/Supabase) ──
DATABASE_URL = os.environ.get("DATABASE_URL")

DB_CONFIG = {
    "dbname": "skincareCollectionDB",
    "user": "postgres",
    "password": "1234",
    "host": "127.0.0.1",
    "port": "5432"
}

def get_connection():
    print("🔗 Connecting to DB...")

    if DATABASE_URL:
        return psycopg2.connect(DATABASE_URL)

    return psycopg2.connect(**DB_CONFIG)

CSV_PATH = os.path.join(
    os.path.dirname(__file__), "..",
    "scraper", "data_products",
    "incidecoder_20260314_130516 - Data.csv"
)

ACTIVE_CSV_PATH = os.path.join(
    os.path.dirname(__file__), "..",
    "scraper", "data_products",
    "incidecoder_20260314_130516 - Active_group.csv"
)

PRODUCT_COLUMNS = [
    "product_url", "name", "brand", "major_category", "subtype",
    "price", "rating", "rating_count",
    "active_tags", "function_tags",
    "ingredients_raw", "ingredients_list",
    "image_url", "image_local", "skintype",
    "free_from", "key_ingredients", "key_functions",
    "active_acne", "active_whitening", "active_wrinkle",
    "active_exfoliation", "active_hydration", "active_barrier",
    "active_soothing", "active_oilct", "active_antioxidant",
]


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
    if val is None:
        return None
    if isinstance(val, float) and (math.isnan(val) or math.isinf(val)):
        return None
    # ← เพิ่มตรงนี้
    if isinstance(val, str):
        val_clean = val.replace(',', '').strip()
        try:
            return float(val_clean) if '.' in val_clean else int(val_clean)
        except ValueError:
            return val
    return val


def _import_products(cur, conn):
    csv_path = os.path.normpath(CSV_PATH)
    if not os.path.exists(csv_path):
        print(f"❌ ไม่พบไฟล์ CSV: {csv_path}")
        return

    df = pd.read_csv(csv_path)
    df.columns = [c.strip().lower() for c in df.columns]
    
    # ← เพิ่มตรงนี้
    if 'price' in df.columns:
        df['price'] = df['price'].astype(str).str.replace(',', '', regex=False)
        df['price'] = pd.to_numeric(df['price'], errors='coerce')
    
    cols = [c for c in PRODUCT_COLUMNS if c in df.columns]
    df = df[cols]

    placeholders = ", ".join(["%s"] * len(cols))
    sql = f"INSERT INTO products ({', '.join(cols)}) VALUES ({placeholders})"

    rows = [tuple(_safe(v) for v in row) for row in df.itertuples(index=False, name=None)]

    cur.executemany(sql, rows)
    conn.commit()
    print(f"✅ Import สำเร็จ! {len(rows)} products")


def init_active_ingredients():
    conn = get_connection()
    try:
        cur = conn.cursor()

        # สร้าง table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS active_ingredients (
                id            SERIAL PRIMARY KEY,
                ingredient    TEXT NOT NULL UNIQUE,
                acne          BOOLEAN DEFAULT FALSE,
                whitening     BOOLEAN DEFAULT FALSE,
                wrinkle       BOOLEAN DEFAULT FALSE,
                exfoliation   BOOLEAN DEFAULT FALSE,
                hydration     BOOLEAN DEFAULT FALSE,
                barrierrepair BOOLEAN DEFAULT FALSE,
                soothing      BOOLEAN DEFAULT FALSE,
                oilcontrol    BOOLEAN DEFAULT FALSE,
                antioxidant   BOOLEAN DEFAULT FALSE
            );
        """)
        conn.commit()

        cur.execute("SELECT COUNT(*) FROM active_ingredients")
        count = cur.fetchone()[0]
        if count > 0:
            print(f"✅ active_ingredients พร้อมแล้ว ({count} รายการ) — ข้าม import")
            return

        csv_path = os.path.normpath(ACTIVE_CSV_PATH)
        if not os.path.exists(csv_path):
            print(f"❌ ไม่พบ Active_group CSV: {csv_path}"); return

        df = pd.read_csv(csv_path)
        df['ingredient'] = df['ingredient'].str.strip()
        CATS = ['acne','whitening','wrinkle','exfoliation',
                'hydration','barrierrepair','soothing','oilcontrol','antioxidant']

        rows = []
        for _, row in df.iterrows():
            cats_in = [c.strip() for c in str(row['category']).split(',')]
            rows.append((
                row['ingredient'],
                'acne' in cats_in, 'whitening' in cats_in,
                'wrinkle' in cats_in, 'exfoliation' in cats_in,
                'hydration' in cats_in, 'barrierrepair' in cats_in,
                'soothing' in cats_in, 'oilcontrol' in cats_in,
                'antioxidant' in cats_in,
            ))

        cur.executemany("""
            INSERT INTO active_ingredients
                (ingredient, acne, whitening, wrinkle, exfoliation,
                hydration, barrierrepair, soothing, oilcontrol, antioxidant)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            ON CONFLICT (ingredient) DO NOTHING
        """, rows)
        conn.commit()
        print(f"✅ active_ingredients imported — {len(rows)} ingredients")
    finally:
        conn.close()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)