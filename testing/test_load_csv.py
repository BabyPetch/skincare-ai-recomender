# -*- coding: utf-8 -*-
import sys
import io

# แก้ปัญหาการแสดงผลภาษาไทย
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import pandas as pd

file_path = r"C:\Users\Petch\Desktop\Projectskin\skincare-ai-recomender\data\Data_Collection_ASA - data.csv"

data = pd.read_csv(file_path, encoding='utf-8-sig')

print("โหลดข้อมูลสำเร็จ ✅\n")
print(data.head())
print("\nคอลัมน์ทั้งหมด:", list(data.columns))

# เพิ่มข้อมูลเพิ่มเติม
print("\nจำนวนแถว:", len(data))
print("\nชนิดข้อมูลแต่ละคอลัมน์:")
print(data.dtypes)
print("\nตัวอย่างข้อมูลคอลัมน์แรก 5 คอลัมน์:")
print(data.iloc[:5, :5])