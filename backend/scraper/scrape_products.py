from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import pandas as pd
import time
import random

# ===== Setup headless browser =====
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")

from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=chrome_options
)

products_data = []

with open("product_links.txt", "r", encoding="utf-8") as f:
    links = f.readlines()

for idx, link in enumerate(links):
    link = link.strip()
    print(f"Scraping {idx+1}/{len(links)}")

    driver.get(link)
    time.sleep(3)  # wait JS render

    # ===== Product Name =====
    try:
        name = driver.find_element(By.TAG_NAME, "h1").text
    except:
        name = None

    # ===== Brand (breadcrumb area) =====
    try:
        brand = driver.find_element(By.CSS_SELECTOR, ".breadcrumb a").text
    except:
        brand = None

    # ===== Ingredients =====
    # ===== Ingredients (correct for INCIDecoder) =====
# ===== Ingredients (correct for INCIDecoder) =====
    try:
        ingredient_elements = driver.find_elements(By.CSS_SELECTOR, "a.ingred-link")
        ingredients_list = [el.text.strip() for el in ingredient_elements if el.text.strip()]
        ingredients = ", ".join(ingredients_list)
    except:
        ingredients = None

    products_data.append({
        "product_url": link,
        "name": name,
        "brand": brand,
        "ingredients_raw": ingredients
    })

    time.sleep(random.uniform(1, 2))

driver.quit()

# ===== Save Excel =====
df = pd.DataFrame(products_data)
df.to_excel("products_raw.xlsx", index=False)

print("✅ Done scraping and saved to Excel!")