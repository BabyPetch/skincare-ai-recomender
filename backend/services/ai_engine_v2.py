"""
ai_engine_v2.py
===============
SCORING FORMULA
---------------
final_score = (cosine × 0.35) + (concern × 0.45) + (skin × 0.05) + (context × 0.15)

skin_type เป็น Hard Filter ก่อน scoring — ผลิตภัณฑ์ต้องตรง skin type ก่อนเสมอ

Layer 1 — TF-IDF cosine similarity (35%)
Layer 2 — Concern ML score normalized (45%)
Layer 3 — Skin type bonus (5%)
Layer 4 — Context boost normalized (15%)

อ้างอิง: Alvarez GV et al. JAAD 2025;93(6):1509-1525.
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
# CONCERN WEIGHTS  (อ้างอิง Alvarez GV et al. JAAD 2025)
# ================================================================
CONCERN_ACTIVE_WEIGHTS = {
    "acne_control": {
        "acne":        1.00,
        "oilcontrol":  0.85,
        "exfoliation": 0.70,
        "soothing":    0.50,
    },
    "brightening": {
        "whitening":   1.00,
        "antioxidant": 0.80,
        "exfoliation": 0.60,
        "hydration":   0.30,
    },
    "anti_aging": {
        "wrinkle":       1.00,
        "antioxidant":   0.85,
        "hydration":     0.65,
        "barrierrepair": 0.50,
    },
    "hydrating": {
        "hydration":     1.00,
        "barrierrepair": 0.85,
        "soothing":      0.40,
    },
    "barrier_repair": {
        "barrierrepair": 1.00,
        "soothing":      0.80,
        "hydration":     0.60,
    },
    "calming": {
        "soothing":      1.00,
        "barrierrepair": 0.75,
        "hydration":     0.40,
    },
    "exfoliating": {
        "exfoliation":  1.00,
        "oilcontrol":   0.75,
        "acne":         0.50,
    },
    "antioxidant": {
        "antioxidant":  1.00,
        "whitening":    0.70,
        "wrinkle":      0.60,
        "exfoliation":  0.40,
    },
}

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

MODEL_TO_COL = {
    "acne":          "active_acne",
    "whitening":     "active_whitening",
    "wrinkle":       "active_wrinkle",
    "exfoliation":   "active_exfoliation",
    "hydration":     "active_hydration",
    "barrierrepair": "active_barrier",
    "soothing":      "active_soothing",
    "oilcontrol":    "active_oilct",
    "antioxidant":   "active_antioxidant",
}

# ================================================================
# CONTEXT RULES
# ================================================================
CONTEXT_RULES = {
    "gender": {
        "male":   {"acne_control": 0.10, "oilcontrol": 0.10, "exfoliating": 0.05},
        "female": {"hydrating": 0.10, "barrier_repair": 0.05, "brightening": 0.05},
        "other":  {},
    },
    "age": {
        "teen":   {"acne_control": 0.20, "hydrating": 0.10},
        "young":  {"brightening": 0.10, "antioxidant": 0.10},
        "adult":  {"anti_aging": 0.15, "brightening": 0.10},
        "mature": {"anti_aging": 0.25, "hydrating": 0.15, "barrier_repair": 0.10},
        "senior": {"anti_aging": 0.30, "hydrating": 0.20, "barrier_repair": 0.15},
    },
    "hydration": {
        "very_dry": {"hydrating": 0.25, "barrier_repair": 0.20},
        "dry":      {"hydrating": 0.15, "barrier_repair": 0.10},
        "normal":   {},
        "oily":     {"acne_control": 0.15, "exfoliating": 0.10},
    },
    "environment": {
        "hot_humid":  {"acne_control": 0.10, "exfoliating": 0.10},
        "ac_all_day": {"hydrating": 0.20, "barrier_repair": 0.15},
        "mixed":      {"hydrating": 0.10},
        "pollution":  {"antioxidant": 0.20, "brightening": 0.10},
        "tropical":   {"antioxidant": 0.15, "brightening": 0.10},
    },
    "experience": {
        "beginner":     {"calming": 0.10, "hydrating": 0.10},
        "intermediate": {"brightening": 0.10},
        "advanced":     {"anti_aging": 0.15, "antioxidant": 0.15, "exfoliating": 0.10},
    },
    "routine_time": {
        "morning": {"antioxidant": 0.10},
        "evening": {"anti_aging": 0.15, "barrier_repair": 0.15, "hydrating": 0.10},
        "both":    {"hydrating": 0.05, "barrier_repair": 0.05},
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


def _context_score_normalized(function_tags: str, boost_map: dict) -> float:
    """
    Normalize context score → [0, 1]
    raw     = Σ boost_w ของ tag ที่ match ใน function_tags
    max_pos = Σ boost_w ทั้งหมดใน boost_map
    return  = raw / max_pos
    """
    if not boost_map:
        return 0.0
    tags = function_tags.lower()
    raw = sum(w for tag, w in boost_map.items() if tag.lower() in tags)
    max_possible = sum(boost_map.values())
    if max_possible == 0:
        return 0.0
    return min(raw / max_possible, 1.0)


def _concern_score_normalized(pred: dict, concerns: list) -> tuple:
    """
    Normalize concern score → [0, 1]
    concern_score_i = Σ(conf × rel_w) / Σ(rel_w)  ต่อ concern หนึ่งตัว
    final           = mean ของทุก concern ที่เลือก
    """
    if not pred or not concerns:
        return 0.0, {}

    scores_per_concern = []
    matched = {}

    for concern in concerns:
        weights = CONCERN_ACTIVE_WEIGHTS.get(concern, {})
        mcats   = CONCERN_TO_MODEL.get(concern, [])

        numerator   = 0.0
        denominator = 0.0
        cat_confs   = []

        for mcat in mcats:
            conf  = pred.get(mcat, 0.0)
            rel_w = weights.get(mcat, 0.3)
            numerator   += conf * rel_w
            denominator += rel_w
            if conf > 0:
                cat_confs.append((mcat, conf, rel_w))

        concern_score = (numerator / denominator) if denominator > 0 else 0.0
        scores_per_concern.append(concern_score)
        if cat_confs:
            matched[concern] = cat_confs

    final = float(np.mean(scores_per_concern)) if scores_per_concern else 0.0
    return min(final, 1.0), matched


def _top_ingredients(row: pd.Series, model_cats: list, n: int = 3) -> list:
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
# CONCERN MODEL (ML)
# ================================================================
class ConcernModel:
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

    def predict_proba(self, ingredients_list_str: str, threshold: float = 0.25) -> dict:
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
        pred = self.predict_proba(row.get("ingredients_list", ""))
        if not pred:
            return 0.0, {}
        return _concern_score_normalized(pred, concerns)


# ================================================================
# EXPLANATION BUILDER
# ================================================================
def build_explanation(row: pd.Series, skin_type: str, concerns: list,
                        matched: dict, scores: dict) -> dict:
    breakdown = {
        "final":   round(scores.get("final", 0), 4),
        "concern": {"score": round(scores.get("concern", 0), 4), "weight": "45%"},
        "tfidf":   {"score": round(scores.get("cosine", 0), 4),  "weight": "35%"},
        "skin":    {"score": round(scores.get("skin", 0), 4),    "weight": "5%"},
        "context": {"score": round(scores.get("context", 0), 4), "weight": "15%"},
    }

    concern_reasons = []
    for concern, cat_confs in matched.items():
        label       = CONCERN_LABEL.get(concern, concern)
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
        "summary": [r["text"] for r in concern_reasons] + other,
    }


# ================================================================
# DATA LOADER
# ================================================================
class DataLoader:
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

        # ── กรองราคาก่อน ─────────────────────────────────────────────────────
        has_price = df["price"] > 0
        filtered = pd.concat([
            df[has_price & (df["price"] >= min_price) & (df["price"] <= max_price)],
            df[~has_price],
        ]).drop_duplicates().copy()

        if filtered.empty:
            return filtered

        # ── STEP 1: Hard Filter Skin Type (ปัจจัยหลัก — ทำก่อน scoring) ──────
        # กรองเฉพาะสินค้าที่ตรง skin type ออกมาก่อน
        # สินค้า "all" / "ทุกสภาพผิว" ผ่านได้เสมอ
        # ถ้าไม่เจอเลย → fallback ใช้ทั้งหมด (ป้องกัน empty result)
        if skin_type and skin_type.lower() != "all":
            skin_match = filtered[
                filtered["skintype"].str.lower().str.contains(skin_type.lower(), na=False) |
                filtered["skintype"].str.lower().str.contains("all", na=False) |
                filtered["skintype"].str.lower().str.contains("ทุกสภาพผิว", na=False)
            ]
            if not skin_match.empty:
                filtered = skin_match

        if filtered.empty:
            return filtered

        # ── STEP 2: Layer 1 — Concern × Active Ingredient (55%) ─────────────
        # หลังกรอง skin แล้ว concern เป็นตัวจัดอันดับหลักใน pool
        results = filtered.apply(
            lambda row: self.concern_model.score_and_match(row, concerns), axis=1
        )
        filtered["concern_score"] = results.apply(lambda x: x[0])
        filtered["_matched"]      = results.apply(lambda x: x[1])

        # ── STEP 3: Layer 2 — TF-IDF Cosine (25%) ────────────────────────────
        # ลดลงจาก 35% เพราะ text similarity มักต่ำโดยไม่จำเป็น
        # (ปัญหา char ngram กับ mixed Thai-English)
        user_vec = self.vectorizer.transform([skin_type + " " + " ".join(concerns)])
        filtered["cosine_score"] = cosine_similarity(
            user_vec, self.tfidf_matrix[filtered.index]
        ).flatten()

        # ── STEP 4: Layer 3 — Context normalized (20%) ───────────────────────
        boost_map = _merge_boosts(context)
        filtered["context_score"] = filtered["function_tags"].apply(
            lambda tags: _context_score_normalized(tags, boost_map)
        )

        # ── STEP 5: Skin Bonus (bonus เล็กน้อยสำหรับสินค้าที่ระบุ skin ตรงๆ)
        # สินค้าที่ระบุ skin type ชัดเจน (ไม่ใช่ "all") ได้ bonus เพิ่ม
        filtered["skin_boost"] = filtered["skintype"].apply(
            lambda x: 1.0 if skin_type and skin_type.lower() in str(x).lower() else 0.0
        )

        # ── Final Score ───────────────────────────────────────────────────────
        # Concern  : 55% — active ingredients เป็นตัวจัดอันดับหลักใน pool
        # Cosine   : 25% — feature similarity
        # Context  : 20% — บริบทผู้ใช้
        # skin_boost ไม่มี weight แยก เพราะ hard filter ทำหน้าที่ไปแล้ว
        filtered["final_score"] = (
            filtered["concern_score"] * 0.55 +
            filtered["cosine_score"]  * 0.25 +
            filtered["context_score"] * 0.20
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