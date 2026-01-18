import json
from datetime import datetime
from config import USERS_FILE_PATH

class UserManager:
    def __init__(self):
        self._init_db()

    def _init_db(self):
        if not USERS_FILE_PATH.exists():
            USERS_FILE_PATH.parent.mkdir(exist_ok=True)
            with open(USERS_FILE_PATH, 'w', encoding='utf-8') as f:
                json.dump([], f)

    def _calculate_age(self, birthdate_str):
        try:
            birthdate = datetime.strptime(birthdate_str, '%Y-%m-%d')
            today = datetime.today()
            age = today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))
            return age
        except:
            return 20 # Default

    def login(self, email, password):
        try:
            users = json.load(open(USERS_FILE_PATH, 'r', encoding='utf-8'))
            user = next((u for u in users if u['email'] == email and u['password'] == password), None)
            
            if user:
                # คำนวณอายุสดๆ ตอน Login แล้วส่งกลับไป
                user['age'] = self._calculate_age(user.get('birthdate', '2000-01-01'))
                return True, user
            return False, "อีเมลหรือรหัสผ่านไม่ถูกต้อง"
        except Exception as e:
            return False, str(e)

    def register(self, name, email, password, birthdate):
        try:
            users = json.load(open(USERS_FILE_PATH, 'r', encoding='utf-8'))
            if any(u['email'] == email for u in users):
                return False, "อีเมลนี้ถูกใช้งานแล้ว"

            new_user = {
                "name": name,
                "email": email,
                "password": password,
                "birthdate": birthdate,
                "role": "user"
            }
            users.append(new_user)
            
            with open(USERS_FILE_PATH, 'w', encoding='utf-8') as f:
                json.dump(users, f, indent=4, ensure_ascii=False)
            
            return True, "สมัครสมาชิกสำเร็จ"
        except Exception as e:
            return False, str(e)