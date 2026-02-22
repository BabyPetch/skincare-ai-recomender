from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time
import random
import os
import datetime

# ===============================
# CONFIG
# ===============================

HEADLESS = True
INPUT_FILE = "product_links.txt"

# ใส่ timestamp กันไฟล์ชน
timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
OUTPUT_FILE = f"products_clean_{timestamp}.csv"

# ===============================
# ACTIVE TAG RULES
# ===============================

ACTIVE_RULES = {
    "retinol": ["retinol"],
    "retinal": ["retinal"],
    "aha": ["glycolic acid", "lactic acid", "mandelic acid"],
    "bha": ["salicylic acid"],
    "pha": ["gluconolactone"],
    "vitamin_c": ["ascorb", "ascorbyl"],
    "niacinamide": ["niacinamide"],
    "peptide": ["peptide"],
    "ceramide": ["ceramide"],
    "zinc_oxide": ["zinc oxide"],
    "titanium_dioxide": ["titanium dioxide"]
}

# ===============================
# FUNCTION RULES
# ===============================

FUNCTION_RULES = {
    "brightening": ["ascorb", "niacinamide", "arbutin"],
    "anti_aging": ["retinol", "retinal", "peptide"],
    "acne_control": ["salicylic acid"],
    "calming": ["centella", "allantoin"],
    "barrier_repair": ["ceramide"],
    "hydrating": ["hyaluronic", "glycerin"],
    "exfoliating": ["glycolic", "salicylic", "lactic"]
}

# ===============================
# HELPER FUNCTIONS
# ===============================

def detect_subtype(name, ingredients, major_category):
    text = (name + " " + ingredients).lower()

    if major_category == "sunscreen":
        if "zinc oxide" in text or "titanium dioxide" in text:
            return "mineral_sunscreen"
        return "chemical_or_hybrid_sunscreen"

    if "retinol" in text:
        return "retinol_serum"

    if "salicylic acid" in text:
        return "bha_exfoliator"

    if "glycolic acid" in text:
        return "aha_exfoliator"

    return major_category


def detect_tags(text, rules):
    tags = set()
    text = text.lower()
    for tag, keywords in rules.items():
        if any(kw in text for kw in keywords):
            tags.add(tag)
    return list(tags)


# ===============================
# SETUP DRIVER
# ===============================

chrome_options = Options()
if HEADLESS:
    chrome_options.add_argument("--headless=new")

chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=chrome_options
)

products_data = []

# ===============================
# LOAD LINKS
# ===============================

if not os.path.exists(INPUT_FILE):
    raise FileNotFoundError(f"{INPUT_FILE} not found")

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    lines = [line.strip() for line in f if line.strip()]

# ===============================
# SCRAPING LOOP
# ===============================

for idx, line in enumerate(lines):
    if "|" in line:
        link, major_category = line.split("|", 1)
    else:
        link = line
        major_category = "unknown"

    print(f"Scraping {idx+1}/{len(lines)}")

    try:
        driver.get(link)
        time.sleep(random.uniform(2, 4))

        # Name
        try:
            name = driver.find_element(By.TAG_NAME, "h1").text.strip()
        except:
            name = ""

        # Brand
        try:
            brand = driver.find_element(By.CSS_SELECTOR, ".breadcrumb a").text.strip()
        except:
            brand = ""

        # Ingredients
        try:
            ingredient_elements = driver.find_elements(By.CSS_SELECTOR, "a.ingred-link")
            ingredients_list = [
                el.text.strip()
                for el in ingredient_elements
                if el.text.strip()
            ]
        except:
            ingredients_list = []

        ingredients_raw = ", ".join(ingredients_list)

        # AI Fields
        subtype = detect_subtype(name, ingredients_raw, major_category)
        active_tags = detect_tags(ingredients_raw, ACTIVE_RULES)
        function_tags = detect_tags(ingredients_raw, FUNCTION_RULES)

        products_data.append({
            "product_url": link,
            "name": name,
            "brand": brand,
            "major_category": major_category,
            "subtype": subtype,
            "active_tags": ",".join(active_tags),
            "function_tags": ",".join(function_tags),
            "ingredients_raw": ingredients_raw,
            "ingredients_list": ",".join(ingredients_list)
        })

    except Exception as e:
        print("Error:", e)

    time.sleep(random.uniform(1, 2))

driver.quit()

# ===============================
# SAVE CSV
# ===============================

df = pd.DataFrame(products_data)

try:
    df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")
    print(f"✅ Done scraping and saved to {OUTPUT_FILE}")
except PermissionError:
    print("❌ Permission denied. Close the CSV file if it is open and try again.")