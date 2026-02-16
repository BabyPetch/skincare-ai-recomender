import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import psycopg2
from psycopg2.extras import RealDictCursor
import os
import json

class SkincareAI:
    def __init__(self):
        self.df = None
        self.vectorizer = None
        self.tfidf_matrix = None
        
        # ⚙️ ตั้งค่า Database
        self.db_config = {
            "dbname": "skincareCollectionDB",
            "user": "postgres",
            "password": "1234",  # <--- เช็ครหัสผ่านให้ถูกต้อง
            "host": "127.0.0.1",
            "port": "5432"
        }
        
        self.load_data()

    def get_db_connection(self):
        try:
            return psycopg2.connect(**self.db_config)
        except Exception as e:
            print(f"❌ Error connecting to DB: {e}")
            return None

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
            print("🔄 AI Engine: Loading data from Database...")
            conn = self.get_db_connection()
            
            if not conn:
                print("❌ Database connection failed. AI Engine disabled.")
                self.df = pd.DataFrame()
                return

            # 1. ดึงข้อมูลสินค้าจาก PostgreSQL
            query = "SELECT * FROM products"
            cur = conn.cursor(cursor_factory=RealDictCursor)
            cur.execute(query)
            rows = cur.fetchall()
            conn.close()

            if not rows:
                print("⚠️ No data found in database.")
                self.df = pd.DataFrame()
                return

            self.df = pd.DataFrame(rows)
            print(f"📦 Loaded {len(self.df)} products from DB.")

            # 2. แปลงข้อมูล JSONB (details) กลับมาเป็นคอลัมน์เพื่อให้ AI ใช้งานง่าย
            # เราต้องแตก details ออกมาเป็น skintype, active_ingredients, benefits
            def extract_detail(row, key, default=''):
                if isinstance(row.get('details'), dict):
                    return row['details'].get(key, default)
                return default

            self.df['skintype'] = self.df.apply(lambda x: extract_detail(x, 'skintype'), axis=1)
            self.df['active ingredients'] = self.df.apply(lambda x: extract_detail(x, 'active_ingredients'), axis=1)
            self.df['benefits'] = self.df.apply(lambda x: extract_detail(x, 'benefits'), axis=1)
            self.df['ingredients'] = self.df.apply(lambda x: extract_detail(x, 'ingredients'), axis=1)
            
            # Map ชื่อคอลัมน์ให้ตรงกับ Logic เดิม
            self.df['type_of_product'] = self.df['category'] 

            # 3. จัดการราคา (ใน DB เป็นตัวเลขอยู่แล้ว แต่กันเหนียวแปลงเป็น float)
            self.df['price'] = pd.to_numeric(self.df['price'], errors='coerce').fillna(0)

            # 4. Rating (ยังคงใช้วิธีโหลด CSV เสริม ถ้ายังไม่มีระบบ Rating ใน DB)
            # แต่ถ้าไม่มีไฟล์ ก็ให้คะแนนเริ่มต้นเป็น 0
            current_dir = os.path.dirname(os.path.abspath(__file__))
            rating_path = os.path.join(current_dir, '../../data/user_ratings.csv') # ปรับ path ตามจริง
            
            if os.path.exists(rating_path):
                try:
                    ratings_df = pd.read_csv(rating_path)
                    avg_ratings = ratings_df.groupby('product_id')['rating'].mean()
                    self.df['rating'] = self.df['id'].map(avg_ratings).fillna(0)
                except:
                    self.df['rating'] = 0
            else:
                self.df['rating'] = 0

            # 5. สร้าง Features สำหรับ Vectorizer
            self.df['combined_features'] = ''
            # รวม text จากคอลัมน์สำคัญ
            feature_cols = ['skintype', 'benefits', 'category', 'brand', 'active ingredients', 'ingredients']
            
            for col in feature_cols:
                if col in self.df.columns:
                    self.df['combined_features'] += self.df[col].astype(str).fillna('') + ' '
            
            # 6. สร้าง TF-IDF Matrix
            self.vectorizer = TfidfVectorizer(analyzer='char_wb', ngram_range=(3, 5), min_df=1)
            self.tfidf_matrix = self.vectorizer.fit_transform(self.df['combined_features'])

            print("✅ AI Engine Ready & Trained.")
            
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

        # --- 1. กรองสภาพผิว ---
        if skin_type and skin_type.lower() != 'all':
            filtered_df = self.df[
                (self.df['skintype'].str.contains(skin_type, case=False, na=False)) |
                (self.df['skintype'].str.contains('all', case=False, na=False)) |
                (self.df['skintype'] == '') 
            ].copy()
        else:
            filtered_df = self.df.copy()

        # --- 2. กรองราคา ---
        filtered_df = filtered_df[
            (filtered_df['price'] >= float(min_price)) & 
            (filtered_df['price'] <= float(max_price))
        ]
        
        if filtered_df.empty:
            return []

        # --- 3. (ใหม่ ✨) แปลง Keyword เป็นภาษาไทย/คำใกล้เคียง ---
        # เพื่อให้ AI ฉลาดขึ้น รู้ว่า acne = สิว
        keyword_map = {
            "acne": ["acne", "สิว", "breakout", "อุดตัน", "bha", "salicylic"],
            "dark spots": ["dark spot", "รอยดำ", "จุดด่างดำ", "hyper", "niacinamide", "vit c", "whitening", "bright"],
            "oily": ["oily", "มัน", "sebum", "pills"],
            "dry": ["dry", "แห้ง", "hydration", "moist", "hyaluron"],
            "sensitive": ["sensitive", "แพ้", "soothing", "calming", "cica"],
            "aging": ["aging", "wrinkle", "ริ้วรอย", "retinol", "bakuchiol"]
        }

        # สร้างข้อความค้นหาใหม่ที่รวมคำไทยไปด้วย
        expanded_concerns = []
        for c in concerns:
            c_lower = c.lower()
            # ถ้ามีใน map ให้เอาคำไทยมาด้วย, ถ้าไม่มีให้ใช้คำเดิม
            expanded_concerns.extend(keyword_map.get(c_lower, [c_lower]))
        
        user_text = ' '.join(expanded_concerns)
        print(f"🔍 Searching for keywords: {user_text}") # Debug ดูว่า AI หาคำว่าอะไรบ้าง

        # --- 4. คำนวณความแมตช์ (Cosine Similarity) ---
        user_vec = self.vectorizer.transform([user_text])
        product_indices = filtered_df.index
        relevant_tfidf = self.tfidf_matrix[product_indices]
        
        cosine_sim = cosine_similarity(user_vec, relevant_tfidf).flatten()
        filtered_df['match_score'] = cosine_sim * 100
        
        # --- 5. ให้คะแนนพิเศษ (Hybrid Score) ---
        def boost_score(row):
            score = row['match_score']
            # เช็ค Text ทั้งก้อนของสินค้า
            props = row['combined_features'].lower()
            
            for keyword in expanded_concerns:
                if keyword in props:
                    score += 15 # เจอคำไทยหรืออังกฤษที่ตรงกัน บวกคะแนนเพิ่ม!
            return score

        filtered_df['final_score'] = filtered_df.apply(boost_score, axis=1)
        filtered_df['final_score'] = (filtered_df['final_score'] * 0.8) + (filtered_df['rating'] * 4)
        
        # --- 6. จัดเรียงและเลือก Top N ---
        results = filtered_df.sort_values(by='final_score', ascending=False).head(top_n)
        
        response = []
        for _, row in results.iterrows():
            quality_score = (row['rating'] / 5) * 100 if row['rating'] > 0 else 80
            
            response.append({
                "id": int(row['id']),
                "name": row['name'],
                "brand": row['brand'],
                "type": row['category'],
                "price": float(row['price']),
                "score": int(row['final_score']),
                "match_percent": int(min(row['final_score'], 100)),
                "analysis": {
                    "skin_match": round(row['match_score'], 1),
                    "quality": round(quality_score, 1),
                    "trend": 85
                },
                "routine_step": self._determine_step(row['category'])
            })
            
        return sorted(response, key=lambda x: x['routine_step'])
    
