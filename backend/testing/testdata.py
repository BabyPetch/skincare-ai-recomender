# -*- coding: utf-8 -*-
import sys
import io
import pandas as pd
from pathlib import Path

if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

DATA_FILE = Path('backend\data\Data_Collection_ASA - data.csv')  

data = pd.read_csv(DATA_FILE, encoding='utf-8-sig')

print("=" * 60)
print("การวิเคราะห์ข้อมูล")
print("=" * 60)

print(f"\n✓ โหลดข้อมูลสำเร็จ: {len(data)} รายการ")
print(f"✓ จำนวนคอลัมน์: {len(data.columns)}")

print("\n📋 คอลัมน์ทั้งหมด:")
for i, col in enumerate(data.columns, 1):
    print(f"  {i}. '{col}'")

print("\n📊 ข้อมูล 3 แถวแรก:")
print(data.head(3))

print("\n🔍 ตรวจสอบคอลัมน์ที่สำคัญ:")

# หาคอลัมน์ skin type
skintype_cols = [col for col in data.columns if 'skin' in col.lower()]
print(f"  - คอลัมน์ที่เกี่ยวกับ skin: {skintype_cols}")

# หาคอลัมน์ product name
name_cols = [col for col in data.columns if 'name' in col.lower() or 'product' in col.lower()]
print(f"  - คอลัมน์ที่เกี่ยวกับ name/product: {name_cols}")

# ถ้ามีคอลัมน์ skin type แสดงค่าที่ไม่ซ้ำกัน
if skintype_cols:
    col = skintype_cols[0]
    unique_vals = data[col].dropna().unique()
    print(f"\n ค่าที่ไม่ซ้ำในคอลัมน์ '{col}':")
    for val in unique_vals[:10]:  # แสดงแค่ 10 ค่าแรก
        count = (data[col] == val).sum()
        print(f"  - '{val}' ({count} รายการ)")

print("\n" + "=" * 60)