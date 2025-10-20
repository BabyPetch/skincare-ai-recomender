# -*- coding: utf-8 -*-
from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
from pathlib import Path
import sys
import io

# ตั้งค่า Encoding ของ Output ให้เป็น UTF-8 (สำคัญสำหรับ Windows)
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# --- CONFIGURATION ---
# ใช้ Pathlib เพื่อให้หาไฟล์เจอเสมอ ไม่ว่าจะรันจากที่ไหนก็ตาม
DATA_FILE_PATH = Path(__file__).parent / 'data' / 'Data_Collection_ASA - data.csv'

# --- APPLICATION SETUP ---
app = Flask(__name__)
CORS(app)  # อนุญาตให้ Frontend (React) เรียก API นี้ได้

# --- DATA LOADING AND PRE-PROCESSING ---
def load_and_prepare_data(path):
    """
    โหลดข้อมูลจากไฟล์ CSV และเตรียมข้อมูลเบื้องต้นเพียงครั้งเดียวตอนเริ่มเซิร์ฟเวอร์
    """
    try:
        df = pd.read_csv(path, encoding='utf-8-sig')
        
        # *** FIX & IMPROVEMENT: แก้ไขการประมวลผลคอลัมน์ราคา ***
        # 1. แปลงคอลัมน์ราคาให้เป็น string เพื่อให้ใช้ .str ได้อย่างปลอดภัย
        # 2. ใช้ .str.replace(',', '') เพื่อลบเครื่องหมายจุลภาคออก
        # 3. แปลงคอลัมน์ที่สะอาดแล้วให้เป็นตัวเลข, ถ้าแปลงไม่ได้จะกลายเป็นค่าว่าง (NaN)
        df['price (bath)'] = pd.to_numeric(df['price (bath)'].astype(str).str.replace(',', ''), errors='coerce')

        print(f"✓ โหลดและเตรียมข้อมูลสำเร็จ: {len(df)} ผลิตภัณฑ์")
        return df
    except Exception as e:
        print(f"✗ เกิดข้อผิดพลาดในการโหลดข้อมูล: {e}")
        return None

# โหลดข้อมูลเก็บไว้ใน memory ตอนเซิร์ฟเวอร์เริ่มทำงาน
products_df = load_and_prepare_data(DATA_FILE_PATH)

# --- HELPER FUNCTIONS FOR FILTERING ---
def filter_by_skintype(df, skin_type):
    if not skin_type:
        return df
    # .contains ครอบคลุมการ match ทั้งแบบบางส่วนและทั้งหมดอยู่แล้ว
    condition = df['skintype'].fillna('').str.contains(skin_type, case=False, na=False)
    return df[condition]

def filter_by_product_type(df, product_type):
    if not product_type or "ทุกประเภท" in product_type:
        return df
    keyword = product_type.split(' ')[0] # เอาแค่คำแรก เช่น "Cleanser"
    condition = df['type_of_product'].fillna('').str.contains(keyword, case=False, na=False)
    return df[condition]

def filter_by_price(df, min_price, max_price):
    """
    *** UPDATED: ฟังก์ชันกรองตามช่วงราคา (min และ max) ***
    """
    filtered_df = df
    if min_price is not None:
        # กรองผลิตภัณฑ์ที่ราคาสูงกว่าหรือเท่ากับ min_price
        filtered_df = filtered_df[filtered_df['price (bath)'] >= min_price]
    if max_price is not None:
        # กรองผลิตภัณฑ์ที่ราคาต่ำกว่าหรือเท่ากับ max_price
        filtered_df = filtered_df[filtered_df['price (bath)'] <= max_price]
    return filtered_df

# --- SCORING LOGIC ---
def calculate_scores(df, skin_type, concerns):
    """
    คำนวณคะแนนผลิตภัณฑ์ตามเกณฑ์ต่างๆ (ระบบคะแนนรวม 100)
    """
    if df.empty:
        return df

    scored_df = df.copy()
    
    # 1. Skin Type Match Score (40 คะแนน)
    # ให้คะแนนสูงถ้าประเภทผิวตรงเป๊ะๆ
    def skin_score(row_skintype):
        if pd.isna(row_skintype): return 0
        # แก้ไขให้รองรับการ split ค่า skintype ที่เป็น list
        skintypes = [s.strip().lower() for s in str(row_skintype).split(',')]
        if skin_type.lower() in skintypes: return 40 # ตรงเป๊ะ
        if any(skin_type.lower() in s for s in skintypes): return 20 # มีคำว่า...
        return 0
    scored_df['skin_score'] = scored_df['skintype'].apply(skin_score)
    
    # 2. Concerns Match Score (40 คะแนน)
    # ยิ่งแก้ปัญหาได้ตรงจุดเยอะ ยิ่งได้คะแนนเยอะ
    def concern_score(row_props):
        score = 0
        if pd.isna(row_props) or not concerns: return 0
        for concern in concerns:
            if concern.lower() in row_props.lower():
                score += 1
        return (score / len(concerns)) * 40 # คิดเป็นสัดส่วนแล้วคูณ 40
    scored_df['concern_score'] = scored_df['คุณสมบัติ(จากactive ingredients)'].apply(concern_score)
    
    # 3. Price Score (20 คะแนน)
    # ยิ่งถูก ยิ่งได้คะแนนเยอะ (เทียบกับผลิตภัณฑ์ที่ผ่านการกรองมาแล้ว)
    min_price_in_set = scored_df['price (bath)'].min()
    max_price_in_set = scored_df['price (bath)'].max()
    if max_price_in_set > min_price_in_set:
        scored_df['price_score'] = (1 - (scored_df['price (bath)'] - min_price_in_set) / (max_price_in_set - min_price_in_set)) * 20
    else:
        scored_df['price_score'] = 20
        
    scored_df['price_score'].fillna(0, inplace=True)

    # รวมคะแนนทั้งหมด
    scored_df['total_score'] = scored_df['skin_score'] + scored_df['concern_score'] + scored_df['price_score']
    return scored_df

# --- API ENDPOINTS ---
@app.route('/api/recommend', methods=['POST'])
def recommend_api():
    if products_df is None:
        return jsonify({'success': False, 'message': 'เกิดข้อผิดพลาด: ไม่สามารถโหลดฐานข้อมูลได้'}), 500
    
    try:
        # รับข้อมูลจาก Frontend
        profile = request.json
        skin_type = profile.get('skinType')
        product_type = profile.get('productType')
        # *** UPDATED: รับค่า minPrice และ maxPrice ***
        min_price = profile.get('minPrice') 
        max_price = profile.get('maxPrice')
        concerns = profile.get('concerns', [])

        # --- ขั้นตอนการทำงาน ---
        # 1. กรองข้อมูลตามเงื่อนไข
        filtered_df = products_df.copy()
        filtered_df = filter_by_skintype(filtered_df, skin_type)
        filtered_df = filter_by_product_type(filtered_df, product_type)
        # *** UPDATED: เรียกใช้ฟังก์ชันกรองราคาแบบใหม่ ***
        filtered_df = filter_by_price(filtered_df, min_price, max_price)

        if filtered_df.empty:
            return jsonify({'success': True, 'recommendations': [], 'message': 'ไม่พบผลิตภัณฑ์ที่ตรงตามเงื่อนไขเบื้องต้น'})

        # 2. คำนวณคะแนนและจัดลำดับ
        scored_df = calculate_scores(filtered_df, skin_type, concerns)
        results_df = scored_df.sort_values('total_score', ascending=False).head(5)

        # 3. สร้าง JSON สำหรับส่งกลับ
        recommendations = []
        for _, row in results_df.iterrows():
            recommendations.append({
                'id': int(row.get('id', 0)),
                'name': str(row.get('name', '')),
                'brand': str(row.get('brand', '')),
                'type': str(row.get('type_of_product', '')),
                'price': float(row.get('price (bath)', 0)),
                'score': round(float(row.get('total_score', 0)), 2) # ปัดทศนิยม 2 ตำแหน่ง
            })
            
        return jsonify({'success': True, 'recommendations': recommendations})

    except Exception as e:
        print(f"✗ เกิดข้อผิดพลาดใน API: {e}")
        return jsonify({'success': False, 'message': 'เกิดข้อผิดพลาดภายในเซิร์ฟเวอร์'}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
