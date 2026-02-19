from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


class Recommender:

    def __init__(self, df):
        self.df = df.copy()

        self.df['combined_features'] = (
            self.df['skintype'].fillna('') + " " +
            self.df['benefits'].fillna('') + " " +
            self.df['category'].fillna('') + " " +
            self.df['brand'].fillna('') + " " +
            self.df['ingredients'].fillna('')
        )

        self.vectorizer = TfidfVectorizer(
            analyzer='char_wb',
            ngram_range=(3, 5)
        )

        self.tfidf_matrix = self.vectorizer.fit_transform(
            self.df['combined_features']
        )

    def recommend(self, skin_type, concerns, min_price, max_price, top_n=5):

        filtered_df = self.df[
            (self.df['price'] >= min_price) &
            (self.df['price'] <= max_price)
        ].copy()

        if filtered_df.empty:
            return []

        user_text = skin_type + " " + " ".join(concerns)
        user_vec = self.vectorizer.transform([user_text])

        indices = filtered_df.index

        cosine_scores = cosine_similarity(
            user_vec,
            self.tfidf_matrix[indices]
        ).flatten()

        filtered_df['cosine_score'] = cosine_scores

        # 🔥 1️⃣ Skin type boost
        filtered_df['skin_boost'] = filtered_df['skintype'].apply(
            lambda x: 0.2 if skin_type.lower() in str(x).lower() else 0
        )

        # 🔥 2️⃣ Price normalization (ถูกกว่าได้คะแนนเพิ่มเล็กน้อย)
        price_range = max_price - min_price if max_price > min_price else 1
        filtered_df['price_score'] = 1 - (
            (filtered_df['price'] - min_price) / price_range
        )

        # 🔥 3️⃣ Final Score
        filtered_df['final_score'] = (
            filtered_df['cosine_score'] * 0.7 +
            filtered_df['skin_boost'] +
            filtered_df['price_score'] * 0.1
        )

        results = filtered_df.sort_values(
            by='final_score',
            ascending=False
        ).head(top_n)

        return results.to_dict(orient="records")
