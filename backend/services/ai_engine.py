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

# ============================================================
#  CONTEXT BOOST RULES
#  tag → weight  (เช็คกับ function_tags ของแต่ละสินค้า)
# ============================================================

AGE_BOOST = {
    'teen':   {'acne_control': 0.20, 'gentle': 0.10, 'lightweight': 0.10},
    'young':  {'brightening': 0.10, 'antioxidant': 0.10, 'hydrating': 0.05},
    'adult':  {'anti_aging': 0.15, 'brightening': 0.10, 'barrier_repair': 0.05},
    'mature': {'anti_aging': 0.25, 'hydrating': 0.15, 'barrier_repair': 0.10},
    'senior': {'anti_aging': 0.30, 'hydrating': 0.20, 'barrier_repair': 0.15},
}

HYDRATION_BOOST = {
    'very_dry': {'hydrating': 0.25, 'barrier_repair': 0.20, 'ceramide': 0.15},
    'dry':      {'hydrating': 0.15, 'barrier_repair': 0.10},
    'normal':   {},
    'oily':     {'acne_control': 0.15, 'lightweight': 0.15, 'oil_control': 0.10},
}

ENV_BOOST = {
    'hot_humid':  {'lightweight': 0.15, 'oil_control': 0.15, 'acne_control': 0.10},
    'ac_all_day': {'hydrating': 0.20, 'barrier_repair': 0.15, 'ceramide': 0.10},
    'mixed':      {'hydrating': 0.10, 'lightweight': 0.10},
    'pollution':  {'antioxidant': 0.20, 'brightening': 0.10, 'barrier_repair': 0.10},
    'tropical':   {'sunscreen': 0.25, 'antioxidant': 0.15, 'lightweight': 0.10},
}

EXPERIENCE_BOOST = {
    'beginner':     {'gentle': 0.20, 'calming': 0.10, 'hydrating': 0.10},
    'intermediate': {'brightening': 0.10, 'hydrating': 0.05},
    'advanced':     {'anti_aging': 0.15, 'antioxidant': 0.15, 'exfoliating': 0.10},
}

ROUTINE_TIME_BOOST = {
    'morning': {'sunscreen': 0.20, 'lightweight': 0.10, 'antioxidant': 0.10},
    'evening': {'anti_aging': 0.15, 'barrier_repair': 0.15, 'hydrating': 0.10},
    'both':    {'hydrating': 0.05, 'barrier_repair': 0.05},
}


def _merge_boosts(*boost_dicts):
    merged = {}
    for d in boost_dicts:
        for tag, w in d.items():
            merged[tag] = merged.get(tag, 0) + w
    return merged


def _context_score(row, boost_map):
    if not boost_map:
        return 0.0
    tags = str(row.get('function_tags', '')).lower()
    return sum(w for tag, w in boost_map.items() if tag.lower() in tags)


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

    def _score(self, df, skin_type, concerns, min_price, max_price, context=None):
        """
        Final score = TF-IDF (50%) + skin_boost (15%) + context_rules (35%)
        """
        has_price = df['price'] > 0
        filtered = pd.concat([
            df[has_price & (df['price'] >= min_price) & (df['price'] <= max_price)],
            df[~has_price]
        ]).copy()

        if filtered.empty:
            return filtered

        # Layer 1: TF-IDF cosine
        user_text = skin_type + " " + " ".join(concerns)
        user_vec  = self.vectorizer.transform([user_text])
        indices   = filtered.index
        filtered['cosine_score'] = cosine_similarity(
            user_vec, self.tfidf_matrix[indices]
        ).flatten()

        # Layer 2: Skin type match
        filtered['skin_boost'] = filtered['skintype'].apply(
            lambda x: 0.15 if skin_type.lower() in str(x).lower() else 0
        )

        # Layer 3: Context rule-based
        ctx = context or {}
        boost_map = _merge_boosts(
            AGE_BOOST.get(ctx.get('age', ''), {}),
            HYDRATION_BOOST.get(ctx.get('hydration', ''), {}),
            ENV_BOOST.get(ctx.get('environment', ''), {}),
            EXPERIENCE_BOOST.get(ctx.get('experience', ''), {}),
            ROUTINE_TIME_BOOST.get(ctx.get('routine_time', ''), {}),
        )
        filtered['context_score'] = filtered.apply(
            lambda row: _context_score(row, boost_map), axis=1
        )

        filtered['final_score'] = (
            filtered['cosine_score']  * 0.50 +
            filtered['skin_boost']    * 0.15 +
            filtered['context_score'] * 0.35
        )

        return filtered

    def recommend_products(self, skin_type, concerns, min_price=0, max_price=100000,
                           top_n=5, context=None):
        if self.df is None:
            return []
        scored = self._score(self.df.copy(), skin_type, concerns,
                             min_price, max_price, context)
        if scored.empty:
            return []
        results = scored.sort_values('final_score', ascending=False).head(top_n)
        return results[RETURN_COLS].to_dict(orient='records')

    def recommend_routine(self, skin_type, concerns, min_price=0, max_price=100000,
                          context=None):
        if self.df is None:
            return []
        scored = self._score(self.df.copy(), skin_type, concerns,
                             min_price, max_price, context)
        if scored.empty:
            return []

        routine = []
        for step_info in ROUTINE_STEPS:
            step_df = scored[scored['major_category'].isin(step_info["categories"])]
            if step_df.empty:
                continue
            best            = step_df.sort_values('final_score', ascending=False).iloc[0]
            product         = best[RETURN_COLS].to_dict()
            product['step']       = step_info['step']
            product['step_label'] = step_info['label']
            product['step_icon']  = step_info['icon']
            routine.append(product)

        return routine

    def search_products(self, query, top_n=10):
        if self.df is None:
            return []
        df = self.df.copy()
        q  = query.lower().strip()

        name_match = df[
            df['name'].str.lower().str.contains(q, na=False) |
            df['brand'].str.lower().str.contains(q, na=False)
        ].copy()

        if not name_match.empty:
            return name_match.head(top_n)[[
                'name', 'brand', 'major_category', 'subtype',
                'skintype', 'function_tags', 'image_url', 'price'
            ]].to_dict(orient='records')

        user_vec    = self.vectorizer.transform([q])
        df['score'] = cosine_similarity(user_vec, self.tfidf_matrix).flatten()
        return df.sort_values('score', ascending=False).head(top_n)[[
            'name', 'brand', 'major_category', 'subtype',
            'skintype', 'function_tags', 'image_url', 'price'
        ]].to_dict(orient='records')