from psycopg2.extras import RealDictCursor
from .db import get_connection


def get_all_products():
    conn = get_connection()
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT * FROM products")
        return cur.fetchall()
    finally:
        conn.close()


def insert_product(product_data):
    conn = get_connection()
    try:
        cur = conn.cursor()
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
            product_data.get('product_url'),
            product_data.get('name'),
            product_data.get('brand'),
            product_data.get('major_category'),
            product_data.get('subtype'),
            product_data.get('price'),
            product_data.get('rating'),
            product_data.get('rating_count'),
            product_data.get('active_tags'),
            product_data.get('function_tags'),
            product_data.get('ingredients_raw'),
            product_data.get('ingredients_list'),
            product_data.get('image_url'),
            product_data.get('image_local'),
            product_data.get('skintype'),
        ))
        conn.commit()
        return True
    except Exception as e:
        print("Insert Product Error:", e)
        return False
    finally:
        conn.close()