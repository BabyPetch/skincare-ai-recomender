# -*- coding: utf-8 -*-
from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
from pathlib import Path
import sys
import io

# --- AI & Data Science Libraries ---
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# --- Configuration & Setup ---
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

DATA_FILE_PATH = Path(__file__).parent / 'data' / 'Data_Collection_ASA - data.csv'

app = Flask(__name__)
CORS(app)

# --- THE HYBRID RECOMMENDATION MODEL CLASS ---

class SkincareRecommender:
    """
    คลาสโมเดลสำหรับแนะนำผลิตภัณฑ์สกินแคร์แบบผสมผสาน (Hybrid)
    """
    def __init__(self, data_path):
        self.df = self._load_and_prepare_data(data_path)
        
        # AI Content-Based Model Components
        self.tfidf_vectorizer = None
        self.tfidf_matrix = None
        
        if self.df is not None:
            print("✓ SkincareRecommender model initialized.")
            self._build_content_based_model()

    def _load_and_prepare_data(self, path):
        try:
            df = pd.read_csv(path, encoding='utf-8-sig')
            df['price (bath)'] = pd.to_numeric(
                df['price (bath)'].astype(str).str.replace(',', ''), errors='coerce'
            )
            df['ingredients'] = df['ingredients'].fillna('')
            print(f"✓ Data loaded and prepared: {len(df)} products")
            return df
        except Exception as e:
            print(f"✗ Error loading data for the model: {e}")
            return None

    def _build_content_based_model(self):
        """
        สร้างโมเดล Content-Based จากส่วนผสมโดยใช้ TF-IDF
        """
        print("Building AI Content-Based model from ingredients...")
        self.tfidf_vectorizer = TfidfVectorizer(stop_words='english', max_features=500)
        self.tfidf_matrix = self.tfidf_vectorizer.fit_transform(self.df['ingredients'])
        print("✓ AI Content-Based model built successfully.")

    def _recommend_content_based(self, profile, top_n=10):
        """
        ส่วนที่ 1: แนะนำโดยใช้คุณสมบัติ (Rule-Based Content Filtering)
        """
        if self.df is None: return pd.DataFrame()

        skin_type = profile.get('skinType')
        concerns = profile.get('concerns', [])
        
        # Apply filters from the profile to the dataframe before scoring
        filtered_df = self.df.copy()
        min_price = profile.get('minPrice')
        max_price = profile.get('maxPrice')
        product_type = profile.get('productType')

        if min_price is not None:
            filtered_df = filtered_df[filtered_df['price (bath)'] >= min_price]
        if max_price is not None:
            filtered_df = filtered_df[filtered_df['price (bath)'] <= max_price]
        if product_type and "ทุกประเภท" not in product_type:
            keyword = product_type.split(' ')[0]
            filtered_df = filtered_df[filtered_df['type_of_product'].fillna('').str.contains(keyword, case=False, na=False)]
        
        if filtered_df.empty: 
            return pd.DataFrame()

        # --- Scoring ---
        scored_df = filtered_df.copy()
        
        # 1. Skin Type Match Score (40 คะแนน) - NEW WEIGHT
        def skin_score(row_skintype):
            if pd.isna(row_skintype) or not skin_type: return 0
            skintypes = [s.strip().lower() for s in str(row_skintype).split(',')]
            if skin_type.lower() in skintypes: return 40 # ตรงเป๊ะ
            return 20 if any(skin_type.lower() in s for s in skintypes) else 0 # ปรับคะแนนส่วนนี้ด้วย
        scored_df['skin_score'] = scored_df['skintype'].apply(skin_score)
        
        # 2. Concerns Match Score (50 คะแนน) - NEW WEIGHT
        def concern_score(row_props):
            score = sum(1 for c in concerns if c.lower() in str(row_props).lower())
            return (score / len(concerns)) * 50 if concerns else 0
        scored_df['concern_score'] = scored_df['คุณสมบัติ(จากactive ingredients)'].apply(concern_score)
        
        # 3. Price Score (10 คะแนน) - NEW WEIGHT
        # Normalize price score within the already filtered group
        min_p, max_p = scored_df['price (bath)'].min(), scored_df['price (bath)'].max()
        if max_p > min_p:
            scored_df['price_score'] = (1 - (scored_df['price (bath)'] - min_p) / (max_p - min_p)) * 10
        else:
            scored_df['price_score'] = 10
        scored_df['price_score'].fillna(0, inplace=True)
        
        # รวมคะแนนทั้งหมด
        scored_df['content_score'] = scored_df['skin_score'] + scored_df['concern_score'] + scored_df['price_score']
        
        return scored_df.sort_values('content_score', ascending=False).head(top_n)

    def _recommend_collaborative(self, user_id, top_n=10):
        """
        ส่วนที่ 2: แนะนำโดยใช้พฤติกรรมผู้ใช้ (Collaborative Filtering) - (Placeholder)
        """
        print(f"Collaborative Filtering: Finding recommendations for user {user_id}...")
        return pd.DataFrame() 

    def recommend_hybrid(self, profile, top_n=5):
        """
        ส่วนที่ 3: แนะนำแบบผสมผสาน (Hybrid) - รวมผลลัพธ์
        """
        user_id = profile.get('userId')

        # Content-based is now the main logic which also handles filtering
        content_recs = self._recommend_content_based(profile, top_n=10)
        collab_recs = self._recommend_collaborative(user_id, top_n=10)

        if collab_recs.empty:
            print("Hybrid: Collaborative data not found. Falling back to Content-Based.")
            final_recs = content_recs.head(top_n)
        else:
            print("Hybrid: Merging results from both systems.")
            content_recs['final_score'] = content_recs['content_score'] * 0.7
            collab_recs['final_score'] = collab_recs.get('collab_score', 0) * 0.3
            
            merged_recs = pd.concat([content_recs, collab_recs])
            final_recs = merged_recs.sort_values('final_score', ascending=False).drop_duplicates(subset=['id']).head(top_n)

        # 3. จัดรูปแบบผลลัพธ์
        recommendations = []
        for _, row in final_recs.iterrows():
            recommendations.append({
                'id': int(row.get('id', 0)),
                'name': str(row.get('name', '')),
                'brand': str(row.get('brand', '')),
                'type': str(row.get('type_of_product', '')), # *** FIX: เพิ่มบรรทัดนี้ ***
                'price': float(row.get('price (bath)', 0)),
                'score': round(float(row.get('content_score', row.get('final_score', 0))), 2)
            })
        return recommendations

# --- GLOBAL MODEL INSTANTIATION ---
recommender_model = SkincareRecommender(DATA_FILE_PATH)

# --- API ENDPOINTS ---
@app.route('/api/recommend', methods=['POST'])
def recommend_api():
    if recommender_model.df is None:
        return jsonify({'success': False, 'message': 'ฐานข้อมูลไม่พร้อมใช้งาน'}), 500
    
    try:
        user_profile = request.json
        recommendations = recommender_model.recommend_hybrid(user_profile, top_n=5)
        
        return jsonify({
            'success': True, 
            'recommendations': recommendations,
            'message': 'ไม่พบผลิตภัณฑ์' if not recommendations else 'แสดงผลแบบ Hybrid'
        })
    except Exception as e:
        print(f"✗ เกิดข้อผิดพลาดใน API: {e}")
        return jsonify({'success': False, 'message': f'เกิดข้อผิดพลาด: {e}'}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)

