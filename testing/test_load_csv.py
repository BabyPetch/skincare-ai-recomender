# -*- coding: utf-8 -*-
import sys
import io
from pathlib import Path

# แก้ปัญหาการแสดงผลภาษาไทย
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import pandas as pd

DATA_FILE = Path('data/Data_Collection_ASA - data.csv')  

data = pd.read_csv(DATA_FILE, encoding='utf-8-sig')

print("โหลดข้อมูลสำเร็จ \n")
print(data.head())
print("\nคอลัมน์ทั้งหมด:", list(data.columns))

# เพิ่มข้อมูลเพิ่มเติม
print("\nจำนวนแถว:", len(data))
print("\nชนิดข้อมูลแต่ละคอลัมน์:")
print(data.dtypes)
print("\nตัวอย่างข้อมูลคอลัมน์แรก 5 คอลัมน์:")
print(data.iloc[:5, :5])