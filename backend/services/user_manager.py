from database.db import get_connection
from psycopg2.extras import RealDictCursor
from datetime import datetime
import json


class UserManager:

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

    def register(self, name, email, password, birthdate, gender='other'):
        conn = get_connection()
        try:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO users (name, email, password, birthdate, gender) VALUES (%s, %s, %s, %s, %s)",
                (name, email, password, birthdate, gender)
            )
            conn.commit()
            return True, "สมัครสมาชิกสำเร็จ"
        except Exception as e:
            return False, str(e)
        finally:
            conn.close()

    def add_history(self, email, skin_type, concerns, recommend_results, routine_results=None):
        conn = get_connection()
        try:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO history
                    (user_email, skin_type, concerns, recommended_products, routine_products, history_type)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                email,
                skin_type,
                json.dumps(concerns, ensure_ascii=False),
                json.dumps(recommend_results, ensure_ascii=False),
                json.dumps(routine_results, ensure_ascii=False) if routine_results else None,
                'both' if routine_results else 'recommend',
            ))
            conn.commit()
        except Exception as e:
            print(f"❌ Failed to save history: {e}")
        finally:
            conn.close()

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
            user['history'] = [
                {
                    "date":         str(h['timestamp']) if h.get('timestamp') else "",
                    "skin_type":    h.get('skin_type'),
                    "concerns":     h.get('concerns', []),
                    "results":      h.get('recommended_products', []),
                    "routine":      h.get('routine_products', []),
                    "history_type": h.get('history_type', 'recommend'),
                }
                for h in history
            ]
            return user
        finally:
            conn.close()

    def get_all_users(self):
        conn = get_connection()
        try:
            cur = conn.cursor(cursor_factory=RealDictCursor)
            cur.execute(
                "SELECT id, email, name, role, birthdate, gender, created_at FROM users ORDER BY id ASC"
            )
            users = cur.fetchall()
            for user in users:
                if user.get('birthdate'):
                    user['birthdate'] = str(user['birthdate'])
            return users
        finally:
            conn.close()

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