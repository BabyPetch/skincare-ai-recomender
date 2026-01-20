import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import os
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE_PATH = os.path.join(BASE_DIR, '../data/Data_Collection_ASA - data.csv')

class SkincareAI:
    def __init__(self):
        self.df = None
        self.vectorizer = None
        self.tfidf_matrix = None
        self.load_data()

    def _analyze_sentiment(self, text):
        if not isinstance(text, str): return 0
        positive_words = ['good', 'great', 'love', 'amazing', 'best', 'excellent', 'ชอบ', 'ดี', 'เลิศ', 'ปัง', 'ขาว', 'ใส']
        negative_words = ['bad', 'worst', 'hate', 'terrible', 'breakout', 'แพ้', 'สิวขึ้น', 'แย่', 'พัง']
        score = 0
        text = text.lower()
        for word in positive_words:
            if word in text: score += 1
        for word in negative_words:
            if word in text: score -= 1
        return score

    def load_data(self):
        try:
            print("🔄 AI Engine: Loading data...")
            if not os.path.exists(DATA_FILE_PATH):
                print(f"❌ Error: Main data file not found at {DATA_FILE_PATH}")
                self.df = pd.DataFrame()
                return

            self.df = pd.read_csv(DATA_FILE_PATH, encoding='utf-8-sig')

            # 1. จัดการชื่อคอลัมน์ (Normalize Columns)
            self.df.columns = self.df.columns.str.strip().str.lower()
            
            # Map ชื่อคอลัมน์ราคาให้เป็น 'price'
            rename_map = {
                'price (bath)': 'price',
                'price(bath)': 'price',
                'price (baht)': 'price',
                'ราคา': 'price'
            }
            self.df.rename(columns=rename_map, inplace=True)
            
            print(f"📊 Columns Found: {self.df.columns.tolist()}")

            # 2. 🔥🔥🔥 แก้ไขสำคัญ: ทำความสะอาดราคาตั้งแต่ตอนโหลด (Regex) 🔥🔥🔥
            if 'price' in self.df.columns:
                # แปลงเป็น String -> ใช้ Regex เอาเฉพาะตัวเลขและจุดทศนิยม ([^0-9.]) -> แปลงเป็น Float
                self.df['price'] = self.df['price'].astype(str).str.replace(r'[^\d.]', '', regex=True)
                self.df['price'] = pd.to_numeric(self.df['price'], errors='coerce').fillna(0)
            else:
                self.df['price'] = 0

            # 3. Clean ID
            if 'id' not in self.df.columns:
                self.df['id'] = self.df.index
            self.df['id'] = pd.to_numeric(self.df['id'], errors='coerce').fillna(0).astype(int)
            print(f"📦 Main Data: Loaded {len(self.df)} products.")

            # 4. Ratings
            current_dir = os.path.dirname(os.path.abspath(__file__))
            rating_path = os.path.join(current_dir, '../data/user_ratings.csv')
            
            if os.path.exists(rating_path):
                try:
                    ratings_df = pd.read_csv(rating_path)
                    ratings_df.columns = ratings_df.columns.str.strip().str.lower()
                    ratings_df['product_id'] = pd.to_numeric(ratings_df['product_id'], errors='coerce')
                    ratings_df = ratings_df.dropna(subset=['product_id'])
                    ratings_df['product_id'] = ratings_df['product_id'].astype(int)
                    
                    avg_ratings = ratings_df.groupby('product_id')['rating'].mean()
                    self.df['real_rating'] = self.df['id'].map(avg_ratings).fillna(0)
                    self.df['rating'] = self.df['real_rating']
                except:
                    self.df['rating'] = 0
            else:
                self.df['rating'] = 0

            # 5. Vectorizer
            self.df['combined_features'] = ''
            feature_cols = ['skintype', 'คุณสมบัติ(จากactive ingredients)', 'type_of_product', 'brand', 'active ingredients']
            for col in feature_cols:
                if col in self.df.columns:
                    self.df['combined_features'] += self.df[col].fillna('') + ' '
            
            if 'reviews' not in self.df.columns: self.df['reviews'] = ''
                
            self.vectorizer = TfidfVectorizer(analyzer='char_wb', ngram_range=(3, 5), min_df=1)
            self.tfidf_matrix = self.vectorizer.fit_transform(self.df['combined_features'])

            self.df['rating'] = pd.to_numeric(self.df['rating'], errors='coerce').fillna(0)
            self.df['sentiment_score'] = self.df['reviews'].apply(self._analyze_sentiment)

            print("✅ AI Engine Ready.")
            
        except Exception as e:
            print(f"❌ Critical Error loading data: {e}")
            self.df = pd.DataFrame()

    def _determine_step(self, product_type):
        product_type = str(product_type).lower()
        if 'cleans' in product_type or 'wash' in product_type or 'micellar' in product_type: return 1
        if 'toner' in product_type: return 2
        if 'serum' in product_type or 'essence' in product_type or 'ampoule' in product_type: return 3
        if 'moist' in product_type or 'cream' in product_type or 'lotion' in product_type or 'gel' in product_type: return 4
        if 'sun' in product_type or 'spf' in product_type or 'uv' in product_type: return 5
        return 99

    def recommend_products(self, skin_type, concerns, min_price=0, max_price=100000, top_n=5):
        if self.df is None or self.df.empty:
            return []

        print(f"🔍 DEBUG: Filtering - Skin: {skin_type}, Price: {min_price}-{max_price}")

        # 1. กรองสภาพผิว
        if skin_type.lower() != 'all':
            if 'skintype' in self.df.columns:
                filtered_df = self.df[
                    (self.df['skintype'].str.contains(skin_type, case=False, na=False)) |
                    (self.df['skintype'].str.contains('all', case=False, na=False))
                ].copy()
            else:
                 filtered_df = self.df.copy()
        else:
            filtered_df = self.df.copy()

        # 2. กรองราคา (ข้อมูลงวดนี้สะอาดแล้วเพราะทำ Regex ตอน Load)
        filtered_df = filtered_df[
            (filtered_df['price'] >= float(min_price)) & 
            (filtered_df['price'] <= float(max_price))
        ]
        
        # ปริ้นท์เช็คว่าเหลือกี่ชิ้น
        print(f"   👉 Items left after price filter: {len(filtered_df)}")

        if filtered_df.empty:
            print("⚠️ No products match the price criteria.")
            return []

        # 3. คำนวณความแมตช์
        user_text = ' '.join(concerns)
        user_vec = self.vectorizer.transform([user_text])
        
        product_indices = filtered_df.index
        relevant_tfidf = self.tfidf_matrix[product_indices]
        
        cosine_sim = cosine_similarity(user_vec, relevant_tfidf).flatten()
        filtered_df['match_score'] = cosine_sim * 100
        
        # 4. Hybrid Score
        filtered_df['final_score'] = (
            (filtered_df['match_score'] * 0.7) + 
            ((filtered_df['rating'] / 5 * 100) * 0.3)
        )
        
        # 5. จัดเรียง
        results = filtered_df.sort_values(by='final_score', ascending=False).head(top_n)
        
        response = []
        for _, row in results.iterrows():
            quality_score = (row['rating'] / 5) * 100 if row['rating'] > 0 else 0
            p_type = row['type_of_product'] if 'type_of_product' in row else 'unknown'
            
            response.append({
                "id": int(row['id']),
                "name": row['name'],
                "brand": row['brand'],
                "type": p_type,
                "price": float(row['price']),
                "score": int(row['final_score']),
                "match_percent": int(row['final_score']),
                "analysis": {
                    "skin_match": round(row['match_score'], 1),
                    "quality": round(quality_score, 1),
                    "trend": 50
                },
                "routine_step": self._determine_step(p_type)
            })
            
        return sorted(response, key=lambda x: x['routine_step'])