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

            # --- 2. รวมข้อมูลสินค้า ---
            self.df['combined_features'] = (
                self.df['skintype'].fillna('') + ' ' + 
                self.df['คุณสมบัติ(จากactive ingredients)'].fillna('') + ' ' + 
                self.df['type_of_product'].fillna('') + ' ' + 
                self.df['brand'].fillna('')
            )
            
            # --- 3. สร้าง AI Vector ---
            self.vectorizer = TfidfVectorizer(analyzer='char_wb', ngram_range=(3, 5), min_df=1)
            self.tfidf_matrix = self.vectorizer.fit_transform(self.df['combined_features'])

            # --- 4. เตรียม Rating ---
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

    # --- ✨ ฟังก์ชันวิเคราะห์ค่าพลังกราฟ Radar ---
    def _analyze_benefits(self, text):
        text = str(text).lower()
        scores = { 'acne': 4, 'brightening': 4, 'moisturizing': 4, 'aging': 4, 'gentle': 4 }
        
        keywords = {
            'acne': ['สิว', 'มัน', 'อุดตัน', 'รูขุมขน', 'acne', 'bha', 'salicylic', 'tea tree', 'oil', 'sebum', 'pore', 'zinc', 'clay', 'mud', 'green tea', 'cleanse', 'foam'],
            'brightening': ['ขาว', 'ใส', 'จุดด่างดำ', 'หมองคล้ำ', 'white', 'bright', 'vit c', 'niacinamide', 'glow', 'radiance', 'dark spot', 'arbutin', 'lemon'],
            'moisturizing': ['ชุ่มชื้น', 'แห้ง', 'น้ำ', 'ฉ่ำ', 'hydrat', 'moist', 'hyaluron', 'ceramide', 'water', 'aloe', 'sooth', 'essence', 'mask', 'dry'],
            'aging': ['ริ้วรอย', 'เหี่ยวย่น', 'ตึง', 'ย้อนวัย', 'age', 'wrinkle', 'retinol', 'firm', 'collagen', 'peptide', 'ginseng', 'repair', 'anti-aging'],
            'gentle': ['แพ้', 'อ่อนโยน', 'ปลอบประโลม', 'sensitive', 'gentle', 'sooth', 'centella', 'free', 'natural', 'calm', 'chamomile', 'organic', 'cica']
        }
        
        for key, words in keywords.items():
            for word in words:
                if word in text: 
                    scores[key] += 2 
            scores[key] = min(scores[key], 10)
            
        return scores

    # --- ✨ ฟังก์ชันดึงจุดเด่น ---
    def _get_highlights(self, props_text):
        if not props_text: return []
        words = str(props_text).replace(',', ' ').split()
        return words[:3]

    def recommend(self, skin_type, concerns, age):
        if self.df is None or self.df.empty:
            print("⚠️ AI Error: Database is empty.")
            return []

        print(f"🔍 AI Analyzing: Skin={skin_type}, Concerns={concerns}")

        user_query = f"{skin_type} {' '.join(concerns)}"
        user_vector = self.vectorizer.transform([user_query])
        
        similarity_scores = cosine_similarity(user_vector, self.tfidf_matrix).flatten()
        
        final_results = []
        
        for idx, score in enumerate(similarity_scores):
            row = self.df.iloc[idx]
            
            s_content = score * 100 
            rating_val = float(row['rating'])
            has_reviews = rating_val > 0 or (str(row.get('reviews','')) != '')

            if has_reviews:
                s_rating = rating_val * 20 
                s_sentiment = (float(row.get('sentiment_score', 0)) + 1) * 50
                total_score = (s_content * 0.6) + (s_rating * 0.2) + (s_sentiment * 0.2)
                insight_suffix = " (จากสเปคและรีวิว)"
            else:
                total_score = s_content * 0.95
                insight_suffix = ""

            row_skin = str(row.get('skintype', '')).lower()
            user_skin = skin_type.lower()
            
            is_skin_match = False
            if user_skin == 'all' or user_skin in row_skin:
                is_skin_match = True
            elif 'all' in row_skin:
                is_skin_match = True

            if is_skin_match and total_score > 1: 
                props = str(row.get('คุณสมบัติ(จากactive ingredients)', ''))
                name = str(row.get('name', ''))
                full_text_for_ai = f"{props} {name}"

                final_results.append({
                    'id': int(row.get('id', 0)),
                    'name': name,
                    'brand': str(row.get('brand', '')),
                    'type': str(row.get('type_of_product', '')),
                    'price': float(str(row.get('price (bath)', 0)).replace(',','')),
                    'score': int(total_score),
                    'ai_insight': f"Match {int(total_score)}%{insight_suffix}",
                    'routine_step': self._get_routine_step(row.get('type_of_product', '')),
                    'benefits': self._analyze_benefits(full_text_for_ai),
                    'highlights': self._get_highlights(props)
                })

        final_results.sort(key=lambda x: x['score'], reverse=True)
        top_picks = final_results[:5]
        top_picks.sort(key=lambda x: x['routine_step'])
        
        print(f"✅ Found {len(top_picks)} recommendations.")
        return top_picks