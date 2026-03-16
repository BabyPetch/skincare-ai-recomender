"""
train_concern_model.py
======================
Train multi-label classifier: ingredients -> concerns
ใช้ Active_group.csv เป็น ground truth

pip install scikit-learn pandas numpy joblib

python train_concern_model.py
  → saves model/concern_classifier.pkl
  → saves model/mlb_ingredients.pkl
  → prints evaluation report
"""

import os, json
import numpy as np
import pandas as pd
from pathlib import Path
from collections import defaultdict

from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.multiclass import OneVsRestClassifier
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, hamming_loss
import joblib

# ================================================================
# PATHS
# ================================================================
BASE     = Path(__file__).parent          # backend/training/
PROJECT  = BASE.parent                    # backend/
DATA_DIR = PROJECT / "scraper" / "data_products"
MODEL_DIR = BASE / "model"

ACTIVE_CSV  = DATA_DIR / "incidecoder_20260314_130516 - Active_group.csv"
PRODUCT_CSV = DATA_DIR / "incidecoder_20260314_130516 - Data.csv"

CATEGORIES = [
    'acne', 'whitening', 'wrinkle', 'exfoliation',
    'hydration', 'barrierrepair', 'soothing', 'oilcontrol', 'antioxidant'
]

COL_MAP = {
    'acne':         'active_acne',
    'whitening':    'active_whitening',
    'wrinkle':      'active_wrinkle',
    'exfoliation':  'active_exfoliation',
    'hydration':    'active_hydration',
    'barrierrepair':'active_barrier',
    'soothing':     'active_soothing',
    'oilcontrol':   'active_oilct',
    'antioxidant':  'active_antioxidant',
}

# ================================================================
# STEP 1: Build ingredient → categories lookup
# ================================================================
def build_lookup(active_csv):
    df = pd.read_csv(active_csv)
    df['ingredient'] = df['ingredient'].str.strip().str.lower()
    lookup = {}
    for _, row in df.iterrows():
        cats = [c.strip() for c in str(row['category']).split(',') if c.strip() in CATEGORIES]
        if cats:
            lookup[row['ingredient']] = cats
    print(f"✅ Lookup: {len(lookup)} active ingredients")
    return lookup

# ================================================================
# STEP 2: Build training dataset
#   X = multi-hot vector of ingredients per product
#   y = multi-hot vector of categories
# ================================================================
def build_dataset(product_csv, lookup):
    df = pd.read_csv(product_csv)
    print(f"📋 Products loaded: {len(df)}")

    # collect all known ingredients
    all_ingredients = sorted(lookup.keys())
    ingr_index = {ing: i for i, ing in enumerate(all_ingredients)}
    n_ingr = len(all_ingredients)
    n_cats = len(CATEGORIES)
    cat_index = {c: i for i, c in enumerate(CATEGORIES)}

    X_rows = []
    y_rows = []
    urls   = []

    for _, row in df.iterrows():
        ingr_str = str(row.get('ingredients_list', '') or '')
        ingrs = [i.strip().lower() for i in ingr_str.split(',') if i.strip()]

        # X: multi-hot over known active ingredients
        x = np.zeros(n_ingr, dtype=np.float32)
        for ing in ingrs:
            if ing in ingr_index:
                x[ingr_index[ing]] = 1.0

        # y: union of categories from all matched ingredients
        y_set = set()
        for ing in ingrs:
            if ing in lookup:
                y_set.update(lookup[ing])

        y = np.zeros(n_cats, dtype=np.float32)
        for cat in y_set:
            if cat in cat_index:
                y[cat_index[cat]] = 1.0

        # skip products with no active ingredients at all
        if x.sum() == 0:
            continue

        X_rows.append(x)
        y_rows.append(y)
        urls.append(row.get('product_url', ''))

    X = np.array(X_rows)
    y = np.array(y_rows)
    print(f"✅ Dataset: {X.shape[0]} products × {X.shape[1]} ingredient features → {y.shape[1]} labels")
    print(f"   Label distribution:")
    for i, cat in enumerate(CATEGORIES):
        pos = int(y[:, i].sum())
        print(f"     {cat:15s}: {pos:4d} / {len(y)} ({pos/len(y)*100:.1f}%)")

    return X, y, all_ingredients, urls

# ================================================================
# STEP 3: Train
# ================================================================
def train(X, y):
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.15, random_state=42
    )
    print(f"\n🔧 Training on {len(X_train)} samples, testing on {len(X_test)}")

    # Multi-label: train one classifier per label (OneVsRest)
    # LogisticRegression is fast and works well for this type
    model = OneVsRestClassifier(
        LogisticRegression(
            C=1.0,
            max_iter=500,
            solver='lbfgs',
            random_state=42,
            n_jobs=-1,
        ),
        n_jobs=-1,
    )

    model.fit(X_train, y_train)

    # Evaluate
    y_pred = model.predict(X_test)
    y_pred_proba = model.predict_proba(X_test)

    print(f"\n📊 Evaluation:")
    print(f"   Hamming loss: {hamming_loss(y_test, y_pred):.4f}  (lower is better)")
    print()
    print(classification_report(
        y_test, y_pred,
        target_names=CATEGORIES,
        zero_division=0
    ))

    return model

# ================================================================
# STEP 4: Save model + metadata
# ================================================================
def save(model, all_ingredients):
    model_path = MODEL_DIR / "concern_classifier.pkl"
    meta_path  = MODEL_DIR / "concern_meta.json"

    joblib.dump(model, model_path)

    meta = {
        "ingredients": all_ingredients,
        "categories":  CATEGORIES,
        "col_map":     COL_MAP,
        "version":     "1.0",
    }
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    print(f"\n💾 Model saved → {model_path}")
    print(f"   Meta  saved → {meta_path}")

# ================================================================
# INFERENCE HELPER (ใช้ใน ai_engine.py)
# ================================================================
def predict_concerns(ingredients_list_str, model, meta, threshold=0.35):
    """
    ingredients_list_str: comma-separated string จาก DB
    returns: dict { category: confidence_score }
    """
    ingr_index = {ing: i for i, ing in enumerate(meta['ingredients'])}
    ingrs = [i.strip().lower() for i in str(ingredients_list_str).split(',') if i.strip()]

    x = np.zeros(len(meta['ingredients']), dtype=np.float32)
    for ing in ingrs:
        if ing in ingr_index:
            x[ingr_index[ing]] = 1.0

    proba = model.predict_proba(x.reshape(1, -1))[0]

    result = {}
    for i, cat in enumerate(meta['categories']):
        if proba[i] >= threshold:
            result[cat] = round(float(proba[i]), 3)
    return result

# ================================================================
# MAIN
# ================================================================
if __name__ == "__main__":
    print("="*55)
    print("  Concern Classifier Training")
    print("="*55)

    if not ACTIVE_CSV.exists():
        print(f"❌ ไม่พบ: {ACTIVE_CSV}"); exit(1)
    if not PRODUCT_CSV.exists():
        print(f"❌ ไม่พบ: {PRODUCT_CSV}"); exit(1)

    lookup              = build_lookup(ACTIVE_CSV)
    X, y, ingredients, urls = build_dataset(PRODUCT_CSV, lookup)
    model               = train(X, y)
    save(model, ingredients)

    print("\n✅ Done — ทดสอบ inference:")
    import json
    meta = json.load(open(MODEL_DIR / "concern_meta.json", encoding="utf-8"))
    test_ingr = "Water, Niacinamide, Salicylic Acid, Glycerin, Zinc PCA, Centella Asiatica Extract"
    result = predict_concerns(test_ingr, model, meta)
    print(f"   Input: {test_ingr}")
    print(f"   Predicted concerns: {result}")