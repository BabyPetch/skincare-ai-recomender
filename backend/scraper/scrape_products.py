import requests
from bs4 import BeautifulSoup
import json
import time
import random

headers = {"User-Agent": "Mozilla/5.0"}

products_data = []

with open("product_links.txt", "r", encoding="utf-8") as f:
    links = f.readlines()

for idx, link in enumerate(links):
    link = link.strip()
    print(f"Scraping {idx+1}/{len(links)}")

    res = requests.get(link, headers=headers)
    soup = BeautifulSoup(res.text, "html.parser")

    # product name
    name_tag = soup.find("h1")
    name = name_tag.text.strip() if name_tag else None

    # brand
    brand_tag = soup.find("div", class_="brand-title")
    brand = brand_tag.text.strip() if brand_tag else None

    # ingredients
    ingredients_section = soup.find("div", class_="ingredients-list")

    if ingredients_section:
        ingredients = ingredients_section.text.strip()
    else:
        ingredients = None

    products_data.append({
        "product_url": link,
        "name": name,
        "brand": brand,
        "ingredients_raw": ingredients
    })

    time.sleep(random.uniform(1, 2))

# save
with open("products_raw.json", "w", encoding="utf-8") as f:
    json.dump(products_data, f, ensure_ascii=False, indent=4)

print("Done scraping!")
