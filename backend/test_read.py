import pandas as pd
import os

# ลองอ่านไฟล์ดู
try:
    path = 'data/user_ratings.csv' # หรือ path เต็ม
    if os.path.exists(path):
        df = pd.read_csv(path)
        print("✅ อ่านไฟล์สำเร็จ!")
        print(df.head())
        print("-" * 20)
        print("🔍 เช็ค Data Type:")
        print(df.dtypes)
    else:
        print("❌ หาไฟล์ไม่เจอจ้า")
except Exception as e:
    print(f"❌ Error: {e}")