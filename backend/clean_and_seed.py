import json
import os
from database.db import get_connection

# ===== Load JSON =====
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(BASE_DIR, "scraper", "products_raw.json")

print("Opening:", file_path)

with open(file_path, "r", encoding="utf-8") as f:
    data = json.load(f)


def clean_text(text):
    if not text:
        return ""
    return " ".join(text.split())


def seed():
    print("🔗 Connecting to DB...")
    conn = get_connection()
    cur = conn.cursor()

    # ===== DROP + RECREATE TABLE (FULL SCHEMA) =====
    print("🗑 Dropping old table...")
    cur.execute("DROP TABLE IF EXISTS products;")

    print("🛠 Creating new table...")
    cur.execute("""
        CREATE TABLE products (
            id SERIAL PRIMARY KEY,
            name TEXT,
            brand TEXT,
            category TEXT,
            ingredients TEXT,
            price NUMERIC,
            image_url TEXT
        );
    """)
    conn.commit()

    print("Total records:", len(data))

    # ===== INSERT DATA =====
    for i, item in enumerate(data):
        name = clean_text(item.get("name"))
        brand = item.get("brand") or (name.split()[0] if name else "")
        ingredients = item.get("ingredients_raw") or ""
        product_url = item.get("product_url")

        print(f"Inserting {i+1}: {name}")

        cur.execute("""
            INSERT INTO products
            (name, brand, category, ingredients, price, image_url)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            name,
            brand,
            "unknown",
            ingredients,
            0,
            product_url
        ))

    conn.commit()
    conn.close()
    print("✅ Seed completed successfully!")


if __name__ == "__main__":
    try:
        seed()
    except Exception as e:
        print("ERROR:", e)
