# -*- coding: utf-8 -*-
import sys
import io
import pandas as pd
from pathlib import Path

# ตั้งค่า encoding สำหรับแสดงภาษาไทย
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# ตั้งชื่อไฟล์ข้อมูล
DATA_FILE = Path('C:/Users/Petch/Desktop/Projectskin/skincare-ai-recomender/data/Data_Collection_ASA - data.csv')

def recommend_products_by_skin_type(user_skin_type):
    """
    ฟังก์ชันแนะนำผลิตภัณฑ์ตามประเภทผิว
    
    Args:
        user_skin_type (str): ประเภทผิวที่ต้องการค้นหา (เช่น 'oily', 'dry', 'combination')
    
    Returns:
        list: รายการชื่อผลิตภัณฑ์ที่เหมาะสม
    """
    print(f"กำลังค้นหาผลิตภัณฑ์สำหรับผิว '{user_skin_type}'...")

    # อ่านไฟล์ CSV
    try:
        df = pd.read_csv(DATA_FILE, encoding='utf-8-sig')
        print(f"✓ โหลดข้อมูลสำเร็จ: {len(df)} รายการ")
    except FileNotFoundError:
        print(f"✗ หาไฟล์ไม่เจอ: {DATA_FILE}")
        print(f"  กรุณาตรวจสอบว่าไฟล์อยู่ในตำแหน่งที่ถูกต้อง")
        return []
    except Exception as e:
        print(f"✗ เกิดข้อผิดพลาดในการอ่านไฟล์: {e}")
        return []

    # แสดงข้อมูลเบื้องต้น
    print(f"✓ คอลัมน์ที่มี: {df.columns.tolist()}")
    
    # ตรวจสอบว่ามีคอลัมน์ที่ต้องการหรือไม่
    skintype_col = None
    name_col = None
    
    # หาคอลัมน์ skintype (ไม่สนใจช่องว่างและตัวพิมพ์)
    for col in df.columns:
        col_clean = col.strip().lower()
        if 'skin' in col_clean and 'type' in col_clean:
            skintype_col = col
        if col_clean in ['name', 'product_name', 'product name', 'productname']:
            name_col = col
    
    if skintype_col is None:
        print("✗ ไม่พบคอลัมน์ 'skintype' ในข้อมูล")
        print(f"  คอลัมน์ที่มี: {df.columns.tolist()}")
        return []
    
    if name_col is None:
        print("✗ ไม่พบคอลัมน์ 'name' ในข้อมูล")
        print(f"  คอลัมน์ที่มี: {df.columns.tolist()}")
        return []
    
    print(f"✓ ใช้คอลัมน์: skintype='{skintype_col}', name='{name_col}'")
    
    # แสดงประเภทผิวที่มีในข้อมูล
    unique_types = df[skintype_col].dropna().unique()
    print(f"✓ ประเภทผิวที่มีในข้อมูล: {unique_types.tolist()}")

    # กรองข้อมูล
    try:
        condition = df[skintype_col].fillna('').astype(str).str.contains(user_skin_type, case=False, na=False)
        recommended_df = df[condition]
        
        print(f"✓ พบผลิตภัณฑ์ที่ตรงกัน: {len(recommended_df)} รายการ")
        
        # ดึงรายชื่อผลิตภัณฑ์
        product_list = recommended_df[name_col].dropna().tolist()
        
        return product_list
    
    except Exception as e:
        print(f"✗ เกิดข้อผิดพลาดในการกรองข้อมูล: {e}")
        return []

def show_product_details(user_skin_type):
    """
    แสดงรายละเอียดผลิตภัณฑ์ที่แนะนำ (เพิ่มเติม)
    """
    try:
        df = pd.read_csv(DATA_FILE, encoding='utf-8-sig')
        
        # หาคอลัมน์ skintype
        skintype_col = None
        for col in df.columns:
            if 'skin' in col.strip().lower() and 'type' in col.strip().lower():
                skintype_col = col
                break
        
        if skintype_col:
            condition = df[skintype_col].fillna('').astype(str).str.contains(user_skin_type, case=False, na=False)
            recommended_df = df[condition]
            
            if len(recommended_df) > 0:
                print(f"\n=== รายละเอียดผลิตภัณฑ์ (แสดง 10 รายการแรก) ===")
                # เลือกคอลัมน์สำคัญแสดง
                display_cols = [col for col in df.columns if col in ['name', 'brand', 'category', 'price', 'rating']]
                if display_cols:
                    print(recommended_df[display_cols].head(10).to_string(index=False))
    except Exception as e:
        print(f"ไม่สามารถแสดงรายละเอียดได้: {e}")

# --- ส่วนทดสอบการทำงาน ---
if __name__ == '__main__':
    print("=" * 60)
    print("ระบบแนะนำผลิตภัณฑ์ดูแลผิว")
    print("=" * 60)
    
    # ประเภทผิวที่ต้องการค้นหา
    user_input_skin_type = 'oily'  # เปลี่ยนเป็น 'dry', 'combination', 'sensitive' ได้
    
    # เรียกใช้ฟังก์ชัน
    recommendations = recommend_products_by_skin_type(user_input_skin_type)
    
    # แสดงผลลัพธ์
    print("\n" + "=" * 60)
    if recommendations:
        print(f"ผลิตภัณฑ์ที่แนะนำสำหรับผิว '{user_input_skin_type}'")
        print("=" * 60)
        for i, product in enumerate(recommendations[:20], 1):  # แสดงแค่ 20 รายการแรก
            print(f"{i:2d}. {product}")
        
        if len(recommendations) > 20:
            print(f"\n... และอีก {len(recommendations) - 20} รายการ")
        
        print(f"\nรวมทั้งหมด: {len(recommendations)} ผลิตภัณฑ์")
        
        # แสดงรายละเอียดเพิ่มเติม
        show_product_details(user_input_skin_type)
    else:
        print(f"ไม่พบผลิตภัณฑ์สำหรับผิว '{user_input_skin_type}'")
        print("\nคำแนะนำ:")
        print("1. ตรวจสอบว่าใช้ชื่อประเภทผิวถูกต้อง")
        print("2. ลองใช้คำค้นหาอื่น เช่น 'dry', 'combination', 'sensitive'")
        print("3. ตรวจสอบข้อมูลในไฟล์ CSV ว่ามีข้อมูลครบถ้วน")
    print("=" * 60)