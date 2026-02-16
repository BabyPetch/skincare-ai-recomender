import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
import json
import os

class UserManager:
    def __init__(self):
        self.db_config = {
            "dbname": "skincareCollectionDB",
            "user": "postgres",
            "password": "1234",
            "host": "127.0.0.1",
            "port": "5432"
        }
        self._init_user_table()

    def get_db_connection(self):
        try:
            return psycopg2.connect(**self.db_config)
        except Exception as e:
            print(f"❌ DB Connection Error: {e}")
            return None

    def _init_user_table(self):
        """สร้างตารางและอัปเดต Schema รวมถึงสร้าง Admin อัตโนมัติ"""
        conn = self.get_db_connection()
        if conn:
            try:
                cur = conn.cursor()
                # 1. สร้างตาราง Users 
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        id SERIAL PRIMARY KEY,
                        email VARCHAR(255) UNIQUE NOT NULL,
                        password VARCHAR(255) NOT NULL,
                        name VARCHAR(255),
                        role VARCHAR(20) DEFAULT 'user',
                        birthdate DATE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                """)
                
                # ตรวจสอบและเพิ่มคอลัมน์ role สำหรับ DB เก่า
                cur.execute("""
                    DO $$ 
                    BEGIN 
                        IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                                       WHERE table_name='users' AND column_name='role') THEN
                            ALTER TABLE users ADD COLUMN role VARCHAR(20) DEFAULT 'user';
                        END IF;
                    END $$;
                """)

                # 2. ตาราง History
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS history (
                        id SERIAL PRIMARY KEY,
                        user_email VARCHAR(255),
                        skin_type VARCHAR(50),
                        concerns TEXT,
                        recommended_products JSONB,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                """)
                
                # 👑 3. สร้างบัญชี Admin อัตโนมัติถ้ายังไม่มี
                cur.execute("SELECT COUNT(*) FROM users WHERE role = 'admin'")
                admin_count = cur.fetchone()[0]
                
                if admin_count == 0:
                    cur.execute("""
                        INSERT INTO users (email, password, name, role) 
                        VALUES ('admin@admin.com', '1234', 'System Admin', 'admin')
                        ON CONFLICT (email) DO NOTHING;
                    """)
                    print("👑 Default Admin created -> Email: admin@admin.com | Pass: 1234")

                conn.commit()
                print("✅ Database Schema Checked/Updated.")
            except Exception as e:
                print(f"❌ Error updating schema: {e}")
            finally:
                cur.close()
                conn.close()

    # 👇 ฟังก์ชัน Login ที่หายไป กลับมาแล้ว!
    def login(self, email, password):
        conn = self.get_db_connection()
        if not conn: return False, "Database Error"
        try:
            cur = conn.cursor(cursor_factory=RealDictCursor)
            cur.execute("SELECT id, email, name, role, birthdate FROM users WHERE email = %s AND password = %s", (email, password))
            user = cur.fetchone()
            
            if user:
                user['age'] = self._calculate_age(user.get('birthdate'))
                if user.get('birthdate'): user['birthdate'] = str(user['birthdate'])
                return True, user
            return False, "อีเมลหรือรหัสผ่านไม่ถูกต้อง"
        except Exception as e:
            return False, str(e)
        finally:
            cur.close()
            conn.close()

    # 👇 ฟังก์ชัน Register เผื่อว่าหายไปด้วย
    def register(self, name, email, password, birthdate):
        conn = self.get_db_connection()
        if not conn: return False, "Database Error"
        try:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO users (name, email, password, birthdate) VALUES (%s, %s, %s, %s)",
                (name, email, password, birthdate)
            )
            conn.commit()
            return True, "สมัครสมาชิกสำเร็จ"
        except psycopg2.IntegrityError:
            return False, "อีเมลนี้มีผู้ใช้งานแล้ว"
        except Exception as e:
            return False, str(e)
        finally:
            cur.close()
            conn.close()

    def add_history(self, email, skin_type, concerns, results):
        conn = self.get_db_connection()
        if not conn: return
        try:
            cur = conn.cursor()
            query = """
                INSERT INTO history (user_email, skin_type, concerns, recommended_products)
                VALUES (%s, %s, %s, %s)
            """
            concerns_str = ", ".join(concerns) if isinstance(concerns, list) else concerns
            results_json = json.dumps(results, ensure_ascii=False)
            cur.execute(query, (email, skin_type, concerns_str, results_json))
            conn.commit()
            print(f"💾 History saved for {email}")
        except Exception as e:
            print(f"❌ Failed to save history: {e}")
        finally:
            cur.close()
            conn.close()

    def get_user_with_history(self, email):
        conn = self.get_db_connection()
        if not conn: return None
        try:
            cur = conn.cursor(cursor_factory=RealDictCursor)
            
            cur.execute("SELECT * FROM users WHERE email = %s", (email,))
            user = cur.fetchone()
            
            if user:
                if user.get('birthdate'): user['birthdate'] = str(user['birthdate'])
                if user.get('created_at'): user['created_at'] = str(user['created_at'])
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
                    c_raw = h.get('concerns', '')
                    c_list = c_raw.split(', ') if c_raw else []

                    formatted_history.append({
                        "date": str(h['timestamp']) if h.get('timestamp') else "",
                        "skin_type": h.get('skin_type', 'Unknown'),
                        "concerns": c_list,
                        "results": h.get('recommended_products', [])
                    })
                
                user['history'] = formatted_history 
                return user
            return None
        except Exception as e:
            print(f"❌ Error fetching user history: {e}")
            return None
        finally:
            conn.close()

    def get_all_users(self):
        conn = self.get_db_connection()
        if not conn: return []
        try:
            cur = conn.cursor(cursor_factory=RealDictCursor)
            cur.execute("SELECT id, email, name, role, birthdate, created_at FROM users ORDER BY id ASC")
            users = cur.fetchall()
            for user in users:
                if user.get('birthdate'): user['birthdate'] = str(user['birthdate'])
                if user.get('created_at'): user['created_at'] = str(user['created_at'])
            return users
        except Exception:
            return []
        finally:
            conn.close()

    def delete_user(self, email):
        conn = self.get_db_connection()
        if not conn: return False, "DB Error"
        try:
            cur = conn.cursor()
            cur.execute("DELETE FROM users WHERE email = %s", (email,))
            if cur.rowcount == 0:
                return False, "ไม่พบอีเมลนี้ในระบบ"
            conn.commit()
            return True, "ลบสมาชิกสำเร็จ"
        except Exception as e:
            return False, str(e)
        finally:
            conn.close()

    def _calculate_age(self, birthdate):
        if not birthdate: return 0
        try:
            if isinstance(birthdate, str):
                birth = datetime.strptime(birthdate, "%Y-%m-%d")
            else:
                birth = datetime.combine(birthdate, datetime.min.time())
            today = datetime.today()
            return today.year - birth.year - ((today.month, today.day) < (birth.month, birth.day))
        except:
            return 0