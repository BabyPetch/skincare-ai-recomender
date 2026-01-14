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
DATA_FILE_PATH = Path(__file__).parent / 'data' / 'Data_Collection_ASA - data.csv'

# --- APPLICATION SETUP ---
app = Flask(__name__)
CORS(app)

# --- DATA LOADING AND PRE-PROCESSING ---
def load_and_prepare_data(path):
    """โหลดข้อมูลจากไฟล์ CSV"""
    try:
        df = pd.read_csv(path, encoding='utf-8-sig')
        df['price (bath)'] = pd.to_numeric(df['price (bath)'].astype(str).str.replace(',', ''), errors='coerce')
        print(f"✓ โหลดและเตรียมข้อมูลสำเร็จ: {len(df)} ผลิตภัณฑ์")
        return df
    except Exception as e:
        print(f"✗ เกิดข้อผิดพลาดในการโหลดข้อมูล: {e}")
        return None

products_df = load_and_prepare_data(DATA_FILE_PATH)

# --- HELPER FUNCTIONS FOR FILTERING ---
def filter_by_skintype(df, skin_type):
    if not skin_type:
        return df
    condition = df['skintype'].fillna('').str.contains(skin_type, case=False, na=False)
    return df[condition]

def filter_by_product_type(df, product_type):
    if not product_type or "ทุกประเภท" in product_type:
        return df
    keyword = product_type.split(' ')[0]
    condition = df['type_of_product'].fillna('').str.contains(keyword, case=False, na=False)
    return df[condition]

def filter_by_price(df, min_price, max_price):
    filtered_df = df
    if min_price is not None:
        filtered_df = filtered_df[filtered_df['price (bath)'] >= min_price]
    if max_price is not None:
        filtered_df = filtered_df[filtered_df['price (bath)'] <= max_price]
    return filtered_df

# --- SCORING LOGIC ---
def calculate_scores(df, skin_type, concerns, age=None, gender=None):
    """คำนวณคะแนนผลิตภัณฑ์"""
    if df.empty:
        return df

    scored_df = df.copy()
    
    # 1. Skin Type Match (30 คะแนน)
    def skin_score(row_skintype):
        if pd.isna(row_skintype): return 0
        skintypes = [s.strip().lower() for s in str(row_skintype).split(',')]
        if skin_type.lower() in skintypes: return 30
        if 'all' in skintypes or 'ทุกสภาพผิว' in skintypes: return 15
        return 0
    scored_df['skin_score'] = scored_df['skintype'].apply(skin_score)
    
    # 2. Concerns Match (35 คะแนน)
    def concern_score(row_props):
        if pd.isna(row_props) or not concerns: return 0
        props_lower = row_props.lower()
        matched = sum(1 for c in concerns if c.lower() in props_lower)
        return (matched / len(concerns)) * 35
    scored_df['concern_score'] = scored_df['คุณสมบัติ(จากactive ingredients)'].apply(concern_score)
    
    # 3. Age Match (15 คะแนน)
    def age_score(row_props):
        if not age or pd.isna(row_props): return 7
        props_lower = row_props.lower()
        if age < 25 and 'ป้องกัน' in props_lower: return 15
        if 25 <= age < 35 and ('ลดริ้วรอยเริ่มแรก' in props_lower or 'เพิ่มความยืดหยุ่น' in props_lower): return 15
        if age >= 35 and 'ลดริ้วรอย' in props_lower: return 15
        return 7
    scored_df['age_score'] = scored_df['คุณสมบัติ(จากactive ingredients)'].apply(age_score) if age else 0
    
    # 4. Price Score (20 คะแนน)
    min_price = scored_df['price (bath)'].min()
    max_price = scored_df['price (bath)'].max()
    if max_price > min_price:
        scored_df['price_score'] = (1 - (scored_df['price (bath)'] - min_price) / (max_price - min_price)) * 20
    else:
        scored_df['price_score'] = 20
    scored_df['price_score'].fillna(0, inplace=True)

    # รวมคะแนน
    scored_df['total_score'] = (
        scored_df['skin_score'] + 
        scored_df['concern_score'] + 
        scored_df['age_score'] + 
        scored_df['price_score']
    )
    
    return scored_df

# --- API ENDPOINTS ---

@app.route('/api/recommend', methods=['POST'])
def recommend_api():
    """API แนะนำผลิตภัณฑ์"""
    if products_df is None:
        return jsonify({'success': False, 'message': 'เกิดข้อผิดพลาด: ไม่สามารถโหลดฐานข้อมูลได้'}), 500
    
    try:
        profile = request.json
        skin_type = profile.get('skinType')
        product_type = profile.get('productType')
        min_price = profile.get('minPrice') 
        max_price = profile.get('maxPrice')
        concerns = profile.get('concerns', [])
        age = profile.get('age')
        gender = profile.get('gender')

        # กรองข้อมูล
        filtered_df = products_df.copy()
        filtered_df = filter_by_skintype(filtered_df, skin_type)
        filtered_df = filter_by_product_type(filtered_df, product_type)
        filtered_df = filter_by_price(filtered_df, min_price, max_price)

        if filtered_df.empty:
            return jsonify({'success': True, 'recommendations': [], 'message': 'ไม่พบผลิตภัณฑ์ที่ตรงตามเงื่อนไข'})

        # คำนวณคะแนน
        scored_df = calculate_scores(filtered_df, skin_type, concerns, age, gender)
        results_df = scored_df.sort_values('total_score', ascending=False).head(5)

        # สร้าง JSON
        recommendations = []
        for _, row in results_df.iterrows():
            recommendations.append({
                'id': int(row.get('id', 0)),
                'name': str(row.get('name', '')),
                'brand': str(row.get('brand', '')),
                'type': str(row.get('type_of_product', '')),
                'price': float(row.get('price (bath)', 0)),
                'score': round(float(row.get('total_score', 0)), 2)
            })
            
        return jsonify({'success': True, 'recommendations': recommendations})

    except Exception as e:
        print(f"✗ เกิดข้อผิดพลาดใน API: {e}")
        return jsonify({'success': False, 'message': 'เกิดข้อผิดพลาดภายในเซิร์ฟเวอร์'}), 500


@app.route('/api/products/<int:product_id>', methods=['GET'])
def get_product_detail(product_id):
    """ดูรายละเอียดผลิตภัณฑ์"""
    if products_df is None:
        return jsonify({'success': False, 'message': 'ไม่สามารถโหลดข้อมูลได้'}), 500
    
    product = products_df[products_df['id'] == product_id]
    
    if product.empty:
        return jsonify({'success': False, 'message': 'ไม่พบผลิตภัณฑ์'}), 404
    
    product_dict = product.iloc[0].to_dict()
    product_dict = {k: (None if pd.isna(v) else v) for k, v in product_dict.items()}
    
    return jsonify({'success': True, 'product': product_dict})


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """สถิติข้อมูล"""
    if products_df is None:
        return jsonify({'success': False}), 500
    
    stats = {
        'total_products': len(products_df),
        'brands': products_df['brand'].nunique(),
        'by_type': products_df['type_of_product'].value_counts().to_dict(),
        'by_skintype': products_df['skintype'].value_counts().to_dict(),
        'price_range': {
            'min': float(products_df['price (bath)'].min()),
            'max': float(products_df['price (bath)'].max()),
            'avg': round(float(products_df['price (bath)'].mean()), 2)
        }
    }
    
    return jsonify({'success': True, 'stats': stats})


@app.route('/api/products', methods=['GET'])
def search_products():
    """ค้นหาผลิตภัณฑ์"""
    if products_df is None:
        return jsonify({'success': False}), 500
    
    query = request.args.get('q', '').lower()
    skin_type = request.args.get('skinType')
    product_type = request.args.get('productType')
    min_price = request.args.get('minPrice', type=float)
    max_price = request.args.get('maxPrice', type=float)
    
    filtered_df = products_df.copy()
    
    if query:
        filtered_df = filtered_df[
            filtered_df['name'].fillna('').str.lower().str.contains(query) |
            filtered_df['brand'].fillna('').str.lower().str.contains(query)
        ]
    
    if skin_type:
        filtered_df = filter_by_skintype(filtered_df, skin_type)
    if product_type:
        filtered_df = filter_by_product_type(filtered_df, product_type)
    if min_price or max_price:
        filtered_df = filter_by_price(filtered_df, min_price, max_price)
    
    results = filtered_df.head(50).to_dict('records')
    
    return jsonify({
        'success': True,
        'products': results,
        'total': len(filtered_df)
    })


@app.route('/api/health', methods=['GET'])
def health_check():
    """ตรวจสอบสถานะ"""
    return jsonify({
        'success': True,
        'status': 'running',
        'products_loaded': len(products_df) if products_df is not None else 0,
        'version': '1.0.0'
    })


if __name__ == '__main__':
    app.run(debug=True, port=5000)