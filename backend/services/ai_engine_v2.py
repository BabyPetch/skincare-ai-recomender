"""
ai_engine_v2.py
===============
Skincare Recommendation Engine — Evidence-Based Scoring

SCORING FORMULA
---------------
final_score = (cosine × 0.35) + (concern × 0.40) + (skin × 0.10) + (context × 0.15)

Layer 1 — TF-IDF cosine similarity (35%)
  user_text = skin_type + concerns  →  cosine similarity กับ product combined_features

Layer 2 — Concern × Active Ingredient score (40%)  ← main driver
  concern_score = Σ [ confidence(mcat) × relative_weight(concern, mcat) × α ]
  capped at 1.0
  relative_weight อ้างอิงจาก dermatologist consensus (Delphi method):
    Alvarez GV et al. JAAD 2025;93(6):1509-1525. doi:10.1016/j.jaad.2025.04.021

Layer 3 — Skin type match (10%)
  +0.10 ถ้า user skin_type อยู่ใน product skintype field

Layer 4 — Context boost (15%)
  age / hydration / environment / experience / routine_time
  เพิ่ม weight ให้ concern ที่สอดคล้องกับ context ของ user

REFERENCES
----------
[1] Alvarez GV, Kang BY, Richmond AM, et al.
    Skincare ingredients recommended by cosmetic dermatologists: A Delphi consensus study.
    J Am Acad Dermatol. 2025;93(6):1509-1525. doi:10.1016/j.jaad.2025.04.021
    → 62 dermatologists, 43 centers, 2-round Delphi (Sep 2023–Sep 2024)
    → consensus ≥70% recommend + ≤15% discourage on 9-point Likert scale
    → 318 ingredients → 83 → 23 consensus ingredients

[2] Thiboutot D, et al. Guidelines of care for the management of acne vulgaris.
    J Am Acad Dermatol. 2024;90:1006.e1-30.
    → salicylic acid, benzoyl peroxide, retinoids Level A evidence

[3] Crous C, Pretorius J, Petzer A. Overview of popular cosmeceuticals in dermatology.
    Skin Health Dis. 2024;4(2):ski2-340. doi:10.1002/ski2.340
    → niacinamide, retinoids, vitamin C, hyaluronic acid mechanism review

[4] Boo YC. Mechanistic basis and clinical evidence for the applications of
    nicotinamide (niacinamide) to control skin aging and pigmentation.
    Antioxidants. 2021;10(8):1315. doi:10.3390/antiox10081315
"""

import json
import numpy as np
import pandas as pd
import joblib
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from database.repository import get_all_products

# ================================================================
# PATHS
# ================================================================
MODEL_DIR = Path(__file__).parent.parent / "training" / "model"

# ================================================================
# ROUTINE STEPS
# ================================================================
ROUTINE_STEPS = [
    {"step": 1, "label": "ล้างหน้า",        "icon": "🧼", "categories": ["cleanser", "cleansing"]},
    {"step": 2, "label": "โทนเนอร์",         "icon": "💦", "categories": ["toner"]},
    {"step": 3, "label": "เซรั่ม",           "icon": "✨", "categories": ["serum", "essence", "ampoule"]},
    {"step": 4, "label": "มอยส์เจอไรเซอร์", "icon": "🔒", "categories": ["moisturizer", "eye_care"]},
    {"step": 5, "label": "กันแดด",           "icon": "☀️", "categories": ["sunscreen"]},
]

RETURN_COLS = [
    "name", "brand", "major_category", "subtype",
    "skintype", "function_tags", "image_url", "price", "final_score",
]

# ================================================================
# CONCERN LABELS (UI → Thai)
# ================================================================
CONCERN_LABEL = {
    "acne_control":   "สิว",
    "brightening":    "หมองคล้ำ/ฝ้า",
    "anti_aging":     "ริ้วรอย",
    "hydrating":      "แห้งกร้าน",
    "barrier_repair": "ผิวเสีย/แพ้ง่าย",
    "calming":        "ผิวแดง/อักเสบ",
    "exfoliating":    "รูขุมขนกว้าง",
    "antioxidant":    "ริ้วรอยดำ/กระ",
}

# ================================================================
# EVIDENCE-BASED ACTIVE FEATURE WEIGHTS
#
# อ้างอิง: Alvarez GV et al. JAAD 2025 [1]
# วิธีคำนวณ: normalize consensus % ของแต่ละ ingredient-concern pair
# เช่น acne concern:
#   benzoyl peroxide 95.2%, salicylic acid 93.6% → acne weight = 1.0
#   salicylic acid 79% for oily skin → oilcontrol weight = 0.85
#   glycolic acid for acne dark spots 82% → exfoliation weight = 0.70
#   niacinamide anti-inflammatory → soothing weight = 0.50
#
# CONCERN_ACTIVE_WEIGHTS[concern][model_category] = relative_weight (0.0–1.0)
# weight สูง = dermatologist consensus สูงว่า ingredient นี้ช่วย concern นี้
# ================================================================
CONCERN_ACTIVE_WEIGHTS = {
    "acne_control": {
        # [1] benzoyl peroxide 95.2%, salicylic acid 93.6% for acne
        # [2] salicylic acid, retinoids Level A evidence for acne
        "acne":        1.00,
        "oilcontrol":  0.85,  # [1] salicylic 79% for oily skin
        "exfoliation": 0.70,  # [1] glycolic acid 82% for acne/dark spots
        "soothing":    0.50,  # [3] niacinamide anti-inflammatory
    },
    "brightening": {
        # [1] hydroquinone 98.4%, kojic 93.6%, tranexamic 87.1%, Vit C 87.1%
        "whitening":   1.00,
        "antioxidant": 0.80,  # [1] Vit C 88.7% anti-aging + brightening
        "exfoliation": 0.60,  # [1] glycolic acid 82% for dark spots
        "hydration":   0.30,  # supporting moisture for even skin tone
    },
    "anti_aging": {
        # [1] retinoids 96.8%, Vit C 88.7%, mineral sunscreen 96.8%
        # [3] retinoids gold standard for collagen stimulation
        "wrinkle":      1.00,
        "antioxidant":  0.85,  # [1] Vit C collagen synthesis 88.7%
        "hydration":    0.65,  # [1] hyaluronic acid 79%
        "barrierrepair":0.50,  # [1] ceramides 82.1%
    },
    "hydrating": {
        # [1] petrolatum 85.5%, ceramides 82.1%, hyaluronic acid 79%, urea 79%
        "hydration":    1.00,
        "barrierrepair":0.85,  # [1] ceramides lock moisture barrier
        "soothing":     0.40,  # [4] niacinamide barrier support
    },
    "barrier_repair": {
        # [1] ceramides 82.1%, [3] niacinamide barrier function
        "barrierrepair":1.00,
        "soothing":     0.80,  # [4] niacinamide reduces inflammation
        "hydration":    0.60,  # moisture retention supports barrier
    },
    "calming": {
        # [1] niacinamide for redness, mineral sunscreen 95.2% for redness
        # [3] niacinamide anti-inflammatory
        "soothing":     1.00,
        "barrierrepair":0.75,  # repair reduces sensitivity
        "hydration":    0.40,  # supporting
    },
    "exfoliating": {
        # [1] salicylic acid 93.6%, glycolic acid 82%
        # [3] AHA/BHA dissolve corneodesmosomes, reduce hyperkeratotic plugs
        "exfoliation":  1.00,
        "oilcontrol":   0.75,  # [1] salicylic 79% for oily/large pores
        "acne":         0.50,  # pore clearing → fewer acne
    },
    "antioxidant": {
        # [1] Vit C 88.7% anti-aging + 87.1% dark spots
        # [3] retinoids, niacinamide antioxidant mechanism
        "antioxidant":  1.00,
        "whitening":    0.70,  # [1] Vit C dark spots 87.1%
        "wrinkle":      0.60,  # [1] Vit C fine lines 88.7%
        "exfoliation":  0.40,  # AHA with antioxidant effect
    },
}

# concern (UI) → model output categories
CONCERN_TO_MODEL = {
    "acne_control":   ["acne", "oilcontrol", "exfoliation", "soothing"],
    "brightening":    ["whitening", "antioxidant", "exfoliation", "hydration"],
    "anti_aging":     ["wrinkle", "antioxidant", "hydration", "barrierrepair"],
    "hydrating":      ["hydration", "barrierrepair", "soothing"],
    "barrier_repair": ["barrierrepair", "soothing", "hydration"],
    "calming":        ["soothing", "barrierrepair", "hydration"],
    "exfoliating":    ["exfoliation", "oilcontrol", "acne"],
    "antioxidant":    ["antioxidant", "whitening", "wrinkle", "exfoliation"],
}

# model category → DB column
MODEL_TO_COL = {
    "acne":         "active_acne",
    "whitening":    "active_whitening",
    "wrinkle":      "active_wrinkle",
    "exfoliation":  "active_exfoliation",
    "hydration":    "active_hydration",
    "barrierrepair":"active_barrier",
    "soothing":     "active_soothing",
    "oilcontrol":   "active_oilct",
    "antioxidant":  "active_antioxidant",
}

# ================================================================
# CONTEXT BOOST RULES
# อ้างอิง: dermatology guidelines สำหรับ age-appropriate skincare
# ================================================================
CONTEXT_RULES = {
    "gender": {
    # อ้างอิง: Dao H, Kazin RA. Gender differences in skin: a review of the literature.
    # Gender Medicine. 2007;4(4):308-328. doi:10.1016/S1550-8579(07)80061-1
    "male":   {"acne_control": 0.10, "oilcontrol": 0.10, "exfoliating": 0.05},
    "female": {"hydrating": 0.10, "barrier_repair": 0.05, "brightening": 0.05},
    "other":  {},
    },
    "age": {
        "teen":   {"acne_control": 0.20, "hydrating": 0.10},
        "young":  {"brightening": 0.10,  "antioxidant": 0.10},
        "adult":  {"anti_aging": 0.15,   "brightening": 0.10},
        "mature": {"anti_aging": 0.25,   "hydrating": 0.15,  "barrier_repair": 0.10},
        "senior": {"anti_aging": 0.30,   "hydrating": 0.20,  "barrier_repair": 0.15},
    },
    "hydration": {
        "very_dry": {"hydrating": 0.25, "barrier_repair": 0.20},
        "dry":      {"hydrating": 0.15, "barrier_repair": 0.10},
        "normal":   {},
        "oily":     {"acne_control": 0.15, "exfoliating": 0.10},
    },
    "environment": {
        "hot_humid":  {"acne_control": 0.10, "exfoliating": 0.10},
        "ac_all_day": {"hydrating": 0.20,    "barrier_repair": 0.15},
        "mixed":      {"hydrating": 0.10},
        "pollution":  {"antioxidant": 0.20,  "brightening": 0.10},
        "tropical":   {"antioxidant": 0.15,  "brightening": 0.10},
    },
    "experience": {
        "beginner":     {"calming": 0.10, "hydrating": 0.10},
        "intermediate": {"brightening": 0.10},
        "advanced":     {"anti_aging": 0.15, "antioxidant": 0.15, "exfoliating": 0.10},
    },
    "routine_time": {
        "morning": {"antioxidant": 0.10},
        "evening": {"anti_aging": 0.15, "barrier_repair": 0.15, "hydrating": 0.10},
        "both":    {"hydrating": 0.05,  "barrier_repair": 0.05},
    },
}

# ================================================================
# HELPERS
# ================================================================
def _merge_boosts(context: dict) -> dict:
    merged = {}
    for key, rule_map in CONTEXT_RULES.items():
        for tag, w in rule_map.get(context.get(key, ""), {}).items():
            merged[tag] = merged.get(tag, 0) + w
    return merged


def _context_score(function_tags: str, boost_map: dict) -> float:
    if not boost_map:
        return 0.0
    tags = function_tags.lower()
    return sum(w for tag, w in boost_map.items() if tag.lower() in tags)


def _top_ingredients(row: pd.Series, model_cats: list, n: int = 3) -> list:
    """ดึง active ingredients จาก columns ที่ match model_cats เรียงตาม weight สูงสุด"""
    seen, result = set(), []
    for mcat in model_cats:
        col = MODEL_TO_COL.get(mcat, "")
        for ing in str(row.get(col, "") or "").split(","):
            ing = ing.strip()
            if ing and ing not in seen:
                seen.add(ing)
                result.append(ing)
                if len(result) >= n:
                    return result
    return result


# ================================================================
# CONCERN MODEL
# ================================================================
class ConcernModel:
    """
    Multi-label classifier: ingredients → { category: confidence }
    trained บน 5090 products × 210 active ingredients จาก Active_group.csv
    """

    def __init__(self):
        self.model       = None
        self.categories  = []
        self._ingr_index = {}
        self._n_features = 0
        self._load()

    def _load(self):
        model_path = MODEL_DIR / "concern_classifier.pkl"
        meta_path  = MODEL_DIR / "concern_meta.json"
        if not model_path.exists():
            print("⚠️  concern_classifier.pkl ไม่พบ — concern_score = 0")
            return
        self.model = joblib.load(model_path)
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        self.categories  = meta["categories"]
        self._ingr_index = {ing: i for i, ing in enumerate(meta["ingredients"])}
        self._n_features = len(meta["ingredients"])
        print(f"✅ Concern model loaded — {self._n_features} ingredients, {len(self.categories)} categories")

    def _vectorize(self, ingredients_list_str: str) -> np.ndarray:
        x = np.zeros(self._n_features, dtype=np.float32)
        for ing in str(ingredients_list_str).split(","):
            idx = self._ingr_index.get(ing.strip().lower())
            if idx is not None:
                x[idx] = 1.0
        return x

    def predict_proba(self, ingredients_list_str: str, threshold: float = 0.30) -> dict:
        """returns { category: confidence } for categories above threshold"""
        if self.model is None:
            return {}
        x = self._vectorize(ingredients_list_str)
        if x.sum() == 0:
            return {}
        proba = self.model.predict_proba(x.reshape(1, -1))[0]
        return {
            cat: round(float(p), 3)
            for cat, p in zip(self.categories, proba)
            if p >= threshold
        }

    def score_and_match(self, row: pd.Series, concerns: list) -> tuple:
        """
        concern_score = Σ [ confidence(mcat) × relative_weight(concern, mcat) × 0.15 ]
        capped at 1.0

        อ้างอิง weight จาก CONCERN_ACTIVE_WEIGHTS ซึ่งอิงจาก Alvarez GV et al. JAAD 2025
        """
        pred = self.predict_proba(row.get("ingredients_list", ""))
        if not pred:
            return 0.0, {}

        total, matched = 0.0, {}
        for concern in concerns:
            weights = CONCERN_ACTIVE_WEIGHTS.get(concern, {})
            for mcat in CONCERN_TO_MODEL.get(concern, []):
                conf        = pred.get(mcat, 0.0)
                rel_weight  = weights.get(mcat, 0.3)  # default 0.3 ถ้าไม่มีใน table
                if conf > 0:
                    total += conf * rel_weight * 0.15
                    matched.setdefault(concern, []).append((mcat, conf, rel_weight))

        return min(total, 1.0), matched


# ================================================================
# EXPLANATION BUILDER
# ================================================================
def build_explanation(row: pd.Series, skin_type: str, concerns: list,
                      matched: dict, scores: dict) -> dict:
    """
    คืน explanation dict ที่มีทั้ง:
    1. score_breakdown — แต่ละ layer contribute เท่าไหร่
    2. concern_reasons — ingredient ไหนทำให้ได้ concern นั้น + confidence
    3. other_reasons — skin type, key ingredients, free-from
    """
    # score breakdown
    breakdown = {
        "final":   round(scores.get("final", 0), 4),
        "concern": {"score": round(scores.get("concern", 0), 4), "weight": "40%"},
        "tfidf":   {"score": round(scores.get("cosine", 0), 4),  "weight": "35%"},
        "skin":    {"score": round(scores.get("skin", 0), 4),    "weight": "10%"},
        "context": {"score": round(scores.get("context", 0), 4), "weight": "15%"},
    }

    # concern reasons พร้อม ingredients + confidence
    concern_reasons = []
    for concern, cat_confs in matched.items():
        label = CONCERN_LABEL.get(concern, concern)
        # เรียงตาม rel_weight × confidence สูงสุด
        sorted_cats = sorted(cat_confs, key=lambda x: -(x[1] * x[2]))
        top_cats    = [mc for mc, _, _ in sorted_cats]
        ingrs       = _top_ingredients(row, top_cats, n=3)

        concern_reasons.append({
            "concern":     concern,
            "label":       label,
            "ingredients": ingrs,
            "top_conf":    round(sorted_cats[0][1], 2) if sorted_cats else 0,
            "text":        f"ช่วย{label}: {', '.join(ingrs)}" if ingrs else f"ช่วย{label}",
        })

    # other reasons
    other = []
    if skin_type and skin_type.lower() in str(row.get("skintype", "")).lower():
        other.append(f"เหมาะกับผิว {skin_type}")

    key = str(row.get("key_ingredients", "") or "").strip()
    if key:
        top = [v.strip() for v in key.split(",") if v.strip()][:3]
        if top:
            other.append(f"Key ingredients: {', '.join(top)}")

    free = str(row.get("free_from", "") or "").strip()
    if free and free.upper() != "NA":
        other.append(f"ปลอดภัย: {free}")

    return {
        "score_breakdown":  breakdown,
        "concern_reasons":  concern_reasons,
        "other_reasons":    other,
        # summary text สำหรับ display
        "summary": [r["text"] for r in concern_reasons] + other,
    }


# ================================================================
# DATA LOADER
# ================================================================
class DataLoader:
    """
    โหลด products จาก DB → build TF-IDF → score → recommend

    Scoring formula (อ้างอิง doc string ด้านบน):
    final_score = cosine×0.35 + concern×0.40 + skin×0.10 + context×0.15
    """

    ACTIVE_COLS = [
        "active_acne", "active_whitening", "active_wrinkle", "active_exfoliation",
        "active_hydration", "active_barrier", "active_soothing",
        "active_oilct", "active_antioxidant",
    ]
    TEXT_COLS = [
        "skintype", "function_tags", "major_category", "brand",
        "ingredients_list", "subtype", "key_ingredients", "free_from",
    ]
    TFIDF_COLS = [
        "skintype", "function_tags", "major_category", "brand", "ingredients_list",
        "active_acne", "active_whitening", "active_wrinkle",
        "active_hydration", "active_barrier", "active_soothing",
    ]

    def __init__(self):
        self.df            = None
        self.vectorizer    = None
        self.tfidf_matrix  = None
        self.concern_model = ConcernModel()
        self._build()

    def _build(self):
        rows = get_all_products()
        if not rows:
            print("⚠️  No products in DB"); return

        df = pd.DataFrame(rows)
        df["price"] = pd.to_numeric(df["price"], errors="coerce").fillna(0)

        for col in self.TEXT_COLS + self.ACTIVE_COLS:
            df[col] = df[col].fillna("") if col in df.columns else ""

        df["combined_features"] = df[self.TFIDF_COLS].apply(
            lambda r: " ".join(r.values.astype(str)), axis=1
        )

        self.df           = df
        self.vectorizer   = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5))
        self.tfidf_matrix = self.vectorizer.fit_transform(df["combined_features"])
        print(f"✅ AI Engine v2 ready — {len(df):,} products loaded")

    def _score(self, df: pd.DataFrame, skin_type: str, concerns: list,
               min_price: float, max_price: float, context: dict) -> pd.DataFrame:

        has_price = df["price"] > 0
        filtered = pd.concat([
            df[has_price & (df["price"] >= min_price) & (df["price"] <= max_price)],
            df[~has_price],
        ]).copy()
        if filtered.empty:
            return filtered

        # Layer 1: TF-IDF cosine (35%)
        user_vec = self.vectorizer.transform([skin_type + " " + " ".join(concerns)])
        filtered["cosine_score"] = cosine_similarity(
            user_vec, self.tfidf_matrix[filtered.index]
        ).flatten()

        # Layer 2: ML concern model with evidence-based weights (40%)
        results = filtered.apply(
            lambda row: self.concern_model.score_and_match(row, concerns), axis=1
        )
        filtered["concern_score"] = results.apply(lambda x: x[0])
        filtered["_matched"]      = results.apply(lambda x: x[1])

        # Layer 3: Skin type match (10%)
        filtered["skin_boost"] = filtered["skintype"].apply(
            lambda x: 0.10 if skin_type.lower() in str(x).lower() else 0.0
        )

        # Layer 4: Context boost (15%)
        boost_map = _merge_boosts(context)
        filtered["context_score"] = filtered["function_tags"].apply(
            lambda tags: _context_score(tags, boost_map)
        )

        # Final weighted score
        filtered["final_score"] = (
            filtered["cosine_score"]  * 0.35 +
            filtered["concern_score"] * 0.40 +
            filtered["skin_boost"]    * 0.10 +
            filtered["context_score"] * 0.15
        ).round(4)

        return filtered

    def recommend_products(self, skin_type: str, concerns: list,
                           min_price: float = 0, max_price: float = 100000,
                           top_n: int = 5, context: dict = None) -> list:
        if self.df is None:
            return []
        scored = self._score(self.df.copy(), skin_type, concerns,
                             min_price, max_price, context or {})
        if scored.empty:
            return []

        output = []
        for _, row in scored.sort_values("final_score", ascending=False).head(top_n).iterrows():
            p = row[RETURN_COLS].to_dict()
            p["explanation"] = build_explanation(
                row, skin_type, concerns, row["_matched"],
                {
                    "final":   row["final_score"],
                    "cosine":  row["cosine_score"],
                    "concern": row["concern_score"],
                    "skin":    row["skin_boost"],
                    "context": row["context_score"],
                }
            )
            output.append(p)
        return output

    def recommend_routine(self, skin_type: str, concerns: list,
                          min_price: float = 0, max_price: float = 100000,
                          context: dict = None) -> list:
        if self.df is None:
            return []
        scored = self._score(self.df.copy(), skin_type, concerns,
                             min_price, max_price, context or {})
        if scored.empty:
            return []

        routine = []
        for step in ROUTINE_STEPS:
            step_df = scored[scored["major_category"].isin(step["categories"])]
            if step_df.empty:
                continue
            best = step_df.sort_values("final_score", ascending=False).iloc[0]
            product = best[RETURN_COLS].to_dict()
            product.update({
                "step":       step["step"],
                "step_label": step["label"],
                "step_icon":  step["icon"],
                "explanation": build_explanation(
                    best, skin_type, concerns, best["_matched"],
                    {
                        "final":   best["final_score"],
                        "cosine":  best["cosine_score"],
                        "concern": best["concern_score"],
                        "skin":    best["skin_boost"],
                        "context": best["context_score"],
                    }
                ),
            })
            routine.append(product)
        return routine

    def search_products(self, query: str) -> list:
        if self.df is None:
            return []
        q  = query.lower().strip()
        df = self.df

        name_match = df[
            df["name"].str.lower().str.contains(q, na=False) |
            df["brand"].str.lower().str.contains(q, na=False)
        ]
        if not name_match.empty:
            return name_match[
                ["name", "brand", "major_category", "subtype",
                 "skintype", "function_tags", "image_url", "price"]
            ].to_dict(orient="records")

        scores = cosine_similarity(
            self.vectorizer.transform([q]), self.tfidf_matrix
        ).flatten()
        return df.assign(score=scores).sort_values("score", ascending=False)[
            ["name", "brand", "major_category", "subtype",
             "skintype", "function_tags", "image_url", "price"]
        ].to_dict(orient="records")