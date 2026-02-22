import pandas as pd

# อ่านไฟล์ Excel
df = pd.read_excel("products_raw.xlsx")

# เซฟเป็น CSV
df.to_csv("products_clean.csv", index=False, encoding="utf-8")

print("✅ Converted to CSV successfully!")