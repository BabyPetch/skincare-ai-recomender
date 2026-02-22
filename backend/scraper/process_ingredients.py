import pandas as pd

df = pd.read_csv("products_final.csv")

# แยก ingredient เป็น list
df["ingredients_list"] = df["ingredients_raw"].apply(
    lambda x: [i.strip().lower() for i in str(x).split(",")]
)

# save
df.to_csv("products_processed.csv", index=False)

print("Ingredients processed ✅")