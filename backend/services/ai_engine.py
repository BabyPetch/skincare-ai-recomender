import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from database.repository import get_all_products


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

    def recommend_products(self, skin_type, concerns, min_price=0, max_price=100000, top_n=5):
        if self.df is None:
            return []

        df = self.df.copy()

        # กรองราคา (ถ้ามีราคา)
        has_price = df['price'] > 0
        price_filtered = df[has_price & (df['price'] >= min_price) & (df['price'] <= max_price)]
        no_price = df[~has_price]
        filtered_df = pd.concat([price_filtered, no_price])

        if filtered_df.empty:
            return []

        user_text = skin_type + " " + " ".join(concerns)
        user_vec = self.vectorizer.transform([user_text])

        indices = filtered_df.index
        cosine_scores = cosine_similarity(user_vec, self.tfidf_matrix[indices]).flatten()
        filtered_df = filtered_df.copy()
        filtered_df['cosine_score'] = cosine_scores

        # Skin type boost
        filtered_df['skin_boost'] = filtered_df['skintype'].apply(
            lambda x: 0.2 if skin_type.lower() in str(x).lower() else 0
        )

        filtered_df['final_score'] = filtered_df['cosine_score'] * 0.7 + filtered_df['skin_boost']

        results = filtered_df.sort_values('final_score', ascending=False).head(top_n)

        return results[[
            'name', 'brand', 'major_category', 'subtype',
            'skintype', 'function_tags', 'image_url', 'final_score'
        ]].to_dict(orient='records')