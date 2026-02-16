from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import os
from datetime import datetime

# ✅ เรียกจากโฟลเดอร์ services ให้ถูกต้อง
from services.ai_engine import SkincareAI
from services.user_manager import UserManager

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

# 2. โหลด UserManager
try:
    user_manager = UserManager()
    print("✅ User Manager Loaded!")
except Exception as e:
    print(f"❌ Failed to load User Manager: {e}")
    user_manager = None

# ---  ส่วน Login / Register ---
@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.json
        print("📥 ข้อมูลที่ได้รับจาก React:", data) # เช็คว่า React ส่งข้อมูลมาไหม
        
        # ป้องกันกรณี React ไม่ได้ส่งข้อมูลเป็น JSON
        if not data:
            print("❌ Error: ไม่มีข้อมูลถูกส่งมา หรือลืมตั้งค่า Content-Type ใน React")
            return jsonify({'error': 'Invalid request format'}), 400
            
        email = data.get('email')
        password = data.get('password')
        
        if not user_manager: 
            return jsonify({'error': 'Server Error (DB Manager not loaded)'}), 500
            
        success, result = user_manager.login(email, password)
        if success: 
            return jsonify({'message': 'Login successful', 'user': result}), 200
        return jsonify({'error': result}), 401
        
    except Exception as e: 
        print(f"💥 เกิด Error ตอน Login: {e}") # ✅ บรรทัดนี้จะช่วยบอกว่าโค้ดพังตรงไหน
        return jsonify({'error': str(e)}), 500
    
@app.route('/api/register', methods=['POST'])
def register():
    try:
        data = request.json
        success, message = user_manager.register(data.get('name'), data.get('email'), data.get('password'), data.get('birthdate'))
        if success: return jsonify({'message': message}), 201
        return jsonify({'error': message}), 400
    except Exception as e: return jsonify({'error': str(e)}), 500

# --- 👑 ส่วน Admin (เช็ค DB ป้องกัน Error) ---
@app.route('/api/admin/users', methods=['GET'])
def get_all_users():
    if not user_manager: return jsonify({'error': 'Server Error'}), 500
    users = user_manager.get_all_users()
    return jsonify(users), 200

@app.route('/api/admin/users/<string:email>', methods=['DELETE'])
def delete_user(email):
    if not user_manager: return jsonify({'error': 'Server Error'}), 500
    success, message = user_manager.delete_user(email)
    return jsonify({'message' if success else 'error': message}), 200 if success else 400

# --- ✨ ส่วน AI Recommender ---
@app.route('/api/recommend', methods=['POST'])
def recommend():
    try:
        data = request.json
        skin_type = data.get('skin_type', 'all')
        concerns = data.get('concerns', [])
        price_key = data.get('price_range', 'any') # รับค่า low, medium, high, any
        email = data.get('email')

        # 🎯 แปลงคำศัพท์ (low, medium, high) ให้เป็นตัวเลขจริง
        if price_key == 'low':
            min_p, max_p = 0, 500
        elif price_key == 'medium':
            min_p, max_p = 500, 1500
        elif price_key == 'high':
            min_p, max_p = 1500, 100000
        else:
            min_p, max_p = 0, 100000

        print(f"📩 AI Request: Skin={skin_type}, Price_Key={price_key} ({min_p}-{max_p})")

        if ai:
            # ส่งราคาที่แปลงเป็นตัวเลขแล้วไปให้ AI
            recommendations = ai.recommend_products(
                skin_type=skin_type, 
                concerns=concerns, 
                min_price=min_p, 
                max_price=max_p
            )
            
            if email and user_manager:
                user_manager.add_history(email, skin_type, concerns, recommendations)

            return jsonify(recommendations)
        
        return jsonify({'error': 'AI Engine not loaded'}), 500

    except Exception as e:
        print(f"❌ Error: {e}")
        return jsonify({'error': str(e)}), 500
    
# --- 👤 ส่วน User Profile ---
@app.route('/api/user/<email>', methods=['GET'])
def get_user_profile(email):
    # ✅ เรียกใช้ get_user_with_history แทนการดึงแบบธรรมดา
    if user_manager:
        user = user_manager.get_user_with_history(email)
        if user:
            return jsonify(user)
    return jsonify({"error": "User not found"}), 404

if __name__ == '__main__':
    print("🚀 Server is running on http://127.0.0.1:5000")
    app.run(debug=True, port=5000)