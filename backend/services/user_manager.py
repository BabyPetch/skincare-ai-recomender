import json
import os
from datetime import datetime
from config import USERS_FILE_PATH

class UserManager:
    def __init__(self):
        self._init_db()

    def _init_db(self):
        """สร้างไฟล์ users.json ถ้ายังไม่มี"""
        if not USERS_FILE_PATH.exists():
            USERS_FILE_PATH.parent.mkdir(parents=True, exist_ok=True)
            with open(USERS_FILE_PATH, 'w', encoding='utf-8') as f:
                json.dump([], f)

    def _calculate_age(self, birthdate_str):
        """คำนวณอายุจากวันเกิด"""
        try:
            if not birthdate_str:
                return 0
            birthdate = datetime.strptime(birthdate_str, '%Y-%m-%d')
            today = datetime.today()
            age = today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))
            return age
        except Exception as e:
            print(f"Warning calculating age: {e}")
            return 0 # Default ถ้าคำนวณไม่ได้

    def login(self, email, password):
        try:
            with open(USERS_FILE_PATH, 'r', encoding='utf-8') as f:
                users = json.load(f)
            
            user = next((u for u in users if u['email'] == email and u['password'] == password), None)
            
            if user:
                # คำนวณอายุสดๆ ตอน Login
                user['age'] = self._calculate_age(user.get('birthdate'))
                return True, user
            return False, "อีเมลหรือรหัสผ่านไม่ถูกต้อง"
        except Exception as e:
            print(f"Login Error: {e}")
            return False, str(e)

    def register(self, name, email, password, birthdate):
        try:
            with open(USERS_FILE_PATH, 'r', encoding='utf-8') as f:
                users = json.load(f)

            if any(u['email'] == email for u in users):
                return False, "อีเมลนี้ถูกใช้งานแล้ว"

            new_user = {
                "name": name,
                "email": email,
                "password": password,
                "birthdate": birthdate,
                "role": "user",
                "history": [] # สร้าง list ว่างรอไว้เลย
            }
            users.append(new_user)
            
            with open(USERS_FILE_PATH, 'w', encoding='utf-8') as f:
                json.dump(users, f, indent=4, ensure_ascii=False)
            
            return True, "สมัครสมาชิกสำเร็จ"
        except Exception as e:
            print(f"Register Error: {e}")
            return False, str(e)

    def get_all_users(self):
        """คืนค่ารายชื่อสมาชิกทั้งหมด"""
        try:
            with open(USERS_FILE_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return []

    def delete_user(self, email):
        """ลบสมาชิกตามอีเมล"""
        try:
            with open(USERS_FILE_PATH, 'r', encoding='utf-8') as f:
                users = json.load(f)
            
            new_users = [u for u in users if u['email'] != email]
            
            if len(users) == len(new_users):
                return False, "ไม่พบอีเมลนี้ในระบบ"

            with open(USERS_FILE_PATH, 'w', encoding='utf-8') as f:
                json.dump(new_users, f, indent=4, ensure_ascii=False)
            
            return True, "ลบสมาชิกสำเร็จ"
        except Exception as e:
            return False, str(e)

    def add_history(self, email, skin_type, concerns, results):
        """บันทึกผลการวิเคราะห์ลงในประวัติของผู้ใช้"""
        print(f"💾 Saving history for: {email}") # Log ดูว่าทำงานไหม
        try:
            with open(USERS_FILE_PATH, 'r', encoding='utf-8') as f:
                users = json.load(f)
            
            found = False
            for user in users:
                if user['email'] == email:
                    if 'history' not in user:
                        user['history'] = []
                    
                    record = {
                        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "skin_type": skin_type,
                        "concerns": concerns,
                        "results": results
                    }
                    
                    # เพิ่มรายการใหม่ไว้บนสุด
                    user['history'].insert(0, record)
                    # เก็บแค่ 5 รายการล่าสุด
                    user['history'] = user['history'][:5]
                    found = True
                    break
            
            if found:
                with open(USERS_FILE_PATH, 'w', encoding='utf-8') as f:
                    json.dump(users, f, indent=4, ensure_ascii=False)
                print("✅ History saved successfully")
                return True, "บันทึกประวัติเรียบร้อย"
            else:
                print(f"❌ User email not found: {email}")
                return False, "User not found"

        except Exception as e:
            print(f"❌ Error saving history: {e}") # Error จะโชว์ใน Terminal (จอดำ)
            return False, str(e)