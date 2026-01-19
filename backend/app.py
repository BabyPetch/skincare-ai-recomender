from flask import Flask, request, jsonify
from flask_cors import CORS
from services.ai_engine import SkincareAI
from services.user_manager import UserManager  # 👈 นำเข้า UserManager ที่คุณให้มา
import os

app = Flask(__name__)
CORS(app)

# 1. โหลด AI
try:
    print("⏳ Starting AI Engine...")
    ai = SkincareAI()
    print("✅ AI Engine Started Successfully!")
except Exception as e:
    print(f"❌ Failed to start AI: {e}")
    ai = None

# 2. โหลด UserManager (ระบบจัดการสมาชิกที่บันทึกลงไฟล์)
try:
    user_manager = UserManager()
    print("✅ User Manager Loaded!")
except Exception as e:
    print(f"❌ Failed to load User Manager: {e}")
    user_manager = None

# --- 🔑 ส่วน Login (ใช้ user_manager.py) ---
@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.json
        email = data.get('email')
        password = data.get('password')

        print(f"🔑 Login Attempt: {email}")

        if not user_manager:
            return jsonify({'error': 'Server Error: UserManager not loaded'}), 500

        # เรียกใช้ฟังก์ชัน login ใน user_manager.py
        success, result = user_manager.login(email, password)

        if success:
            # result คือ object user ที่ได้มาจากไฟล์ (มีทั้ง age, birthdate, role ครบ)
            return jsonify({
                'message': 'Login successful',
                'user': result 
            }), 200
        else:
            # result คือข้อความ error
            return jsonify({'error': result}), 401

    except Exception as e:
        print(f"❌ Login Error: {e}")
        return jsonify({'error': str(e)}), 500

# --- 📝 ส่วน Register (ใช้ user_manager.py) ---
@app.route('/api/register', methods=['POST'])
def register():
    try:
        data = request.json
        
        # ดึงข้อมูลจาก Frontend
        name = data.get('name')
        email = data.get('email')
        password = data.get('password')
        birthdate = data.get('birthdate') # ส่งมาเป็น 'YYYY-MM-DD'

        if not user_manager:
            return jsonify({'error': 'Server Error: UserManager not loaded'}), 500

        # เรียกใช้ฟังก์ชัน register ใน user_manager.py
        success, message = user_manager.register(name, email, password, birthdate)

        if success:
            return jsonify({'message': message}), 201
        else:
            return jsonify({'error': message}), 400

    except Exception as e:
        print(f"❌ Register Error: {e}")
        return jsonify({'error': str(e)}), 500
    
    
    # --- 👑 ส่วน Admin API ---
@app.route('/api/admin/users', methods=['GET'])
def get_all_users():
    # ในงานจริงต้องเช็ค Token ว่าเป็น Admin ไหม แต่นี้เราข้ามไปก่อน
    users = user_manager.get_all_users()
    return jsonify(users), 200

@app.route('/api/admin/users/<string:email>', methods=['DELETE'])
def delete_user(email):
    success, message = user_manager.delete_user(email)
    if success:
        return jsonify({'message': message}), 200
    else:
        return jsonify({'error': message}), 400

# --- ✨ ส่วน AI Recommender (อันเดิม) ---
# แก้ไข route /api/recommend

@app.route('/api/recommend', methods=['POST'])
def recommend():
    try:
        data = request.json  # ใช้ json อย่างเดียวเพื่อง่าย
        # หรือถ้าใช้ FormData ต้องแก้ frontend ให้ส่ง email มาด้วย
        
        # รับข้อมูล
        skin_type = data.get('skin_type')
        concerns = data.get('concerns') # รับมาเป็น string "สิว,ริ้วรอย" หรือ list
        if isinstance(concerns, str):
            concerns = concerns.split(',')
            
        age = data.get('age', 25)
        email = data.get('email') # 👈 เพิ่มรับ Email

        print(f"📩 AI Request: Skin={skin_type}, Concerns={concerns}, Email={email}")

        if ai:
            # 1. ให้ AI คิด
            recommendations = ai.recommend(skin_type, concerns, age)
            
            # 2. ถ้ามี email ส่งมา ให้บันทึกลง History
            if email and user_manager:
                user_manager.add_history(email, skin_type, concerns, recommendations)
                print(f"✅ Saved history for {email}")

            return jsonify(recommendations)
        else:
            return jsonify({'error': 'AI Engine not loaded'}), 500

    except Exception as e:
        print(f"❌ Error: {e}")
        return jsonify({'error': str(e)}), 500
    
# --- เพิ่ม API นี้ลงไปใน app.py ---
@app.route('/api/user/<email>', methods=['GET'])
def get_user_latest(email):
    """ดึงข้อมูลผู้ใช้ล่าสุด (รวมถึง History ที่เพิ่งเพิ่ม)"""
    users = user_manager.get_all_users()
    user = next((u for u in users if u['email'] == email), None)
    
    if user:
        # คำนวณอายุใหม่ด้วย เผื่อข้ามปี
        user['age'] = user_manager._calculate_age(user.get('birthdate'))
        return jsonify(user)
    return jsonify({"error": "User not found"}), 404

if __name__ == '__main__':
    print("🚀 Server is running on http://127.0.0.1:5000")
    app.run(debug=True, port=5000)