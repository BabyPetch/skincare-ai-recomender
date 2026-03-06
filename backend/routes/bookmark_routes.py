from flask import Blueprint, request, jsonify
from database.db import get_connection
from psycopg2.extras import RealDictCursor

bookmark_bp = Blueprint("bookmark", __name__)


@bookmark_bp.route('/api/bookmark', methods=['POST'])
def toggle_bookmark():
    """เพิ่ม หรือ ลบ bookmark (toggle)"""
    data       = request.json
    email      = data.get('email')
    product    = data.get('product')

    if not email or not product:
        return jsonify({"error": "missing email or product"}), 400

    conn = get_connection()
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)

        # เช็คว่ามีอยู่แล้วไหม
        cur.execute(
            "SELECT id FROM bookmarks WHERE user_email = %s AND product_name = %s",
            (email, product.get('name'))
        )
        existing = cur.fetchone()

        if existing:
            # ลบออก
            cur.execute(
                "DELETE FROM bookmarks WHERE user_email = %s AND product_name = %s",
                (email, product.get('name'))
            )
            conn.commit()
            return jsonify({"status": "removed"})
        else:
            # เพิ่มใหม่
            cur.execute("""
                INSERT INTO bookmarks
                    (user_email, product_name, brand, major_category, skintype, function_tags, image_url, price)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (user_email, product_name) DO NOTHING
            """, (
                email,
                product.get('name'),
                product.get('brand'),
                product.get('major_category'),
                product.get('skintype'),
                product.get('function_tags'),
                product.get('image_url'),
                product.get('price') or 0,
            ))
            conn.commit()
            return jsonify({"status": "added"})

    except Exception as e:
        print(f"❌ Bookmark error: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()


@bookmark_bp.route('/api/bookmarks/<email>', methods=['GET'])
def get_bookmarks(email):
    """ดึง bookmarks ทั้งหมดของ user"""
    conn = get_connection()
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("""
            SELECT * FROM bookmarks
            WHERE user_email = %s
            ORDER BY created_at DESC
        """, (email,))
        rows = cur.fetchall()
        result = []
        for r in rows:
            result.append({
                "name":           r['product_name'],
                "brand":          r['brand'],
                "major_category": r['major_category'],
                "skintype":       r['skintype'],
                "function_tags":  r['function_tags'],
                "image_url":      r['image_url'],
                "price":          r['price'],
                "saved_at":       str(r['created_at']),
            })
        return jsonify(result)
    finally:
        conn.close()


@bookmark_bp.route('/api/bookmarks/check', methods=['POST'])
def check_bookmarks():
    """เช็คว่าสินค้าไหนบ้างที่ user บันทึกไว้แล้ว (ส่งชื่อสินค้าหลายตัวพร้อมกัน)"""
    data   = request.json
    email  = data.get('email')
    names  = data.get('names', [])

    if not email or not names:
        return jsonify([])

    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT product_name FROM bookmarks WHERE user_email = %s AND product_name = ANY(%s)",
            (email, names)
        )
        saved = [row[0] for row in cur.fetchall()]
        return jsonify(saved)
    finally:
        conn.close()