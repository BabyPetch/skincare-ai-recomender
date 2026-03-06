"""
patch_price.py
--------------
Patch ราคาประมาณตาม category ลง DB

Usage:
    python patch_price.py
"""

import psycopg2
import random

DB_CONFIG = {
    "dbname": "skincareCollectionDB",
    "user": "postgres",
    "password": "1234",
    "host": "127.0.0.1",
    "port": "5432"
}

# ราคาประมาณ (min, max) ต่อ category
PRICE_RANGES = {
    "cleanser":    (150,  500),
    "toner":       (200,  600),
    "serum":       (400, 1500),
    "moisturizer": (300, 1000),
    "sunscreen":   (200,  700),
    "mask":        (100,  400),
    "exfoliator":  (300,  900),
    "eye_care":    (400, 1200),
    "treatment":   (300,  800),
}

DEFAULT_RANGE = (200, 800)


def get_random_price(min_p, max_p):
    """สุ่มราคาแบบ round number เช่น 299, 350, 490"""
    price = random.randint(min_p, max_p)
    # ปัดให้ดูเป็นราคาจริง (x9 หรือ x0)
    price = round(price / 50) * 50 - 1
    return max(price, min_p)


def patch_prices():
    conn = psycopg2.connect(**DB_CONFIG)
    try:
        cur = conn.cursor()

        # ดึง products ที่ยังไม่มีราคา
        cur.execute("SELECT id, major_category FROM products WHERE price IS NULL OR price = 0")
        rows = cur.fetchall()
        print(f"  Found {len(rows)} products without price")

        updated = 0
        for product_id, category in rows:
            cat = (category or "").lower().strip()
            min_p, max_p = PRICE_RANGES.get(cat, DEFAULT_RANGE)
            price = get_random_price(min_p, max_p)

            cur.execute(
                "UPDATE products SET price = %s WHERE id = %s",
                (price, product_id)
            )
            updated += 1

        conn.commit()
        print(f"  Updated {updated} products with estimated prices")

        # แสดงตัวอย่าง
        cur.execute("""
            SELECT name, major_category, price 
            FROM products 
            ORDER BY RANDOM() 
            LIMIT 10
        """)
        print("\n  Sample:")
        for name, cat, price in cur.fetchall():
            print(f"    {cat:15} ฿{price:>6}  {name[:40]}")

    finally:
        conn.close()


if __name__ == "__main__":
    patch_prices()