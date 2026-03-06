import argparse
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    from thai_mapping import parse_thai_input
    THAI_ENABLED = True
except ImportError:
    THAI_ENABLED = False

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class Recommender:

    def __init__(self, df):
        self.df = df.copy()

        self.df['combined_features'] = (
            self.df['skintype'].fillna('') + " " +
            self.df['function_tags'].fillna('') + " " +
            self.df['major_category'].fillna('') + " " +
            self.df['brand'].fillna('') + " " +
            self.df['ingredients_list'].fillna('')
        )

        self.vectorizer = TfidfVectorizer(analyzer='char_wb', ngram_range=(3, 5))
        self.tfidf_matrix = self.vectorizer.fit_transform(self.df['combined_features'])

    def recommend(self, skin_type, concerns, top_n=5):
        df = self.df.copy()

        user_text = skin_type + " " + " ".join(concerns)
        user_vec = self.vectorizer.transform([user_text])

        scores = cosine_similarity(user_vec, self.tfidf_matrix).flatten()
        df['cosine_score'] = scores

        df['skin_boost'] = df['skintype'].apply(
            lambda x: 0.2 if skin_type.lower() in str(x).lower() else 0
        )

        df['final_score'] = df['cosine_score'] * 0.7 + df['skin_boost']

        results = df.sort_values('final_score', ascending=False).head(top_n)

        return results[['name', 'brand', 'major_category', 'subtype',
                         'skintype', 'function_tags', 'final_score']].to_dict(orient='records')


def show_results(results, skin_type, concerns):
    print(f"\n{'='*60}")
    print(f"  skin_type : {skin_type}")
    print(f"  concerns  : {', '.join(concerns)}")
    print(f"{'='*60}")
    if not results:
        print("  ไม่พบสินค้าที่ตรงกัน")
        return
    for i, r in enumerate(results, 1):
        print(f"\n  [{i}] {r['brand']} — {r['name']}")
        print(f"       category : {r['major_category']} / {r['subtype']}")
        print(f"       skintype : {r['skintype']}")
        print(f"       functions: {r['function_tags']}")
        print(f"       score    : {r['final_score']:.4f}")
    print()


TEST_CASES = [
    {"skin_type": "dry",         "concerns": ["hydrating", "barrier_repair"]},
    {"skin_type": "oily",        "concerns": ["acne_control", "brightening"]},
    {"skin_type": "sensitive",   "concerns": ["calming", "barrier_repair"]},
    {"skin_type": "combination", "concerns": ["brightening", "anti_aging"]},
]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", default="data_products/incidecoder_20260225_143616_patched.csv")
    parser.add_argument("--top_n", type=int, default=5)
    args = parser.parse_args()

    print(f"\nLoading {args.csv} ...")
    df = pd.read_csv(args.csv)
    print(f"  {len(df):,} products loaded")

    for col in ['skintype', 'function_tags', 'major_category', 'brand', 'ingredients_list', 'subtype']:
        if col not in df.columns:
            df[col] = ""

    print("\nBuilding TF-IDF matrix ...")
    rec = Recommender(df)
    print("  Ready!\n")

    for tc in TEST_CASES:
        results = rec.recommend(tc["skin_type"], tc["concerns"], top_n=args.top_n)
        show_results(results, tc["skin_type"], tc["concerns"])

    print("=" * 60)
    if THAI_ENABLED:
        print("  Interactive Mode  — รับภาษาไทยได้  (พิมพ์ q เพื่อออก)")
        print("  เช่น: หน้ามัน สิว เซรั่ม")
        print("        ผิวแห้ง ขาดความชุ่มชื้น ครีม")
    else:
        print("  Interactive Mode  (พิมพ์ q เพื่อออก)")
    print("=" * 60)

    while True:
        user_input = input("\n  พิมพ์ได้เลย (ไทย/อังกฤษ): ").strip()
        if user_input.lower() == "q":
            break

        if THAI_ENABLED:
            st, concerns, category = parse_thai_input(user_input)
            if not st:
                st = "all"
            if not concerns:
                concerns = []
            print(f"  → skintype: {st}  |  concerns: {concerns}  |  category: {category or 'any'}")
        else:
            st = user_input
            concerns = []

        results = rec.recommend(st, concerns, top_n=args.top_n)
        show_results(results, st, concerns)


if __name__ == "__main__":
    main()