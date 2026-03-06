import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from database.repository import get_all_products


ROUTINE_STEPS = [
    { "step": 1, "label": "ล้างหน้า",        "icon": "🧼", "categories": ["cleanser"] },
    { "step": 2, "label": "โทนเนอร์",         "icon": "💦", "categories": ["toner"] },
    { "step": 3, "label": "เซรั่ม",           "icon": "✨", "categories": ["serum", "treatment"] },
    { "step": 4, "label": "มอยส์เจอไรเซอร์", "icon": "🔒", "categories": ["moisturizer", "eye_care"] },
    { "step": 5, "label": "กันแดด",           "icon": "☀️", "categories": ["sunscreen"] },
]

RETURN_COLS = ['name', 'brand', 'major_category', 'subtype',
               'skintype', 'function_tags', 'image_url', 'price', 'final_score']


class DataLoader:

    def __init__(self):
        self.df = None
        self.vectorizer = None
        self.tfidf_matrix = None
        self._build()

    def _build(self):
        rows = get_all_products()
        if not rows:
            print("⚠️  No products found in DB")
            return

        df = pd.DataFrame(rows)
        df['price'] = pd.to_numeric(df['price'], errors='coerce').fillna(0)

        for col in ['skintype', 'function_tags', 'major_category', 'brand', 'ingredients_list', 'subtype']:
            if col not in df.columns:
                df[col] = ""
            else:
                df[col] = df[col].fillna("")

        df['combined_features'] = (
            df['skintype'] + " " +
            df['function_tags'] + " " +
            df['major_category'] + " " +
            df['brand'] + " " +
            df['ingredients_list']
        )

        self.df = df
        self.vectorizer = TfidfVectorizer(analyzer='char_wb', ngram_range=(3, 5))
        self.tfidf_matrix = self.vectorizer.fit_transform(df['combined_features'])
        print(f"✅ AI Engine ready — {len(df):,} products loaded")

    def _score(self, df, skin_type, concerns, min_price, max_price):
        """คำนวณ score กรองราคา + TF-IDF + skin boost"""
        has_price = df['price'] > 0
        filtered = pd.concat([
            df[has_price & (df['price'] >= min_price) & (df['price'] <= max_price)],
            df[~has_price]
        ]).copy()

        if filtered.empty:
            return filtered

        user_text = skin_type + " " + " ".join(concerns)
        user_vec = self.vectorizer.transform([user_text])
        indices = filtered.index
        scores = cosine_similarity(user_vec, self.tfidf_matrix[indices]).flatten()

        filtered['cosine_score'] = scores
        filtered['skin_boost'] = filtered['skintype'].apply(
            lambda x: 0.2 if skin_type.lower() in str(x).lower() else 0
        )
        filtered['final_score'] = filtered['cosine_score'] * 0.7 + filtered['skin_boost']
        return filtered

    def recommend_products(self, skin_type, concerns, min_price=0, max_price=100000, top_n=5):
        if self.df is None:
            return []

        scored = self._score(self.df.copy(), skin_type, concerns, min_price, max_price)
        if scored.empty:
            return []

        results = scored.sort_values('final_score', ascending=False).head(top_n)
        return results[RETURN_COLS].to_dict(orient='records')

    def recommend_routine(self, skin_type, concerns, min_price=0, max_price=100000):
        """
        ส่งคืน routine เรียง step 1-5
        แต่ละ step หยิบสินค้าที่ match ที่สุด 1 ชิ้น
        ถ้า category นั้นไม่มีในข้อมูล → ข้ามไป
        """
        if self.df is None:
            return []

        df = self.df.copy()
        scored = self._score(df, skin_type, concerns, min_price, max_price)
        if scored.empty:
            return []

        routine = []
        for step_info in ROUTINE_STEPS:
            cats = step_info["categories"]
            step_df = scored[scored['major_category'].isin(cats)]

            if step_df.empty:
                continue

            best = step_df.sort_values('final_score', ascending=False).iloc[0]
            product = best[RETURN_COLS].to_dict()
            product['step'] = step_info['step']
            product['step_label'] = step_info['label']
            product['step_icon'] = step_info['icon']
            routine.append(product)

        return routine

    def search_products(self, query, top_n=10):
        if self.df is None:
            return []

        df = self.df.copy()
        q = query.lower().strip()

        name_match = df[
            df['name'].str.lower().str.contains(q, na=False) |
            df['brand'].str.lower().str.contains(q, na=False)
        ].copy()

        if not name_match.empty:
            results = name_match.head(top_n)
        else:
            user_vec = self.vectorizer.transform([q])
            scores = cosine_similarity(user_vec, self.tfidf_matrix).flatten()
            df = df.copy()
            df['score'] = scores
            results = df.sort_values('score', ascending=False).head(top_n)

        return results[[
            'name', 'brand', 'major_category', 'subtype',
            'skintype', 'function_tags', 'image_url', 'price'
        ]].to_dict(orient='records')