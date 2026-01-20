import pandas as pd
import numpy as np
import os
import sys
from pathlib import Path

# =========================================================
# 🔧 แก้ Path: ให้ไฟล์ใน services มองเห็น config ที่อยู่ข้างนอก
# =========================================================
# ถอยหลัง 1 ขั้น (จาก services -> backend) เพื่อหา config.py
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from config import DATA_FILE_PATH, BASE_DIR
except ImportError:
    print("❌ Error: หาไฟล์ config.py ไม่เจอ กรุณาเช็คว่ารันจาก folder 'backend' หรือไม่")
    sys.exit(1)

# กำหนดที่อยู่ไฟล์ที่จะ save (save ลง backend/data/user_ratings.csv)
OUTPUT_RATINGS_FILE = BASE_DIR / 'data' / 'user_ratings.csv'

def generate_file():
    print(f"1️⃣  กำลังอ่านข้อมูลสินค้าจาก: {DATA_FILE_PATH.name}")
    
    try:
        # อ่านไฟล์สินค้าหลัก
        product_df = pd.read_csv(DATA_FILE_PATH, encoding='utf-8-sig')
        
        # ✅ เช็คว่ามีคอลัมน์ id หรือไม่
        if 'id' not in product_df.columns:
            print(f"❌ Error: ไม่พบคอลัมน์ 'id' ในไฟล์ CSV (พบแต่: {list(product_df.columns)})")
            return

        # ดึง ID สินค้าทั้งหมดออกมา
        product_ids = product_df['id'].unique()
        print(f"📦 พบสินค้าทั้งหมด: {len(product_ids)} รายการ")
        
        # --- เริ่มการสุ่ม (User 100 คน, 1000 รีวิว) ---
        print("2️⃣  กำลังสุ่มสร้าง User Ratings...")
        np.random.seed(42)
        num_ratings = 1000 
        
        users = np.random.randint(1, 101, size=num_ratings) # User 1-100
        items = np.random.choice(product_ids, size=num_ratings) # สุ่มสินค้าจาก ID จริงๆ
        ratings = np.random.randint(3, 6, size=num_ratings) # คะแนน 3-5
        
        # สร้าง DataFrame
        ratings_df = pd.DataFrame({
            'user_id': users,
            'product_id': items,
            'rating': ratings
        })
        
        # ลบข้อมูลซ้ำ (User คนเดิม ให้คะแนนสินค้าเดิม)
        ratings_df = ratings_df.drop_duplicates(subset=['user_id', 'product_id'])
        
        # บันทึกไฟล์
        ratings_df.to_csv(OUTPUT_RATINGS_FILE, index=False, encoding='utf-8')
        
        print("-" * 30)
        print(f"✅ สำเร็จ! สร้างไฟล์ Rating ไว้ที่:")
        print(f"📂 {OUTPUT_RATINGS_FILE}")
        print(f"📊 จำนวนรีวิวที่ได้: {len(ratings_df)} แถว")
        print("-" * 30)

    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {e}")

if __name__ == "__main__":
    generate_file()