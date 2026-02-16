import pandas as pd
import psycopg2
import re
import os

def import_csv_to_db():
    print("🔍 กำลังตรวจสอบข้อมูลในตาราง Products...")
    try:
        # 1. เชื่อมต่อ DB
        conn = psycopg2.connect(
            dbname="skincareCollectionDB",
            user="postgres",
            password="1234", 
            host="127.0.0.1",
            port="5432"
        )
        cur = conn.cursor()

        # ✨ 2. เช็คว่ามีข้อมูลอยู่แล้วหรือยัง?
        cur.execute("SELECT COUNT(*) FROM products")
        count = cur.fetchone()[0]

        if count > 0:
            print(f"✅ มีข้อมูลสกินแคร์ในระบบแล้ว {count} รายการ (ข้ามการดึงไฟล์ CSV)")
            cur.close()
            conn.close()
            return  # หยุดทำงานฟังก์ชันนี้ไปเลย ไม่ต้อง Insert ซ้ำ

        # 3. ถ้ายังไม่มีข้อมูล ให้เริ่มดึงไฟล์ CSV
        print("⚠️ ยังไม่มีข้อมูลสกินแคร์! เริ่มกระบวนการดึงข้อมูลจากไฟล์ CSV...")
        csv_path = os.path.join('data', 'Data_Collection_ASA - data.csv')

        if not os.path.exists(csv_path):
            print(f"❌ ไม่พบไฟล์ CSV ที่: {csv_path} (โปรดเช็คโฟลเดอร์ data)")
            return

        df = pd.read_csv(csv_path, encoding='utf-8-sig')
        df = df.fillna("") 
        print(f"📦 อ่านไฟล์ CSV สำเร็จ: พบข้อมูล {len(df)} รายการ")

        def clean_price(price_val):
            if price_val == "" or pd.isna(price_val): return 0
            cleaned = re.sub(r'[^\d.]', '', str(price_val))
            return float(cleaned) if cleaned else 0

        # 4. วนลูป Insert
        inserted_count = 0
        for index, row in df.iterrows():
            if not row.get('name') or str(row.get('name')).lower() == "nan" or row.get('name') == "":
                continue

            name = row.get('name', 'Unknown')
            brand = row.get('brand', 'Unknown')
            price = clean_price(row.get('price (bath)', 0))
            category = row.get('type_of_product', 'unknown')
            skin_type = row.get('skintype', '')
            
            ing_normal = row.get('ingredients', '')
            ing_active = row.get('active ingredients', '')
            ingredients = f"Active: {ing_active} | All: {ing_normal}" if ing_active else ing_normal
            description = row.get('คุณสมบัติ(จากactive ingredients)', '')

            sql = """
                INSERT INTO products (name, brand, category, skin_type, ingredients, description, price)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            
            try:
                cur.execute(sql, (name, brand, category, skin_type, ingredients, description, price))
                inserted_count += 1
            except Exception as e:
                print(f"⚠️ แถวที่ {index+1} ({name}) มีปัญหา: {e}")
                conn.rollback()
                continue

        conn.commit()
        cur.close()
        conn.close()
        print(f"✨ นำเข้าข้อมูล CSV ลงฐานข้อมูลสำเร็จ {inserted_count} รายการ!")

    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในการนำเข้าข้อมูล: {e}")