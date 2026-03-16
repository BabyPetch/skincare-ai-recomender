"""
ai_engine_v2.py — ใช้ trained model แทน rule-based lookup
"""
import json
import numpy as np
import pandas as pd
import joblib
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from database.repository import get_all_products

MODEL_DIR = Path(__file__).parent.parent / "training" / "model"

ROUTINE_STEPS = [
    { "step": 1, "label": "ล้างหน้า",        "icon": "🧼", "categories": ["cleanser","cleansing"] },
    { "step": 2, "label": "โทนเนอร์",         "icon": "💦", "categories": ["toner"] },
    { "step": 3, "label": "เซรั่ม",           "icon": "✨", "categories": ["serum","essence","ampoule"] },
    { "step": 4, "label": "มอยส์เจอไรเซอร์", "icon": "🔒", "categories": ["moisturizer","eye_care"] },
    { "step": 5, "label": "กันแดด",           "icon": "☀️", "categories": ["sunscreen"] },
]

RETURN_COLS = [
    'name','brand','major_category','subtype',
    'skintype','function_tags','image_url','price','final_score'
]

CONCERN_LABEL = {
    'acne_control':'สิว', 'brightening':'หมองคล้ำ/ฝ้า',
    'anti_aging':'ริ้วรอย', 'hydrating':'แห้งกร้าน',
    'barrier_repair':'ผิวเสีย/แพ้ง่าย', 'calming':'ผิวแดง/อักเสบ',
    'exfoliating':'รูขุมขนกว้าง', 'antioxidant':'ริ้วรอยดำ/กระ',
}

# concern (UI) → model categories
CONCERN_TO_MODEL = {
    'acne_control':   ['acne','oilcontrol','exfoliation','soothing'],
    'brightening':    ['whitening','antioxidant','hydration'],
    'anti_aging':     ['wrinkle','antioxidant','hydration'],
    'hydrating':      ['hydration','barrierrepair'],
    'barrier_repair': ['barrierrepair','soothing'],
    'calming':        ['barrierrepair','soothing'],
    'exfoliating':    ['oilcontrol','exfoliation'],
    'antioxidant':    ['whitening','exfoliation','antioxidant'],
}

ACTIVE_COL_LABEL = {
    'active_acne':'รักษาสิว', 'active_whitening':'ลดหมองคล้ำ/ฝ้า',
    'active_wrinkle':'ลดริ้วรอย', 'active_exfoliation':'ผลัดเซลล์ผิว',
    'active_hydration':'ให้ความชุ่มชื้น', 'active_barrier':'เสริมเกราะผิว',
    'active_soothing':'ลดการอักเสบ', 'active_oilct':'ควบคุมความมัน',
    'active_antioxidant':'ต้านอนุมูลอิสระ',
}

COL_MAP = {
    'acne':'active_acne','whitening':'active_whitening','wrinkle':'active_wrinkle',
    'exfoliation':'active_exfoliation','hydration':'active_hydration',
    'barrierrepair':'active_barrier','soothing':'active_soothing',
    'oilcontrol':'active_oilct','antioxidant':'active_antioxidant',
}

AGE_BOOST = {
    'teen':   {'acne_control':0.20,'hydrating':0.10},
    'young':  {'brightening':0.10,'antioxidant':0.10},
    'adult':  {'anti_aging':0.15,'brightening':0.10},
    'mature': {'anti_aging':0.25,'hydrating':0.15,'barrier_repair':0.10},
    'senior': {'anti_aging':0.30,'hydrating':0.20,'barrier_repair':0.15},
}
HYDRATION_BOOST = {
    'very_dry':{'hydrating':0.25,'barrier_repair':0.20},
    'dry':     {'hydrating':0.15,'barrier_repair':0.10},
    'normal':  {},
    'oily':    {'acne_control':0.15},
}
ENV_BOOST = {
    'hot_humid':  {'acne_control':0.10},
    'ac_all_day': {'hydrating':0.20,'barrier_repair':0.15},
    'mixed':      {'hydrating':0.10},
    'pollution':  {'antioxidant':0.20,'brightening':0.10},
    'tropical':   {'antioxidant':0.15},
}
EXPERIENCE_BOOST = {
    'beginner':    {'calming':0.10,'hydrating':0.10},
    'intermediate':{'brightening':0.10},
    'advanced':    {'anti_aging':0.15,'antioxidant':0.15,'exfoliating':0.10},
}
ROUTINE_TIME_BOOST = {
    'morning':{'antioxidant':0.10},
    'evening':{'anti_aging':0.15,'barrier_repair':0.15,'hydrating':0.10},
    'both':   {'hydrating':0.05,'barrier_repair':0.05},
}

def _merge_boosts(*dicts):
    out = {}
    for d in dicts:
        for k, v in d.items():
            out[k] = out.get(k, 0) + v
    return out

def _context_score(row, boost_map):
    if not boost_map: return 0.0
    tags = str(row.get('function_tags','')).lower()
    return sum(w for tag, w in boost_map.items() if tag.lower() in tags)

# ================================================================
# MODEL LOADER
# ================================================================
class ConcernModel:
    def __init__(self):
        self.model = None
        self.meta  = None
        self._ingr_index = {}
        self._load()

    def _load(self):
        model_path = MODEL_DIR / "concern_classifier.pkl"
        meta_path  = MODEL_DIR / "concern_meta.json"
        if not model_path.exists():
            print("⚠️  concern_classifier.pkl ไม่พบ — ใช้ rule-based แทน")
            return
        self.model = joblib.load(model_path)
        with open(meta_path, encoding="utf-8") as f:
            self.meta = json.load(f)
        self._ingr_index = {ing: i for i, ing in enumerate(self.meta['ingredients'])}
        print(f"✅ Concern model loaded ({len(self.meta['ingredients'])} ingredients)")

    def predict(self, ingredients_list_str, threshold=0.30):
        """
        returns dict: { model_category: confidence }
        e.g. {'acne': 0.82, 'oilcontrol': 0.71, 'soothing': 0.45}
        """
        if self.model is None:
            return {}
        ingrs = [i.strip().lower() for i in str(ingredients_list_str).split(',') if i.strip()]
        x = np.zeros(len(self.meta['ingredients']), dtype=np.float32)
        for ing in ingrs:
            if ing in self._ingr_index:
                x[self._ingr_index[ing]] = 1.0
        if x.sum() == 0:
            return {}
        proba = self.model.predict_proba(x.reshape(1, -1))[0]
        return {
            cat: round(float(proba[i]), 3)
            for i, cat in enumerate(self.meta['categories'])
            if proba[i] >= threshold
        }

    def concern_score(self, row, concerns, threshold=0.30):
        """
        คำนวณ concern score จาก model predictions
        นับ confidence ของ model categories ที่ map กับ UI concerns
        """
        pred = self.predict(row.get('ingredients_list',''), threshold)
        if not pred:
            return 0.0, {}

        total = 0.0
        matched = {}  # concern → [(model_cat, conf)]
        for concern in concerns:
            model_cats = CONCERN_TO_MODEL.get(concern, [])
            for mcat in model_cats:
                conf = pred.get(mcat, 0.0)
                if conf > 0:
                    total += conf * 0.15
                    if concern not in matched:
                        matched[concern] = []
                    matched[concern].append((mcat, conf))
        return min(total, 1.0), matched

# ================================================================
# EXPLANATION BUILDER
# ================================================================
def _build_explanation(row, skin_type, concerns, matched_concerns):
    reasons = []

    # 1. skin type
    if skin_type and skin_type.lower() in str(row.get('skintype','')).lower():
        reasons.append(f"เหมาะกับผิว {skin_type}")

    # 2. concern match (จาก model)
    for concern, cat_confs in matched_concerns.items():
        label = CONCERN_LABEL.get(concern, concern)
        # เอา active ingredients จริงๆ จาก column
        ingr_examples = []
        for mcat, conf in sorted(cat_confs, key=lambda x: -x[1])[:2]:
            col = COL_MAP.get(mcat, '')
            val = str(row.get(col, '') or '').strip()
            if val:
                top = [v.strip() for v in val.split(',') if v.strip()][:2]
                ingr_examples.extend(top)
        ingr_examples = list(dict.fromkeys(ingr_examples))[:3]
        if ingr_examples:
            reasons.append(f"ช่วย{label}: {', '.join(ingr_examples)}")
        else:
            reasons.append(f"ช่วย{label}")

    # 3. key ingredients
    key = str(row.get('key_ingredients','') or '').strip()
    if key:
        top = [v.strip() for v in key.split(',') if v.strip()][:3]
        if top:
            reasons.append(f"Key ingredients: {', '.join(top)}")

    # 4. free from
    free = str(row.get('free_from','') or '').strip()
    if free and free != 'NA':
        reasons.append(f"ปลอดภัย: {free}")

    return reasons

# ================================================================
# DATA LOADER + SCORING
# ================================================================
class DataLoader:
    def __init__(self):
        self.df           = None
        self.vectorizer   = None
        self.tfidf_matrix = None
        self.concern_model = ConcernModel()
        self._build()

    def _build(self):
        rows = get_all_products()
        if not rows:
            print("⚠️  No products in DB"); return

        df = pd.DataFrame(rows)
        df['price'] = pd.to_numeric(df['price'], errors='coerce').fillna(0)

        for col in ['skintype','function_tags','major_category','brand',
                    'ingredients_list','subtype','key_ingredients','free_from',
                    'active_acne','active_whitening','active_wrinkle',
                    'active_exfoliation','active_hydration','active_barrier',
                    'active_soothing','active_oilct','active_antioxidant']:
            df[col] = df[col].fillna('') if col in df.columns else ''

        df['combined_features'] = (
            df['skintype']         + " " +
            df['function_tags']    + " " +
            df['major_category']   + " " +
            df['brand']            + " " +
            df['ingredients_list'] + " " +
            df['active_acne']      + " " +
            df['active_whitening'] + " " +
            df['active_wrinkle']   + " " +
            df['active_hydration'] + " " +
            df['active_barrier']   + " " +
            df['active_soothing']
        )

        self.df = df
        self.vectorizer = TfidfVectorizer(analyzer='char_wb', ngram_range=(3,5))
        self.tfidf_matrix = self.vectorizer.fit_transform(df['combined_features'])
        print(f"✅ AI Engine v2 ready — {len(df):,} products")

    def _score(self, df, skin_type, concerns, min_price, max_price, context=None):
        has_price = df['price'] > 0
        filtered = pd.concat([
            df[has_price & (df['price'] >= min_price) & (df['price'] <= max_price)],
            df[~has_price]
        ]).copy()
        if filtered.empty: return filtered

        # Layer 1: TF-IDF 35%
        user_text = skin_type + " " + " ".join(concerns)
        user_vec  = self.vectorizer.transform([user_text])
        filtered['cosine_score'] = cosine_similarity(
            user_vec, self.tfidf_matrix[filtered.index]
        ).flatten()

        # Layer 2: Concern model 40%
        model_results = filtered.apply(
            lambda row: self.concern_model.concern_score(row, concerns),
            axis=1
        )
        filtered['concern_score']   = model_results.apply(lambda x: x[0])
        filtered['_matched']        = model_results.apply(lambda x: x[1])

        # Layer 3: Skin type 10%
        filtered['skin_boost'] = filtered['skintype'].apply(
            lambda x: 0.10 if skin_type.lower() in str(x).lower() else 0
        )

        # Layer 4: Context 15%
        ctx = context or {}
        boost_map = _merge_boosts(
            AGE_BOOST.get(ctx.get('age',''), {}),
            HYDRATION_BOOST.get(ctx.get('hydration',''), {}),
            ENV_BOOST.get(ctx.get('environment',''), {}),
            EXPERIENCE_BOOST.get(ctx.get('experience',''), {}),
            ROUTINE_TIME_BOOST.get(ctx.get('routine_time',''), {}),
        )
        filtered['context_score'] = filtered.apply(
            lambda row: _context_score(row, boost_map), axis=1
        )

        filtered['final_score'] = (
            filtered['cosine_score']   * 0.35 +
            filtered['concern_score']  * 0.40 +
            filtered['skin_boost']     * 0.10 +
            filtered['context_score']  * 0.15
        ).round(4)

        return filtered

    def recommend_products(self, skin_type, concerns, min_price=0, max_price=100000,
                           top_n=5, context=None):
        if self.df is None: return []
        scored = self._score(self.df.copy(), skin_type, concerns,
                             min_price, max_price, context)
        if scored.empty: return []
        results = scored.sort_values('final_score', ascending=False).head(top_n)
        output = []
        for _, row in results.iterrows():
            p = row[RETURN_COLS].to_dict()
            p['explanation'] = _build_explanation(row, skin_type, concerns,
                                                   row.get('_matched', {}))
            output.append(p)
        return output

    def recommend_routine(self, skin_type, concerns, min_price=0, max_price=100000,
                          context=None):
        if self.df is None: return []
        scored = self._score(self.df.copy(), skin_type, concerns,
                             min_price, max_price, context)
        if scored.empty: return []
        routine = []
        for step_info in ROUTINE_STEPS:
            step_df = scored[scored['major_category'].isin(step_info['categories'])]
            if step_df.empty: continue
            best    = step_df.sort_values('final_score', ascending=False).iloc[0]
            product = best[RETURN_COLS].to_dict()
            product['step']        = step_info['step']
            product['step_label']  = step_info['label']
            product['step_icon']   = step_info['icon']
            product['explanation'] = _build_explanation(best, skin_type, concerns,
                                                         best.get('_matched', {}))
            routine.append(product)
        return routine

    def search_products(self, query):
        if self.df is None: return []
        df = self.df.copy()
        q  = query.lower().strip()
        name_match = df[
            df['name'].str.lower().str.contains(q, na=False) |
            df['brand'].str.lower().str.contains(q, na=False)
        ].copy()
        if not name_match.empty:
            return name_match[[
                'name','brand','major_category','subtype',
                'skintype','function_tags','image_url','price'
            ]].to_dict(orient='records')
        df['score'] = cosine_similarity(
            self.vectorizer.transform([q]), self.tfidf_matrix
        ).flatten()
        return df.sort_values('score', ascending=False)[[
            'name','brand','major_category','subtype',
            'skintype','function_tags','image_url','price'
        ]].to_dict(orient='records')