"""
import_products.py
วางไฟล์นี้ใน backend/ แล้วรัน:
  python import_products.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

import pandas as pd
from database.db import get_connection

CSV_PATH = r"scraper\data_products\incidecoder_20260225_143616_patched.csv"

COLUMNS = [
    "product_url", "name", "brand", "major_category", "subtype",
    "price", "rating", "rating_count",
    "active_tags", "function_tags",
    "ingredients_raw", "ingredients_list",
    "image_url", "image_local", "skintype",
]

def main():
    print("📂 Loading CSV...")
    df = pd.read_csv(CSV_PATH)
    df.columns = [c.strip().lower() for c in df.columns]

    # keep only known columns
    cols = [c for c in COLUMNS if c in df.columns]
    df   = df[cols].where(pd.notnull(df[cols]), None)
    print(f"   {len(df)} rows, {len(cols)} columns")

    conn = get_connection()
    cur  = conn.cursor()

    print("🗑  Clearing old products...")
    cur.execute("TRUNCATE TABLE products RESTART IDENTITY CASCADE;")

    print("⬆️  Inserting...")
    placeholders = ", ".join(["%s"] * len(cols))
    sql = f"INSERT INTO products ({', '.join(cols)}) VALUES ({placeholders})"
    rows = [tuple(row) for row in df.itertuples(index=False, name=None)]
    cur.executemany(sql, rows)

    conn.commit()
    cur.close()
    conn.close()
    print(f"✅ Done! {len(rows)} products imported.")

if __name__ == "__main__":
    main()