from psycopg2.extras import RealDictCursor
from .db import get_connection

# =========================
# PRODUCTS
# =========================

def get_all_products():
    conn = get_connection()
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT * FROM products")
        return cur.fetchall()
    finally:
        conn.close()


def get_products_by_price_range(min_price, max_price):
    conn = get_connection()
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute(
            """
            SELECT * FROM products
            WHERE price BETWEEN %s AND %s
            """,
            (min_price, max_price)
        )
        return cur.fetchall()
    finally:
        conn.close()


def insert_product(product_data):
    conn = get_connection()
    try:
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO products
            (name, brand, category, skin_type, ingredients,
                description, price, image_url)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            product_data['name'],
            product_data.get('brand'),
            product_data.get('category'),
            product_data.get('skin_type'),
            product_data.get('ingredients'),
            product_data.get('description'),
            product_data.get('price'),
            product_data.get('image_url')
        ))

        conn.commit()
        return True

    except Exception as e:
        print("❌ Insert Product Error:", e)
        return False

    finally:
        conn.close()
