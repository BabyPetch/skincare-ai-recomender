import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from textblob import TextBlob
from config import DATA_FILE_PATH, ROUTINE_MAP

class SkincareAI:
    def __init__(self):
        self.df = None
        self.vectorizer = None
        self.tfidf_matrix = None
        self.load_data()

    def load_data(self):
        try:
            # 1. โหลดข้อมูล
            self.df = pd.read_csv(DATA_FILE_PATH, encoding='utf-8-sig')
            
            # --- 🛡️ ส่วนแก้ Error: สร้างคอลัมน์หลอก ถ้าใน CSV ไม่มี ---
            if 'rating' not in self.df.columns:
                self.df['rating'] = 0 
            
            if 'reviews' not in self.df.columns:
                self.df['reviews'] = ''

            # --- 2. รวมข้อมูลสินค้า (แก้ชื่อคอลัมน์ให้ตรงเป๊ะ) ---
            # ใช้ type_of_product แทน category
            self.df['combined_features'] = (
                self.df['skintype'].fillna('') + ' ' + 
                self.df['คุณสมบัติ(จากactive ingredients)'].fillna('') + ' ' + 
                self.df['type_of_product'].fillna('') + ' ' + 
                self.df['brand'].fillna('')
            )
            
            # --- 3. สร้าง AI Vector (สูตร N-gram อ่านภาษาไทยรู้เรื่อง) ---
            # analyzer='char_wb' ช่วยให้อ่านทีละ 3-5 ตัวอักษร (แก้ปัญหาตัดคำผิด)
            self.vectorizer = TfidfVectorizer(analyzer='char_wb', ngram_range=(3, 5), min_df=1)
            self.tfidf_matrix = self.vectorizer.fit_transform(self.df['combined_features'])

            # --- 4. เตรียม Rating (แปลงเป็นตัวเลข) ---
            self.df['rating'] = pd.to_numeric(self.df['rating'], errors='coerce').fillna(0)
            self.df['sentiment_score'] = self.df['reviews'].apply(self._analyze_sentiment)

            print(f"✅ AI Engine Ready: Loaded {len(self.df)} products.")
            
        except Exception as e:
            print(f"❌ Error loading data: {e}")
            self.df = pd.DataFrame()

    def _analyze_sentiment(self, reviews_str):
        if pd.isna(reviews_str) or str(reviews_str).strip() == "":
            return 0.0
        try:
            reviews = str(reviews_str).split('|')
            scores = [TextBlob(r).sentiment.polarity for r in reviews]
            return sum(scores) / len(scores) if scores else 0.0
        except:
            return 0.0

    def _get_routine_step(self, product_type):
        pt_lower = str(product_type).lower()
        for key, step in ROUTINE_MAP.items():
            if key in pt_lower: return step
        return 6

    def recommend(self, skin_type, concerns, age):
        # 1. เช็คความปลอดภัย
        if self.df is None or self.df.empty:
            print("⚠️ AI Error: Database is empty.")
            return []

        print(f"🔍 AI Analyzing: Skin={skin_type}, Concerns={concerns}")

        # 2. แปลงความต้องการลูกค้าเป็น Vector
        user_query = f"{skin_type} {' '.join(concerns)}"
        user_vector = self.vectorizer.transform([user_query])
        
        # 3. คำนวณความเหมือน (0-1)
        similarity_scores = cosine_similarity(user_vector, self.tfidf_matrix).flatten()
        
        final_results = []
        
        for idx, score in enumerate(similarity_scores):
            row = self.df.iloc[idx]
            
            # คะแนน Content (เต็ม 100)
            s_content = score * 100 
            
            # เช็คว่ามีรีวิวไหม (เพื่อปรับสูตรคำนวณ)
            rating_val = float(row['rating'])
            has_reviews = rating_val > 0 or (str(row.get('reviews','')) != '')

            # --- 🧠 Logic คำนวณคะแนน ---
            if has_reviews:
                # สูตร Hybrid (ถ้ามีรีวิว)
                s_rating = rating_val * 20 
                s_sentiment = (float(row.get('sentiment_score', 0)) + 1) * 50
                total_score = (s_content * 0.6) + (s_rating * 0.2) + (s_sentiment * 0.2)
                insight_suffix = " (จากสเปคและรีวิว)"
            else:
                # สูตร Content ล้วน (ลดทอนนิดหน่อย)
                total_score = s_content * 0.95
                insight_suffix = ""

            # --- 🛡️ กรอง Skin Type (แก้ให้ไม่สนตัวพิมพ์เล็ก/ใหญ่) ---
            row_skin = str(row.get('skintype', '')).lower()
            user_skin = skin_type.lower()
            
            is_skin_match = False
            # ถ้าลูกค้าเลือก All หรือ ผิวลูกค้าตรงกับสินค้า
            if user_skin == 'all' or user_skin in row_skin:
                is_skin_match = True
            # หรือถ้าสินค้าบอกว่าใช้ได้กับ All skin types
            elif 'all' in row_skin:
                is_skin_match = True

            # --- 🎯 กรองคะแนนขั้นต่ำ (ปรับลดเหลือ > 1) ---
            if is_skin_match and total_score > 1: 
                final_results.append({
                    'id': int(row.get('id', 0)),
                    'name': str(row.get('name', '')),
                    'brand': str(row.get('brand', '')),
                    'type': str(row.get('type_of_product', '')), # ใช้ชื่อคอลัมน์ที่ถูก
                    'price': float(str(row.get('price (bath)', 0)).replace(',','')),
                    'score': int(total_score),
                    'ai_insight': f"Match {int(total_score)}%{insight_suffix}",
                    'routine_step': self._get_routine_step(row.get('type_of_product', ''))
                })

        # 4. เรียงลำดับคะแนนมาก -> น้อย
        final_results.sort(key=lambda x: x['score'], reverse=True)
        
        # 5. ตัดเอาแค่ Top 5 แล้วเรียงตามขั้นตอนการทา (Step)
        top_picks = final_results[:5]
        top_picks.sort(key=lambda x: x['routine_step'])
        
        print(f"✅ Found {len(top_picks)} recommendations.")
        return top_picks