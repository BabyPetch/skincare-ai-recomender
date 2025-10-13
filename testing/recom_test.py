# -*- coding: utf-8 -*-
import sys
import io
import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MinMaxScaler

# ตั้งค่า encoding
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

DATA_FILE = Path('data/Data_Collection_ASA - data.csv')  

class HybridSkinCareRecommender:
    """ระบบแนะนำแบบ Hybrid (Content-Based + Collaborative Filtering)"""
    
    def __init__(self):
        self.df = None
        self.tfidf_matrix = None
        self.content_sim_matrix = None
        self.user_ratings = None  # จะจำลองข้อมูล ratings
        self.load_data()
        self.prepare_content_based()
        self.simulate_user_ratings()
    
    def load_data(self):
        """โหลดข้อมูล"""
        try:
            self.df = pd.read_csv(DATA_FILE, encoding='utf-8-sig')
            print(f"✓ โหลดข้อมูลสำเร็จ: {len(self.df)} ผลิตภัณฑ์\n")
        except Exception as e:
            print(f"✗ เกิดข้อผิดพลาด: {e}")
            sys.exit(1)
    
    def prepare_content_based(self):
        """เตรียมข้อมูลสำหรับ Content-Based Filtering"""
        print("🔄 กำลังเตรียม Content-Based Model...")
        
        # รวมข้อมูลทั้งหมดเป็น text features
        self.df['combined_features'] = (
            self.df['skintype'].fillna('') + ' ' +
            self.df['type_of_product'].fillna('') + ' ' +
            self.df['ingredients'].fillna('') + ' ' +
            self.df['active ingredients'].fillna('') + ' ' +
            self.df['คุณสมบัติ(จากactive ingredients)'].fillna('') + ' ' +
            self.df['brand'].fillna('')
        )
        
        # สร้าง TF-IDF Matrix
        tfidf = TfidfVectorizer(
            max_features=200,
            stop_words=None,  # ไม่ใช้ stop words เพราะมีทั้งไทยและอังกฤษ
            ngram_range=(1, 2)  # unigram และ bigram
        )
        
        self.tfidf_matrix = tfidf.fit_transform(self.df['combined_features'])
        
        # คำนวณ Cosine Similarity
        self.content_sim_matrix = cosine_similarity(self.tfidf_matrix, self.tfidf_matrix)
        
        print("✓ Content-Based Model พร้อมใช้งาน\n")
    
    def simulate_user_ratings(self):
        """จำลองข้อมูล user ratings (สำหรับ Collaborative Filtering)"""
        print("🔄 กำลังจำลองข้อมูล User Ratings...")
        
        # สร้างข้อมูล user ratings แบบสุ่ม (ปกติจะได้จาก database)
        np.random.seed(42)
        n_users = 50  # จำลอง 50 users
        n_products = len(self.df)
        
        # สร้าง sparse matrix (user x product)
        # ส่วนใหญ่จะเป็น 0 (ยังไม่ได้ให้คะแนน)
        ratings = np.zeros((n_users, n_products))
        
        # แต่ละ user ให้คะแนนประมาณ 5-10 ผลิตภัณฑ์
        for user in range(n_users):
            n_rated = np.random.randint(5, 11)
            rated_products = np.random.choice(n_products, n_rated, replace=False)
            
            # ให้คะแนน 1-5 แบบมี bias ตามประเภทผิว
            for prod_idx in rated_products:
                # ถ้า user ชอบผิวมัน และสินค้าเหมาะกับผิวมัน -> คะแนนสูง
                base_rating = np.random.uniform(3, 5)
                ratings[user, prod_idx] = base_rating
        
        self.user_ratings = ratings
        print("✓ สร้างข้อมูล User Ratings สำเร็จ (50 users)\n")
    
    def content_based_recommend(self, product_idx, n_recommendations=10):
        """
        Content-Based Filtering: แนะนำสินค้าที่คล้ายกัน
        
        Args:
            product_idx: index ของผลิตภัณฑ์ที่ชอบ
            n_recommendations: จำนวนผลิตภัณฑ์ที่แนะนำ
        """
        # หาความคล้ายกัน
        similarity_scores = list(enumerate(self.content_sim_matrix[product_idx]))
        
        # เรียงตามคะแนน (ไม่รวมตัวเอง)
        similarity_scores = sorted(similarity_scores, key=lambda x: x[1], reverse=True)
        similarity_scores = similarity_scores[1:n_recommendations+1]
        
        # ดึง indices
        product_indices = [i[0] for i in similarity_scores]
        scores = [i[1] for i in similarity_scores]
        
        # สร้าง DataFrame ผลลัพธ์
        results = self.df.iloc[product_indices].copy()
        results['similarity_score'] = scores
        results['recommendation_method'] = 'Content-Based'
        
        return results
    
    def collaborative_filtering_recommend(self, user_id, n_recommendations=10):
        """
        Collaborative Filtering: แนะนำตาม user ที่คล้ายกัน
        
        Args:
            user_id: ID ของผู้ใช้
            n_recommendations: จำนวนผลิตภัณฑ์ที่แนะนำ
        """
        if user_id >= len(self.user_ratings):
            print("❌ User ID ไม่ถูกต้อง")
            return None
        
        # คำนวณความคล้ายกันระหว่าง users (User-User CF)
        user_similarity = cosine_similarity(self.user_ratings)
        
        # หา users ที่คล้ายกัน
        similar_users = user_similarity[user_id]
        
        # ทำนายคะแนนสำหรับผลิตภัณฑ์ที่ user ยังไม่ได้ให้คะแนน
        user_ratings_vector = self.user_ratings[user_id]
        predicted_ratings = np.zeros(len(self.df))
        
        for prod_idx in range(len(self.df)):
            if user_ratings_vector[prod_idx] == 0:  # ยังไม่ได้ให้คะแนน
                # ใช้ weighted average จาก similar users
                numerator = 0
                denominator = 0
                
                for other_user in range(len(self.user_ratings)):
                    if other_user != user_id and self.user_ratings[other_user, prod_idx] > 0:
                        numerator += similar_users[other_user] * self.user_ratings[other_user, prod_idx]
                        denominator += abs(similar_users[other_user])
                
                if denominator > 0:
                    predicted_ratings[prod_idx] = numerator / denominator
        
        # หาผลิตภัณฑ์ที่มีคะแนนทำนายสูงสุด
        top_indices = predicted_ratings.argsort()[-n_recommendations:][::-1]
        
        # กรองเฉพาะที่มีคะแนนมากกว่า 0
        top_indices = [idx for idx in top_indices if predicted_ratings[idx] > 0]
        
        if len(top_indices) == 0:
            print("⚠️  ไม่พบข้อมูลเพียงพอสำหรับ Collaborative Filtering")
            return None
        
        results = self.df.iloc[top_indices].copy()
        results['predicted_rating'] = [predicted_ratings[idx] for idx in top_indices]
        results['recommendation_method'] = 'Collaborative Filtering'
        
        return results
    
    def hybrid_recommend(self, user_id, skin_type, product_preferences=None, n_recommendations=10):
        """
        Hybrid Recommender: ผสม Content-Based + Collaborative Filtering + Rules
        
        Args:
            user_id: ID ของผู้ใช้ (สำหรับ CF)
            skin_type: ประเภทผิว (สำหรับ filtering)
            product_preferences: ผลิตภัณฑ์ที่เคยชอบ (list of product names)
            n_recommendations: จำนวนผลิตภัณฑ์ที่แนะนำ
        """
        print(f"\n🔄 กำลังประมวลผล Hybrid Recommendation...")
        
        # 1. กรองตามประเภทผิว
        df_filtered = self.df[
            self.df['skintype'].fillna('').str.contains(skin_type, case=False, na=False)
        ].copy()
        
        if len(df_filtered) == 0:
            print("❌ ไม่พบผลิตภัณฑ์สำหรับประเภทผิวนี้")
            return None
        
        # 2. Content-Based Score
        content_scores = np.zeros(len(self.df))
        if product_preferences:
            for pref in product_preferences:
                matches = self.df[self.df['name'].str.contains(pref, case=False, na=False)]
                if len(matches) > 0:
                    prod_idx = matches.index[0]
                    sim_scores = self.content_sim_matrix[prod_idx]
                    content_scores += sim_scores
            content_scores = content_scores / len(product_preferences) if product_preferences else content_scores
        
        # 3. Collaborative Filtering Score
        cf_scores = np.zeros(len(self.df))
        if user_id < len(self.user_ratings):
            user_similarity = cosine_similarity(self.user_ratings)
            similar_users = user_similarity[user_id]
            user_ratings_vector = self.user_ratings[user_id]
            
            for prod_idx in range(len(self.df)):
                if user_ratings_vector[prod_idx] == 0:
                    numerator = 0
                    denominator = 0
                    
                    for other_user in range(len(self.user_ratings)):
                        if other_user != user_id and self.user_ratings[other_user, prod_idx] > 0:
                            numerator += similar_users[other_user] * self.user_ratings[other_user, prod_idx]
                            denominator += abs(similar_users[other_user])
                    
                    if denominator > 0:
                        cf_scores[prod_idx] = numerator / denominator
        
        # 4. Normalize scores
        scaler = MinMaxScaler()
        if content_scores.max() > 0:
            content_scores = scaler.fit_transform(content_scores.reshape(-1, 1)).flatten()
        if cf_scores.max() > 0:
            cf_scores = scaler.fit_transform(cf_scores.reshape(-1, 1)).flatten()
        
        # 5. Hybrid Score (weighted combination)
        # Content-Based: 60%, Collaborative: 40%
        hybrid_scores = 0.6 * content_scores + 0.4 * cf_scores
        
        # เพิ่มคะแนนให้ผลิตภัณฑ์ที่อยู่ใน df_filtered
        for idx in df_filtered.index:
            hybrid_scores[idx] += 0.2  # bonus สำหรับผลิตภัณฑ์ที่ตรงกับประเภทผิว
        
        # 6. เรียงตามคะแนน
        top_indices = hybrid_scores.argsort()[-n_recommendations*2:][::-1]  # เอาเผื่อไว้
        
        # กรองเฉพาะที่อยู่ใน df_filtered
        top_indices = [idx for idx in top_indices if idx in df_filtered.index][:n_recommendations]
        
        results = self.df.iloc[top_indices].copy()
        results['content_score'] = [content_scores[idx] for idx in top_indices]
        results['cf_score'] = [cf_scores[idx] for idx in top_indices]
        results['hybrid_score'] = [hybrid_scores[idx] for idx in top_indices]
        results['recommendation_method'] = 'Hybrid'
        
        return results

def display_recommendations(df, title="ผลการแนะนำ", show_scores=True):
    """แสดงผลลัพธ์"""
    if df is None or len(df) == 0:
        print("❌ ไม่พบผลิตภัณฑ์ที่แนะนำ")
        return
    
    print("\n" + "=" * 100)
    print(f"🌟 {title}")
    print("=" * 100)
    
    for rank, (idx, row) in enumerate(df.iterrows(), 1):
        medal = '🥇' if rank == 1 else '🥈' if rank == 2 else '🥉' if rank == 3 else f'#{rank}'
        
        print(f"\n{medal} {row['name']}")
        print(f"     💼 แบรนด์: {row['brand']}")
        print(f"     📦 ประเภท: {row['type_of_product']}")
        print(f"     🧴 เหมาะสำหรับ: {row['skintype']}")
        print(f"     💰 ราคา: {row['price (bath)']} บาท")
        
        if show_scores and 'recommendation_method' in row:
            print(f"     🔬 วิธีการแนะนำ: {row['recommendation_method']}")
            
            if 'similarity_score' in row and pd.notna(row['similarity_score']):
                print(f"     📊 ความคล้ายกัน: {row['similarity_score']:.2%}")
            
            if 'predicted_rating' in row and pd.notna(row['predicted_rating']):
                print(f"     ⭐ คะแนนทำนาย: {row['predicted_rating']:.2f}/5.0")
            
            if 'hybrid_score' in row and pd.notna(row['hybrid_score']):
                print(f"     🎯 Hybrid Score: {row['hybrid_score']:.3f}")
                if pd.notna(row.get('content_score')) and pd.notna(row.get('cf_score')):
                    print(f"        └─ Content: {row['content_score']:.3f} | CF: {row['cf_score']:.3f}")
        
        if pd.notna(row['active ingredients']):
            print(f"     ✨ {str(row['active ingredients'])[:80]}...")
    
    print("\n" + "=" * 100)
    print(f"💡 แสดง {len(df)} รายการ")
    print("=" * 100)

# ========================
# ตัวอย่างการใช้งาน
# ========================
if __name__ == '__main__':
    recommender = HybridSkinCareRecommender()
    
    print("=" * 100)
    print("🌟 ระบบแนะนำผลิตภัณฑ์ดูแลผิว - Content-Based & Collaborative Filtering")
    print("=" * 100)
    
    # ==========================
    # เลือกโหมดที่ต้องการ (1-4)
    # ==========================
    mode = 3  # เปลี่ยนได้
    
    if mode == 1:
        # โหมด 1: Content-Based Filtering
        print("\n📊 โหมด 1: Content-Based Filtering")
        print("หลักการ: แนะนำผลิตภัณฑ์ที่มีส่วนผสมและคุณสมบัติคล้ายกัน\n")
        
        # หาผลิตภัณฑ์ที่ต้องการเป็นตัวอย่าง
        sample_product = recommender.df[recommender.df['name'].str.contains('CeraVe', case=False, na=False)]
        
        if len(sample_product) > 0:
            product_idx = sample_product.index[0]
            product_name = sample_product.iloc[0]['name']
            
            print(f"🔍 ค้นหาผลิตภัณฑ์ที่คล้ายกับ: {product_name}\n")
            
            results = recommender.content_based_recommend(product_idx, n_recommendations=5)
            display_recommendations(results, f"ผลิตภัณฑ์ที่คล้ายกับ {product_name}")
    
    elif mode == 2:
        # โหมด 2: Collaborative Filtering
        print("\n👥 โหมด 2: Collaborative Filtering")
        print("หลักการ: แนะนำตามผู้ใช้ที่มีความชอบคล้ายกัน\n")
        
        user_id = 5  # เปลี่ยน user ID ได้ (0-49)
        print(f"🔍 แนะนำสำหรับ User #{user_id}\n")
        
        results = recommender.collaborative_filtering_recommend(user_id, n_recommendations=5)
        if results is not None:
            display_recommendations(results, f"แนะนำสำหรับ User #{user_id}")
    
    elif mode == 3:
        # โหมด 3: Hybrid Recommendation (แนะนำ!)
        print("\n🎯 โหมด 3: Hybrid Recommendation")
        print("หลักการ: ผสม Content-Based (60%) + Collaborative Filtering (40%)\n")
        
        user_id = 10  # เปลี่ยนได้
        skin_type = 'oily'  # oily, dry, normal, combination, sensitive
        product_preferences = ['CeraVe', 'Cetaphil']  # ผลิตภัณฑ์ที่เคยชอบ
        
        print(f"📋 ข้อมูลผู้ใช้:")
        print(f"   - User ID: {user_id}")
        print(f"   - ประเภทผิว: {skin_type}")
        print(f"   - ผลิตภัณฑ์ที่เคยชอบ: {', '.join(product_preferences)}")
        
        results = recommender.hybrid_recommend(
            user_id=user_id,
            skin_type=skin_type,
            product_preferences=product_preferences,
            n_recommendations=10
        )
        
        if results is not None:
            display_recommendations(results, "ผลการแนะนำแบบ Hybrid")
            
            # บันทึกผลลัพธ์
            output_dir = Path('Datasaver')
            output_dir.mkdir(parents=True, exist_ok=True)
            output_file = output_dir / f'hybrid_recommendation_user{user_id}_{skin_type}.csv'
            results.to_csv(output_file, index=False, encoding='utf-8-sig')
            print(f"\n💾 บันทึกผลลัพธ์ไว้ที่: {output_file}")
    
    elif mode == 4:
        # โหมด 4: เปรียบเทียบทั้ง 3 วิธี
        print("\n🔬 โหมด 4: เปรียบเทียบวิธีการแนะนำ")
        
        # Content-Based
        sample = recommender.df[recommender.df['skintype'].str.contains('oily', case=False, na=False)].iloc[0]
        cb_results = recommender.content_based_recommend(sample.name, n_recommendations=3)
        
        # Collaborative
        cf_results = recommender.collaborative_filtering_recommend(user_id=5, n_recommendations=3)
        
        # Hybrid
        hybrid_results = recommender.hybrid_recommend(
            user_id=5,
            skin_type='oily',
            product_preferences=['CeraVe'],
            n_recommendations=3
        )
        
        print("\n📊 Content-Based Top 3:")
        display_recommendations(cb_results, "Content-Based", show_scores=True)
        
        print("\n📊 Collaborative Filtering Top 3:")
        if cf_results is not None:
            display_recommendations(cf_results, "Collaborative Filtering", show_scores=True)
        
        print("\n📊 Hybrid Top 3:")
        if hybrid_results is not None:
            display_recommendations(hybrid_results, "Hybrid", show_scores=True)
    
    print("\n✨ ลองเปลี่ยนโหมด (mode = 1, 2, 3, 4) เพื่อทดสอบวิธีการแนะนำต่างๆ")