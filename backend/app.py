# -*- coding: utf-8 -*-
from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
from pathlib import Path
import sys
import io
import json

# ตั้งค่า Encoding
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

app = Flask(__name__)
CORS(app)

# --- CONFIGURATION ---
BASE_DIR = Path(__file__).parent
DATA_FILE_PATH = BASE_DIR / 'data' / 'Data_Collection_ASA - data.csv'
USERS_FILE_PATH = BASE_DIR / 'data' / 'users.json'

# --- AI CONFIGURATION ---
ROUTINE_MAP = {
    "cleanser": 1, "toner": 2, "serum": 3, "essence": 3,
    "moisturizer": 4, "cream": 4, "sunscreen": 5
}

# --- HELPER FUNCTIONS ---
def get_routine_step(product_type):
    """ระบุลำดับขั้นตอนการทา"""
    pt_lower = str(product_type).lower()
    for key, step in ROUTINE_MAP.items():
        if key in pt_lower: return step
    return 6

def generate_ai_insight(row, concerns):
    """สร้างคำอธิบาย AI"""
    props = str(row.get('คุณสมบัติ(จากactive ingredients)', '')).lower()
    matched = [c for c in concerns if c.lower() in props]
    if matched:
        return f"✨ AI แนะนำ: จัดการปัญหา '{', '.join(matched)}' ได้ตรงจุด"
    return "💡 AI แนะนำ: สูตรอ่อนโยน ช่วยบำรุงผิวพื้นฐานให้แข็งแรง"

def calculate_advanced_scores(df, skin_type, concerns, age=25):
    """
    ฟังก์ชันคำนวณคะแนนขั้นสูง (Logic เต็มรูปแบบ)
    1. Skin Type (30%)
    2. Concerns (35%)
    3. Age Appropriateness (15%)
    4. Price Value (20%)
    """
    if df.empty: return df
    scored_df = df.copy()

    # 1. Skin Type Match (30 คะแนน)
    def skin_score(row_skintype):
        if pd.isna(row_skintype): return 0
        st_str = str(row_skintype).lower()
        if skin_type.lower() in st_str: return 30
        if 'all' in st_str or 'ทุกสภาพผิว' in st_str: return 15
        return 0
    scored_df['skin_score'] = scored_df['skintype'].apply(skin_score)

    # 2. Concerns Match (35 คะแนน)
    def concern_score(row_props):
        if pd.isna(row_props) or not concerns: return 0
        props_lower = row_props.lower()
        matched = sum(1 for c in concerns if c.lower() in props_lower)
        # บัญญัติไตรยางศ์: ตรงกี่ข้อ คิดเป็นสัดส่วนเต็ม 35
        return (matched / len(concerns)) * 35
    scored_df['concern_score'] = scored_df['คุณสมบัติ(จากactive ingredients)'].apply(concern_score)

    # 3. Age Match (15 คะแนน)
    def age_score(row_props):
        if pd.isna(row_props): return 7
        props_lower = row_props.lower()
        # Logic แยกช่วงอายุ
        if age < 25 and 'ป้องกัน' in props_lower: return 15
        if 25 <= age < 35 and ('ริ้วรอย' in props_lower or 'กระจ่างใส' in props_lower): return 15
        if age >= 35 and ('ลดเลือน' in props_lower or 'ยกกระชับ' in props_lower): return 15
        return 7
    scored_df['age_score'] = scored_df['คุณสมบัติ(จากactive ingredients)'].apply(age_score)

    # 4. Price Score (20 คะแนน) - ยิ่งถูกยิ่งคะแนนเยอะ (Normalized)
    min_p = scored_df['price (bath)'].min()
    max_p = scored_df['price (bath)'].max()
    if max_p > min_p:
        scored_df['price_score'] = 20 * (1 - ((scored_df['price (bath)'] - min_p) / (max_p - min_p)))
    else:
        scored_df['price_score'] = 20 # ถ้าราคาเท่ากันหมด
    
    # รวมคะแนน
    scored_df['total_score'] = (
        scored_df['skin_score'] + 
        scored_df['concern_score'] + 
        scored_df['age_score'] + 
        scored_df['price_score']
    )
    return scored_df

# --- LOAD DATA ---
try:
    products_df = pd.read_csv(DATA_FILE_PATH, encoding='utf-8-sig')
    products_df['price (bath)'] = pd.to_numeric(products_df['price (bath)'].astype(str).str.replace(',', ''), errors='coerce')
    print(f"✅ Database Loaded: {len(products_df)} items")
except Exception as e:
    print(f"❌ Database Error: {e}")
    products_df = None

# --- API ENDPOINTS ---
@app.route('/api/recommend', methods=['POST'])
def recommend_api():
    if products_df is None:
        return jsonify({'success': False, 'message': 'Database error'}), 500
    
    try:
        data = request.json
        skin_type = data.get('skinType', 'All')
        concerns = data.get('concerns', [])
        age = data.get('age', 25) # ค่า Default อายุ 25 ถ้าไม่ได้ส่งมา

        # 1. Filter เบื้องต้น (กรองตามสภาพผิว)
        df = products_df.copy()
        if skin_type and skin_type != 'All':
            # กรองแบบหลวมๆ (Loose Filter) ให้เหลือเฉพาะที่ผิวใช้ได้
            df = df[df['skintype'].fillna('').str.contains(skin_type, case=False) | 
                   df['skintype'].fillna('').str.contains('All', case=False) |
                   df['skintype'].fillna('').str.contains('ทุกสภาพผิว', case=False)]

        # 2. คำนวณคะแนนละเอียด (Advanced Scoring)
        scored_df = calculate_advanced_scores(df, skin_type, concerns, age)

        # 3. เลือก Top 5
        results = scored_df.sort_values('total_score', ascending=False).head(5)

        recommendations = []
        for _, row in results.iterrows():
            recommendations.append({
                'id': int(row.get('id', 0)),
                'name': str(row.get('name', '')),
                'brand': str(row.get('brand', '')),
                'type': str(row.get('type_of_product', '')),
                'price': float(row.get('price (bath)', 0)),
                'score': int(row.get('total_score', 0)),
                'ai_insight': generate_ai_insight(row, concerns),
                'routine_step': get_routine_step(row.get('type_of_product', ''))
            })
        
        # จัดลำดับการทา 1 -> 5
        recommendations.sort(key=lambda x: x['routine_step'])
        
        return jsonify({'success': True, 'recommendations': recommendations})

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

# --- USER SYSTEM ---
def init_users():
    if not USERS_FILE_PATH.exists():
        USERS_FILE_PATH.parent.mkdir(exist_ok=True)
        with open(USERS_FILE_PATH, 'w', encoding='utf-8') as f: json.dump([], f)

@app.route('/api/login', methods=['POST'])
def login():
    init_users()
    data = request.json
    try:
        users = json.load(open(USERS_FILE_PATH, 'r', encoding='utf-8'))
        user = next((u for u in users if u['email'] == data['email'] and u['password'] == data['password']), None)
        if user: return jsonify({"success": True, "user": user})
        return jsonify({"success": False, "message": "Login Failed"}), 401
    except: return jsonify({"success": False, "message": "Error"}), 500

@app.route('/api/register', methods=['POST'])
def register():
    init_users()
    data = request.json
    try:
        users = json.load(open(USERS_FILE_PATH, 'r', encoding='utf-8'))
        users.append({"name": data['name'], "email": data['email'], "password": data['password'], "role": "user"})
        json.dump(users, open(USERS_FILE_PATH, 'w', encoding='utf-8'), indent=4, ensure_ascii=False)
        return jsonify({"success": True})
    except Exception as e: return jsonify({"success": False, "message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)