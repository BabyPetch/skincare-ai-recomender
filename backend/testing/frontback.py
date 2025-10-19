# -*- coding: utf-8 -*-
from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MinMaxScaler
import os
from dotenv import load_dotenv

# สำหรับ NLP
try:
    import openai
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False

load_dotenv()

app = Flask(__name__)
CORS(app)

DATA_FILE = Path('backend\data\Data_Collection_ASA - data.csv')

class HybridSkinCareRecommender:
    def __init__(self):
        self.df = None
        self.tfidf_matrix = None
        self.content_sim_matrix = None
        self.user_ratings = None
        self.load_data()
        self.prepare_content_based()
        self.simulate_user_ratings()
    
    def load_data(self):
        try:
            self.df = pd.read_csv(DATA_FILE, encoding='utf-8-sig')
        except Exception as e:
            print(f"Error loading data: {e}")
            raise
    
    def prepare_content_based(self):
        self.df['combined_features'] = (
            self.df['skintype'].fillna('') + ' ' +
            self.df['type_of_product'].fillna('') + ' ' +
            self.df['ingredients'].fillna('') + ' ' +
            self.df['active ingredients'].fillna('') + ' ' +
            self.df['คุณสมบัติ(จากactive ingredients)'].fillna('') + ' ' +
            self.df['brand'].fillna('')
        )
        
        tfidf = TfidfVectorizer(
            max_features=200,
            stop_words=None,
            ngram_range=(1, 2)
        )
        
        self.tfidf_matrix = tfidf.fit_transform(self.df['combined_features'])
        self.content_sim_matrix = cosine_similarity(self.tfidf_matrix, self.tfidf_matrix)
    
    def simulate_user_ratings(self):
        np.random.seed(42)
        n_users = 50
        n_products = len(self.df)
        
        ratings = np.zeros((n_users, n_products))
        
        for user in range(n_users):
            n_rated = np.random.randint(5, 11)
            rated_products = np.random.choice(n_products, n_rated, replace=False)
            
            for prod_idx in rated_products:
                base_rating = np.random.uniform(3, 5)
                ratings[user, prod_idx] = base_rating
        
        self.user_ratings = ratings
    
    def hybrid_recommend(self, user_id, skin_type, product_preferences=None, n_recommendations=10):
        df_filtered = self.df[
            self.df['skintype'].fillna('').str.contains(skin_type, case=False, na=False)
        ].copy()
        
        if len(df_filtered) == 0:
            return None
        
        content_scores = np.zeros(len(self.df))
        if product_preferences:
            for pref in product_preferences:
                matches = self.df[self.df['name'].str.contains(pref, case=False, na=False)]
                if len(matches) > 0:
                    prod_idx = matches.index[0]
                    sim_scores = self.content_sim_matrix[prod_idx]
                    content_scores += sim_scores
            content_scores = content_scores / len(product_preferences) if product_preferences else content_scores
        
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
        
        scaler = MinMaxScaler()
        if content_scores.max() > 0:
            content_scores = scaler.fit_transform(content_scores.reshape(-1, 1)).flatten()
        if cf_scores.max() > 0:
            cf_scores = scaler.fit_transform(cf_scores.reshape(-1, 1)).flatten()
        
        hybrid_scores = 0.6 * content_scores + 0.4 * cf_scores
        
        for idx in df_filtered.index:
            hybrid_scores[idx] += 0.2
        
        top_indices = hybrid_scores.argsort()[-n_recommendations*2:][::-1]
        top_indices = [idx for idx in top_indices if idx in df_filtered.index][:n_recommendations]
        
        results = self.df.iloc[top_indices].copy()
        results['hybrid_score'] = [hybrid_scores[idx] for idx in top_indices]
        
        return results.to_dict('records')

# Initialize recommender
recommender = HybridSkinCareRecommender()

class NLPAnalyzer:
    """วิเคราะห์ข้อความโดยใช้ AI"""
    
    @staticmethod
    def extract_skin_info(user_text):
        """
        แยกข้อมูลประเภทผิวและปัญหาจากข้อความ
        ใช้ keyword matching เพื่อความเรียบง่าย
        (ในงานจริงควรใช้ OpenAI/Ollama)
        """
        user_text = user_text.lower()
        
        # Skin type mapping
        skin_types = {
            'oily': ['มัน', 'oily', 'ความมัน'],
            'dry': ['แห้ง', 'dry', 'ความแห้ง'],
            'combination': ['ผสม', 'combination', 'mixed'],
            'normal': ['ปกติ', 'normal', 'สุขภาพดี'],
            'sensitive': ['แพ้ง่าย', 'sensitive', 'แพ้', 'บอบบาง']
        }
        
        # Skin problem mapping
        skin_problems = {
            'acne': ['สิ่ว', 'acne', '痘', 'บุ่ม'],
            'wrinkles': ['ริ้วรอย', 'wrinkles', 'ริ้ว'],
            'dark_spots': ['จุดด่างดำ', 'dark spots', 'ฝ้า'],
            'dryness': ['ความแห้ง', 'dryness', 'ลอก'],
        }
        
        detected_skin_type = 'normal'
        detected_problems = []
        
        for skin_type, keywords in skin_types.items():
            if any(kw in user_text for kw in keywords):
                detected_skin_type = skin_type
                break
        
        for problem, keywords in skin_problems.items():
            if any(kw in user_text for kw in keywords):
                detected_problems.append(problem)
        
        return {
            'skin_type': detected_skin_type,
            'problems': detected_problems,
            'confidence': 0.75
        }
    
    @staticmethod
    def extract_preferences(user_text):
        """แยกแบรนด์หรือผลิตภัณฑ์ที่เคยใช้"""
        brands = ['CeraVe', 'Cetaphil', 'Neutrogena', 'Eucerin', 'La Roche-Posay']
        found_brands = []
        
        for brand in brands:
            if brand.lower() in user_text.lower():
                found_brands.append(brand)
        
        return found_brands

@app.route('/api/analyze', methods=['POST'])
def analyze_text():
    """
    Endpoint: รับข้อความจาก frontend และวิเคราะห์
    
    Request JSON:
    {
        "text": "ผิวของฉันมันและมีสิ่วเยอะ ต้องใช้อะไรดี",
        "user_id": 5
    }
    """
    try:
        data = request.json
        user_text = data.get('text', '')
        user_id = data.get('user_id', 5)
        
        if not user_text:
            return jsonify({'error': 'ข้อความว่างเปล่า'}), 400
        
        # วิเคราะห์ข้อความ
        skin_info = NLPAnalyzer.extract_skin_info(user_text)
        preferences = NLPAnalyzer.extract_preferences(user_text)
        
        # ได้คำแนะนำ
        recommendations = recommender.hybrid_recommend(
            user_id=user_id,
            skin_type=skin_info['skin_type'],
            product_preferences=preferences if preferences else None,
            n_recommendations=10
        )
        
        return jsonify({
            'status': 'success',
            'analysis': {
                'skin_type': skin_info['skin_type'],
                'problems': skin_info['problems'],
                'detected_brands': preferences,
                'confidence': skin_info['confidence']
            },
            'recommendations': recommendations,
            'count': len(recommendations) if recommendations else 0
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/products', methods=['GET'])
def get_products():
    """ดึงรายการผลิตภัณฑ์ทั้งหมด"""
    try:
        products = recommender.df.to_dict('records')
        return jsonify({
            'status': 'success',
            'products': products,
            'count': len(products)
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/skin-types', methods=['GET'])
def get_skin_types():
    """ดึงประเภทผิวที่มีอยู่"""
    try:
        skin_types = recommender.df['skintype'].unique().tolist()
        return jsonify({
            'status': 'success',
            'skin_types': [st for st in skin_types if pd.notna(st)]
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    """ตรวจสอบสถานะ API"""
    return jsonify({'status': 'ok', 'message': 'API is running'}), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)