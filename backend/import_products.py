"""
import_products.py
------------------
Import patched CSV เข้า PostgreSQL

Usage:
    python import_products.py --csv scraper/data_products/incidecoder_20260225_143616_patched.csv
"""

import argparse
import pandas as pd
import psycopg2
from pathlib import Path

DB_CONFIG = {
    "dbname": "skincareCollectionDB",
    "user": "postgres",
    "password": "1234",
    "host": "127.0.0.1",
    "port": "5432"
}


def get_connection():
    return psycopg2.connect(**DB_CONFIG)


def clean_val(val):
    """แปลง NaN → None สำหรับ PostgreSQL"""
    if pd.isna(val):
        return None
    return val


def import_products(csv_path: str):
    df = pd.read_csv(csv_path)
    print(f"  Loaded {len(df):,} rows from {csv_path}")

    conn = get_connection()
    try:
        cur = conn.cursor()

        # ล้างข้อมูลเก่าออกก่อน (ถ้าต้องการ import ใหม่)
        cur.execute("TRUNCATE TABLE products RESTART IDENTITY CASCADE")
        print("  Cleared existing products")

        inserted = 0
        failed = 0

        for _, row in df.iterrows():
            try:
                cur.execute("""
                    INSERT INTO products (
                        product_url, name, brand, major_category, subtype,
                        price, rating, rating_count,
                        active_tags, function_tags,
                        ingredients_raw, ingredients_list,
                        image_url, image_local, skintype
                    ) VALUES (
                        %s, %s, %s, %s, %s,
                        %s, %s, %s,
                        %s, %s,
                        %s, %s,
                        %s, %s, %s
                    )
                """, (
                    clean_val(row.get('product_url')),
                    clean_val(row.get('name')),
                    clean_val(row.get('brand')),
                    clean_val(row.get('major_category')),
                    clean_val(row.get('subtype')),
                    clean_val(row.get('price')) or None,
                    clean_val(row.get('rating')) or None,
                    clean_val(row.get('rating_count')) or None,
                    clean_val(row.get('active_tags')),
                    clean_val(row.get('function_tags')),
                    clean_val(row.get('ingredients_raw')),
                    clean_val(row.get('ingredients_list')),
                    clean_val(row.get('image_url')),
                    clean_val(row.get('image_local')),
                    clean_val(row.get('skintype')),
                ))
                inserted += 1
            except Exception as e:
                print(f"  Failed row {row.get('name')}: {e}")
                failed += 1

        conn.commit()
        print(f"\n  Inserted : {inserted:,}")
        print(f"  Failed   : {failed:,}")
        print("  Done!")

    finally:
        conn.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", required=True)
    args = parser.parse_args()
    import_products(args.csv)