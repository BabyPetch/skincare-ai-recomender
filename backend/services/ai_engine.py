import pandas as pd
import numpy as np
import sys
import os
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import TruncatedSVD

# ==========================================
# 🔧 SETUP PATH & CONFIG IMPORT
# ==========================================
# เทคนิค: ถอยหลัง 1 ขั้นจาก folder services เพื่อให้เจอ config.py ที่หน้า backend
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from config import DATA_FILE_PATH, ROUTINE_MAP, BASE_DIR
except ImportError:
    # Fallback กรณีหา config ไม่เจอ (กันเหนียว)
    print("⚠️ Warning: Could not import config. Using fallback paths.")
    BASE_DIR = Path(__file__).parent.parent
    DATA_FILE_PATH = BASE_DIR / 'data' / 'Data_Collection_ASA - data.csv'
    ROUTINE_MAP = {}

# ==========================================
# 🧠 AI ENGINE CLASS
# ==========================================
class SkincareAI:
    def __init__(self):
        self.df = None
        self.ratings_df = None 
        self.vectorizer = None
        self.tfidf_matrix = None
        self.cf_matrix = None  
        self.product_id_map = []
        
        # ⭐ เอาไว้เก็บ Dictionary คะแนนเฉลี่ย (เช่น {53: 4.2, 75: 3.5})
        self.product_avg_ratings = {} 
        
        # เริ่มโหลดข้อมูลทันทีที่ประกาศ Class
        self.load_data()

    # ---------------------------------------------------------
    # 1️⃣ DATA LOADING & PREPARATION
    # ---------------------------------------------------------
    def load_data(self):
        print("-" * 50)
        print("⏳ Starting AI Engine Initialization...")
        
        try:
            # --- Load Product Data (Content-Based) ---
            print(f"📦 Loading Products from: {DATA_FILE_PATH.name}")
            self.df = pd.read_csv(DATA_FILE_PATH, encoding='utf-8-sig')
            
            # Data Cleaning / Fill Missing Values
            if 'rating' not in self.df.columns: self.df['rating'] = 0 
            if 'reviews' not in self.df.columns: self.df['reviews'] = ''
            
            # สร้าง Combined Features สำหรับ NLP
            self.df['combined_features'] = (
                self.df['skintype'].fillna('') + ' ' + 
                self.df['คุณสมบัติ(จากactive ingredients)'].fillna('') + ' ' + 
                self.df['type_of_product'].fillna('') + ' ' + 
                self.df['brand'].fillna('')
            )
            
            # Build TF-IDF (Content-Based)
            self.vectorizer = TfidfVectorizer(analyzer='char_wb', ngram_range=(3, 5), min_df=1)
            self.tfidf_matrix = self.vectorizer.fit_transform(self.df['combined_features'])

            # --- Load User Ratings (Collaborative Filtering) ---
            ratings_path = BASE_DIR / 'data' / 'user_ratings.csv'
            
            if ratings_path.exists():
                print(f"👥 Loading User Ratings from: {ratings_path.name}")
                self.ratings_df = pd.read_csv(ratings_path)
                
                if not self.ratings_df.empty:
                    # ⭐ 1. บังคับแปลง Rating และ Product ID เป็นตัวเลขให้หมด ⭐
                    self.ratings_df['rating'] = pd.to_numeric(self.ratings_df['rating'], errors='coerce')
                    self.ratings_df['product_id'] = pd.to_numeric(self.ratings_df['product_id'], errors='coerce').fillna(0).astype(int)
                    
                    # 2. สร้าง Dictionary
                    self.product_avg_ratings = self.ratings_df.groupby('product_id')['rating'].mean().to_dict()
                    
                    # ⭐ DEBUG: ปริ้นท์ออกมาดูหน่อยว่าโหลดอะไรมาบ้าง (ดูแค่ 5 ตัวแรก)
                    print(f"   📊 Debug Loaded Ratings: {list(self.product_avg_ratings.items())[:5]}")
                    print(f"   ⭐ Calculated avg ratings for {len(self.product_avg_ratings)} products.")
                # ---------------------------------------------------

                print(f"   -> Found {len(self.ratings_df)} reviews.")
            else:
                print(f"⚠️ Warning: File not found at {ratings_path}")
                print("   -> System will run in 'Content-Based Only' mode.")
                self.ratings_df = pd.DataFrame(columns=['user_id', 'product_id', 'rating'])
                self.product_avg_ratings = {}

            # Build SVD Model
            self._build_collaborative_model()

            print(f"✅ AI System Ready: {len(self.df)} Products / {len(self.ratings_df)} Ratings Loaded.")
            print("-" * 50)
            
        except Exception as e:
            print(f"❌ CRITICAL ERROR in load_data: {e}")
            import traceback
            traceback.print_exc()
            self.df = pd.DataFrame()

    # ---------------------------------------------------------
    # 2️⃣ MODEL BUILDING (SVD)
    # ---------------------------------------------------------
    def _build_collaborative_model(self):
        if self.ratings_df.empty:
            self.cf_matrix = None
            return

        try:
            # Pivot Table: User x Item
            user_item_matrix = self.ratings_df.pivot_table(index='user_id', columns='product_id', values='rating').fillna(0)
            
            if user_item_matrix.empty:
                return

            # SVD Calculation
            X = user_item_matrix.values.T # Transpose -> Item x User
            n_components = min(12, len(user_item_matrix) - 1)
            
            SVD = TruncatedSVD(n_components=n_components, random_state=42)
            matrix = SVD.fit_transform(X)
            
            # Calculate Correlation Matrix
            self.cf_matrix = np.corrcoef(matrix)
            self.product_id_map = list(user_item_matrix.columns) # Map index to Product ID
            
        except Exception as e:
            print(f"⚠️ SVD Construction Error: {e}")
            self.cf_matrix = None

    def _get_collaborative_score(self, target_id):
        """ ค้นหาคะแนนความสัมพันธ์จาก Collaborative Filtering """
        if self.cf_matrix is None: return 0
        try:
            if target_id in self.product_id_map:
                idx = self.product_id_map.index(target_id)
                # คืนค่าเฉลี่ยความสัมพันธ์ (ยิ่งสูงยิ่งดี)
                return np.mean(self.cf_matrix[idx]) 
            return 0
        except:
            return 0

    # ---------------------------------------------------------
    # 3️⃣ MAIN RECOMMENDATION LOGIC
    # ---------------------------------------------------------
    def recommend(self, skin_type, concerns, age, price_range=''):
        if self.df is None or self.df.empty: return []

        print(f"\n🔍 Processing Request: Skin={skin_type}, Concerns={concerns}, Price={price_range}")

        # --- Step 1: Content-Based Search ---
        user_query = f"{skin_type} {' '.join(concerns)}"
        user_vector = self.vectorizer.transform([user_query])
        cb_scores = cosine_similarity(user_vector, self.tfidf_matrix).flatten()
        
        final_results = []
        
        for idx, cb_score in enumerate(cb_scores):
            row = self.df.iloc[idx]
            product_id = row.get('id')
            
            # --- Step 2: Filtering ---
            # Skin Type Filter
            row_skin = str(row.get('skintype', '')).lower()
            user_skin = skin_type.lower()
            
            is_skin_match = False
            if user_skin == 'all' or user_skin in row_skin or 'all' in row_skin or 'ทุกสภาพผิว' in row_skin:
                is_skin_match = True
            
            # Price Filter
            is_price_match = self._check_price_match(row.get('price (bath)', 0), price_range)

            if is_skin_match and is_price_match:
                # --- Step 3: ⚖️ HYBRID SCORING ---
                
                # A. Content Score (0-100)
                score_content = cb_score * 100 
                
                # B. Collaborative Score (0-100)
                score_collab = self._get_collaborative_score(product_id) * 100 

                # ⭐ DEBUG PRINT: เช็คว่า ID ตรงกันไหม ⭐
                if score_collab > 0:
                     print(f"   ✅ Collab Hit! ID: {product_id} ({row['name'][:20]}...) -> Score: {score_collab:.2f}")

                # C. Rating Score (0-100)
                # ----------------------------------------------------
                try:
                    # ✅ 1. แปลง ID ให้เป็น Integer แน่นอนก่อนค้นหา
                    # (เผื่อมันมาเป็น 53.0 หรือ "53" จะได้แก้ให้เป็น 53)
                    lookup_id = int(product_id) 
                    
                    # ✅ 2. ค้นหาจากตัวแปรที่เตรียมไว้
                    avg_star = self.product_avg_ratings.get(lookup_id, 0)

                    # ⭐ Debug: ถ้าเป็นสินค้าตัวปัญหา ให้ปริ้นบอกเราหน่อย
                    if lookup_id in [26, 53, 75]:
                        print(f"   🔍 Debug ID: {lookup_id} -> Found Rating: {avg_star}")
                        
                except Exception as e:
                    # กันเหนียว กรณี ID เป็นค่าแปลกๆ แปลงเป็น int ไม่ได้
                    avg_star = 0
                    print(f"   ⚠️ Error lookup rating for ID {product_id}: {e}")

                score_rating = avg_star * 20 
                # ---------------------------------------------------- 

                # D. Final Weighted Score
                val_content = score_content * 0.6  
                val_rating = score_rating * 0.2    
                val_collab = score_collab * 0.2    
                
                total_score = val_content + val_rating + val_collab

                # --- Step 4: Formatting Result ---
                if total_score > 10: 
                    props = str(row.get('คุณสมบัติ(จากactive ingredients)', ''))
                    full_text = f"{props} {row['name']} {row_skin}"
                    benefits = self._analyze_benefits(full_text)

                    final_results.append({
                        'id': int(product_id),
                        'name': row['name'],
                        'brand': row['brand'],
                        'type': str(row.get('type_of_product', '')),
                        'price': float(str(row.get('price (bath)', 0)).replace(',','')),
                        'score': int(total_score),
                        'match_percent': int(total_score),
                        
                        'analysis': {
                            'skin_match': round(val_content, 1),
                            'quality': round(val_rating, 1),
                            'trend': round(val_collab, 1)
                        },
                        
                        'routine_step': self._get_routine_step(row['type_of_product']),
                        'acne_score': benefits['acne'],
                        'brightening_score': benefits['brightening'],
                        'moisturizing_score': benefits['moisturizing'],
                        'anti_aging_score': benefits['aging'],
                        'gentle_score': benefits['gentle'],
                        'highlights': self._get_highlights(props)
                    })

        # --- Step 5: Sorting & Selection ---
        final_results.sort(key=lambda x: x['score'], reverse=True)
        
        routine_picks = {}
        for item in final_results:
            step = item['routine_step']
            if step not in routine_picks:
                routine_picks[step] = item
            elif len(routine_picks) >= 6:
                break
                
        recommended_list = list(routine_picks.values())
        recommended_list.sort(key=lambda x: x['routine_step'])
        
        return recommended_list

    # ---------------------------------------------------------
    # 4️⃣ HELPER FUNCTIONS
    # ---------------------------------------------------------
    def _analyze_benefits(self, text):
        text = str(text).lower()
        scores = { 'acne': 4, 'brightening': 4, 'moisturizing': 4, 'aging': 4, 'gentle': 4 }
        
        keywords = {
            'acne': ['สิว', 'มัน', 'อุดตัน', 'รูขุมขน', 'acne', 'bha', 'pore', 'zinc', 'oil control', 'salicylic'],
            'brightening': ['ขาว', 'ใส', 'จุดด่างดำ', 'หมองคล้ำ', 'ฝ้า', 'white', 'bright', 'vit c', 'niacinamide', 'arbutin', 'glow'],
            'moisturizing': ['ชุ่มชื้น', 'แห้ง', 'ขาดน้ำ', 'ฉ่ำ', 'hydrat', 'moist', 'hyaluron', 'ceramide', 'aloe'],
            'aging': ['ริ้วรอย', 'เหี่ยวย่น', 'ตึง', 'age', 'wrinkle', 'retinol', 'collagen', 'peptide', 'firm', 'lift'],
            'gentle': ['แพ้', 'อ่อนโยน', 'sensitive', 'gentle', 'sooth', 'cica', 'centella', 'calm', 'barrier', 'free']
        }
        
        for key, words in keywords.items():
            for word in words:
                if word in text: scores[key] += 2 
            scores[key] = min(scores[key], 10)
        return scores

    def _get_routine_step(self, product_type):
        pt_lower = str(product_type).lower()
        for key, step in ROUTINE_MAP.items():
            if key in pt_lower: return step
        return 6

    def _get_highlights(self, props_text):
        text = str(props_text).strip()
        if not text or text.lower() == 'nan': 
            return []
        return text.replace(',', ' ').split()[:3]
        
    def _check_price_match(self, price, price_range):
        try:
            if not price_range or price_range == 'any': return True
            p = float(str(price).replace(',', ''))
            if price_range == 'low': return p < 500
            if price_range == 'medium': return 500 <= p <= 1500
            if price_range == 'high': return p > 1500
            return True 
        except:
            return False