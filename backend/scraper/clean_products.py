import pandas as pd

# โหลดไฟล์
df = pd.read_csv("products_clean.csv")

# ลบ newline ในชื่อ
df["name"] = df["name"].str.replace("\n", " ", regex=False)

# เติม brand ถ้าว่าง (ดึงจาก name คำแรก)
df["brand"] = df["brand"].fillna(df["name"].str.split().str[0])

# ลบ duplicate
df = df.drop_duplicates(subset=["product_url"])

# save ใหม่
df.to_csv("products_final.csv", index=False)

print("Clean complete ✅")