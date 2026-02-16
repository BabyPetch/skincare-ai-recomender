import pandas as pd
import psycopg2
from psycopg2.extras import Json
import re
import os
import sys

# 1. เชื่อมต่อ Database (ปรับปรุงเพื่อป้องกันการค้าง)
try:
    print("⌛ กำลังพยายามเชื่อมต่อฐานข้อมูล...")
    conn = psycopg2.connect(
        dbname="skincareCollectionDB",
        user="postgres",
        password="1234", 
        host="127.0.0.1",   # เปลี่ยน localhost เป็น 127.0.0.1 เพื่อความชัวร์
        port="5432",
        connect_timeout=5   # ถ้า 5 วินาทีเชื่อมไม่ได้ ให้หยุดค้างทันที
    )
    cur = conn.cursor()
    print("✅ เชื่อมต่อฐานข้อมูลสำเร็จ!")
except Exception as e:
    print(f"❌ เชื่อมต่อไม่ได้เพราะ: {e}")
    print("\n💡 คำแนะนำ: เช็คว่าเปิด pgAdmin 4 ไว้หรือยัง หรือชื่อ DB สะกดตรงไหม")
    sys.exit()

# 2. พาธไฟล์
csv_path = os.path.join('data', 'Data_Collection_ASA - data.csv')

try:
    df = pd.read_csv(csv_path, encoding='utf-8-sig')
    # ✨ เพิ่มบรรทัดนี้: เปลี่ยนค่าว่าง (NaN) ทั้งหมดในไฟล์ให้เป็นข้อความว่าง ""
    df = df.fillna("") 
    print(f"📦 อ่านไฟล์ CSV สำเร็จ: พบข้อมูล {len(df)} รายการ")
except FileNotFoundError:
    print(f"❌ ไม่พบไฟล์ CSV ที่: {csv_path}")
    sys.exit()

# ปรับฟังก์ชันคลีนราคาให้รองรับค่าว่างมากขึ้น
def clean_price(price_val):
    if price_val == "" or pd.isna(price_val): return 0
    cleaned = re.sub(r'[^\d.]', '', str(price_val))
    return float(cleaned) if cleaned else 0

print("🚀 กำลังเริ่มนำข้อมูลเข้าฐานข้อมูล...")

# 3. วนลูป Insert ข้อมูล
count = 0
for index, row in df.iterrows():
    # กรองแถวที่ไม่มีชื่อสินค้า (แถวว่างท้ายไฟล์)
    if not row.get('name') or str(row.get('name')).lower() == "nan":
        continue

    name = row.get('name', 'Unknown')
    brand = row.get('brand', 'Unknown')
    price = clean_price(row.get('price (bath)', 0))
    category = row.get('type_of_product', 'unknown')

    # ข้อมูลในนี้จะเป็นข้อความว่าง "" แทนที่จะเป็น NaN แล้ว
    details_data = {
        "skintype": row.get('skintype', ''),
        "size": row.get('size', ''),
        "ingredients": row.get('ingredients', ''),
        "active_ingredients": row.get('active ingredients', ''),
        "benefits": row.get('คุณสมบัติ(จากactive ingredients)', '')
    }

    sql = """
        INSERT INTO products (name, brand, price, category, details)
        VALUES (%s, %s, %s, %s, %s)
    """
    
    try:
        cur.execute(sql, (name, brand, price, category, Json(details_data)))
        count += 1
    except Exception as e:
        print(f"⚠️ แถวที่ {index+1} ({name}) มีปัญหา: {e}")
        conn.rollback()
        continue

# ยืนยันการบันทึก
conn.commit()
cur.close()
conn.close()

print(f"✨ เสร็จสมบูรณ์! นำเข้าข้อมูลทั้งหมด {count} รายการเรียบร้อยแล้ว")
