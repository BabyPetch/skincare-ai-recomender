import requests
from bs4 import BeautifulSoup
import time
import random

BASE_URL = "https://incidecoder.com/products?page={}"

product_links = []
headers = {"User-Agent": "Mozilla/5.0"}

for page in range(1, 26):
    print(f"Scraping page {page}...")

    url = BASE_URL.format(page)
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, "html.parser")

    # หา box สินค้าแต่ละตัว
    product_boxes = soup.find_all("div", class_="previewbox-v2")

    for box in product_boxes:
        a_tag = box.find("a")
        if a_tag and "href" in a_tag.attrs:
            link = "https://incidecoder.com" + a_tag["href"]
            product_links.append(link)

    time.sleep(random.uniform(1, 2))

print("Total links:", len(product_links))

with open("product_links.txt", "w", encoding="utf-8") as f:
    for link in product_links:
        f.write(link + "\n")
print("Links saved to product_links.txt")