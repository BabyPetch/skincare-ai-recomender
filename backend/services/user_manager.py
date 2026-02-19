from database.db import get_connection
from psycopg2.extras import RealDictCursor
from datetime import datetime
import json


class UserManager:

    # =========================
    # LOGIN
    # =========================
    def login(self, email, password):
        conn = get_connection()
        try:
            cur = conn.cursor(cursor_factory=RealDictCursor)

            cur.execute(
                "SELECT * FROM users WHERE email = %s AND password = %s",
                (email, password)
            )

            user = cur.fetchone()

            if user:
                user['age'] = self._calculate_age(user.get('birthdate'))

                if user.get('birthdate'):
                    user['birthdate'] = str(user['birthdate'])

                return True, user

            return False, "อีเมลหรือรหัสผ่านไม่ถูกต้อง"

        finally:
            conn.close()

    # =========================
    # REGISTER
    # =========================
    def register(self, name, email, password, birthdate):
        conn = get_connection()
        try:
            cur = conn.cursor()

            cur.execute(
                "INSERT INTO users (name, email, password, birthdate) VALUES (%s, %s, %s, %s)",
                (name, email, password, birthdate)
            )

            conn.commit()
            return True, "สมัครสมาชิกสำเร็จ"

        except Exception as e:
            return False, str(e)

        finally:
            conn.close()

    # =========================
    # ADD HISTORY (JSONB)
    # =========================
    def add_history(self, email, skin_type, concerns, results):
        conn = get_connection()

        try:
            cur = conn.cursor()

            query = """
                INSERT INTO history (user_email, skin_type, concerns, recommended_products)
                VALUES (%s, %s, %s, %s)
            """

            concerns_json = json.dumps(concerns, ensure_ascii=False)
            results_json = json.dumps(results, ensure_ascii=False)

            cur.execute(query, (email, skin_type, concerns_json, results_json))

            conn.commit()

        except Exception as e:
            print(f"❌ Failed to save history: {e}")

        finally:
            conn.close()

    # =========================
    # GET USER + HISTORY
    # =========================
    def get_user_with_history(self, email):
        conn = get_connection()

        try:
            cur = conn.cursor(cursor_factory=RealDictCursor)

            cur.execute("SELECT * FROM users WHERE email = %s", (email,))
            user = cur.fetchone()

            if not user:
                return None

            if user.get('birthdate'):
                user['birthdate'] = str(user['birthdate'])

            user['age'] = self._calculate_age(user.get('birthdate'))

            cur.execute("""
                SELECT * FROM history
                WHERE user_email = %s
                ORDER BY timestamp DESC
                LIMIT 10
            """, (email,))

            history = cur.fetchall()

            formatted_history = []

            for h in history:
                formatted_history.append({
                    "date": str(h['timestamp']) if h.get('timestamp') else "",
                    "skin_type": h.get('skin_type'),
                    "concerns": h.get('concerns', []),
                    "results": h.get('recommended_products', [])
                })

            user['history'] = formatted_history

            return user

        finally:
            conn.close()

    # =========================
    # GET ALL USERS
    # =========================
    def get_all_users(self):
        conn = get_connection()

        try:
            cur = conn.cursor(cursor_factory=RealDictCursor)
            cur.execute("SELECT id, email, name, role, birthdate, created_at FROM users ORDER BY id ASC")

            users = cur.fetchall()

            for user in users:
                if user.get('birthdate'):
                    user['birthdate'] = str(user['birthdate'])

            return users

        finally:
            conn.close()

    # =========================
    # DELETE USER
    # =========================
    def delete_user(self, email):
        conn = get_connection()

        try:
            cur = conn.cursor()
            cur.execute("DELETE FROM users WHERE email = %s", (email,))

            if cur.rowcount == 0:
                return False, "ไม่พบอีเมลนี้ในระบบ"

            conn.commit()
            return True, "ลบสมาชิกสำเร็จ"

        finally:
            conn.close()

    # =========================
    # CALCULATE AGE
    # =========================
    def _calculate_age(self, birthdate):
        if not birthdate:
            return 0

        try:
            if isinstance(birthdate, str):
                birth = datetime.strptime(birthdate, "%Y-%m-%d")
            else:
                birth = datetime.combine(birthdate, datetime.min.time())

            today = datetime.today()

            return today.year - birth.year - (
                (today.month, today.day) < (birth.month, birth.day)
            )

        except:
            return 0
