from flask import Blueprint, request, jsonify
from database.db import get_connection
from psycopg2.extras import RealDictCursor

review_bp = Blueprint("review", __name__)


# -------------------------------------------------------
# POST /api/review  — เพิ่ม/แก้ review (upsert)
# -------------------------------------------------------
@review_bp.route('/api/review', methods=['POST'])
def upsert_review():
    data         = request.json
    email        = data.get('email')
    user_name    = data.get('user_name', 'ไม่ระบุชื่อ')
    product_name = data.get('product_name')
    brand        = data.get('brand', '')
    rating       = data.get('rating')
    title        = data.get('title', '')
    body         = data.get('body', '')

    if not email or not product_name or not rating:
        return jsonify({"error": "missing required fields"}), 400
    if not (1 <= int(rating) <= 5):
        return jsonify({"error": "rating must be 1-5"}), 400

    conn = get_connection()
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("""
            INSERT INTO reviews
                (user_email, user_name, product_name, brand, rating, title, body)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (user_email, product_name)
            DO UPDATE SET
                rating     = EXCLUDED.rating,
                title      = EXCLUDED.title,
                body       = EXCLUDED.body,
                user_name  = EXCLUDED.user_name,
                created_at = CURRENT_TIMESTAMP
            RETURNING *
        """, (email, user_name, product_name, brand, int(rating), title, body))
        conn.commit()
        row = cur.fetchone()
        return jsonify({"status": "ok", "review": dict(row)})
    except Exception as e:
        print(f"❌ Review upsert error: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()


# -------------------------------------------------------
# DELETE /api/review  — ลบ review
# -------------------------------------------------------
@review_bp.route('/api/review', methods=['DELETE'])
def delete_review():
    data         = request.json
    email        = data.get('email')
    product_name = data.get('product_name')

    if not email or not product_name:
        return jsonify({"error": "missing fields"}), 400

    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            "DELETE FROM reviews WHERE user_email = %s AND product_name = %s",
            (email, product_name)
        )
        conn.commit()
        return jsonify({"status": "deleted"})
    finally:
        conn.close()


# -------------------------------------------------------
# GET /api/reviews/<product_name>  — ดู review ของสินค้า
# -------------------------------------------------------
@review_bp.route('/api/reviews/<path:product_name>', methods=['GET'])
def get_reviews(product_name):
    conn = get_connection()
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("""
            SELECT user_name, rating, title, body, created_at
            FROM reviews
            WHERE product_name = %s
            ORDER BY created_at DESC
        """, (product_name,))
        rows = cur.fetchall()

        # summary
        ratings = [r['rating'] for r in rows]
        avg     = round(sum(ratings) / len(ratings), 1) if ratings else 0
        dist    = {i: ratings.count(i) for i in range(1, 6)}

        return jsonify({
            "product_name": product_name,
            "total":        len(rows),
            "average":      avg,
            "distribution": dist,
            "reviews":      [dict(r) for r in rows],
        })
    finally:
        conn.close()


# -------------------------------------------------------
# GET /api/reviews/user/<email>  — ดู review ทั้งหมดของ user
# -------------------------------------------------------
@review_bp.route('/api/reviews/user/<email>', methods=['GET'])
def get_user_reviews(email):
    conn = get_connection()
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("""
            SELECT product_name, brand, rating, title, body, created_at
            FROM reviews
            WHERE user_email = %s
            ORDER BY created_at DESC
        """, (email,))
        rows = cur.fetchall()
        return jsonify([dict(r) for r in rows])
    finally:
        conn.close()


# -------------------------------------------------------
# POST /api/reviews/check  — เช็คว่า user รีวิวสินค้านี้ไปแล้วไหม
# -------------------------------------------------------
@review_bp.route('/api/reviews/check', methods=['POST'])
def check_review():
    data         = request.json
    email        = data.get('email')
    product_name = data.get('product_name')

    if not email or not product_name:
        return jsonify(None)

    conn = get_connection()
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("""
            SELECT rating, title, body
            FROM reviews
            WHERE user_email = %s AND product_name = %s
        """, (email, product_name))
        row = cur.fetchone()
        return jsonify(dict(row) if row else None)
    finally:
        conn.close()