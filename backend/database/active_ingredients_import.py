"""
Import active_ingredients จาก CSV เข้า DB
วางไว้ใน backend/database/ แล้วรัน:
    python active_ingredients_import.py
"""
import os, sys
import pandas as pd
import psycopg2

DB_CONFIG = {
    "dbname": "skincareCollectionDB",
    "user": "postgres",
    "password": "1234",
    "host": "127.0.0.1",
    "port": "5432"
}

CSV_PATH = os.path.join(
    os.path.dirname(__file__), "..",
    "scraper", "data_products",
    "incidecoder_20260314_130516_-_Active_group.csv"
)

CATS = ['acne','whitening','wrinkle','exfoliation',
        'hydration','barrierrepair','soothing','oilcontrol','antioxidant']

def run():
    csv_path = os.path.normpath(CSV_PATH)
    if not os.path.exists(csv_path):
        print(f"❌ ไม่พบ: {csv_path}"); sys.exit(1)

    df = pd.read_csv(csv_path)
    df['ingredient'] = df['ingredient'].str.strip()
    print(f"📋 {len(df)} ingredients to import")

    conn = psycopg2.connect(**DB_CONFIG)
    cur  = conn.cursor()

    # สร้าง table ถ้ายังไม่มี
    cur.execute(f"""
        CREATE TABLE IF NOT EXISTS active_ingredients (
            id          SERIAL PRIMARY KEY,
            ingredient  TEXT NOT NULL UNIQUE,
            acne        BOOLEAN DEFAULT FALSE,
            whitening   BOOLEAN DEFAULT FALSE,
            wrinkle     BOOLEAN DEFAULT FALSE,
            exfoliation BOOLEAN DEFAULT FALSE,
            hydration   BOOLEAN DEFAULT FALSE,
            barrierrepair BOOLEAN DEFAULT FALSE,
            soothing    BOOLEAN DEFAULT FALSE,
            oilcontrol  BOOLEAN DEFAULT FALSE,
            antioxidant BOOLEAN DEFAULT FALSE
        );
    """)
    conn.commit()

    inserted = updated = 0
    for _, row in df.iterrows():
        cats_in = [c.strip() for c in str(row['category']).split(',')]
        vals    = {c: (c in cats_in) for c in CATS}

        cur.execute(f"""
            INSERT INTO active_ingredients
                (ingredient, acne, whitening, wrinkle, exfoliation,
                 hydration, barrierrepair, soothing, oilcontrol, antioxidant)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (ingredient) DO UPDATE SET
                acne          = EXCLUDED.acne,
                whitening     = EXCLUDED.whitening,
                wrinkle       = EXCLUDED.wrinkle,
                exfoliation   = EXCLUDED.exfoliation,
                hydration     = EXCLUDED.hydration,
                barrierrepair = EXCLUDED.barrierrepair,
                soothing      = EXCLUDED.soothing,
                oilcontrol    = EXCLUDED.oilcontrol,
                antioxidant   = EXCLUDED.antioxidant
        """, (
            row['ingredient'],
            vals['acne'], vals['whitening'], vals['wrinkle'],
            vals['exfoliation'], vals['hydration'], vals['barrierrepair'],
            vals['soothing'], vals['oilcontrol'], vals['antioxidant']
        ))

        if cur.statusmessage == "INSERT 0 1":
            inserted += 1
        else:
            updated += 1

    conn.commit()
    conn.close()
    print(f"✅ Done — inserted: {inserted}, updated: {updated}")

    # verify
    conn2 = psycopg2.connect(**DB_CONFIG)
    cur2  = conn2.cursor()
    cur2.execute("SELECT COUNT(*) FROM active_ingredients")
    print(f"   Total in DB: {cur2.fetchone()[0]}")
    conn2.close()

if __name__ == "__main__":
    run()