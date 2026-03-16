import pandas as pd
import requests
import re
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed

# ===== FILE PATH =====
INPUT_FILE = "data_products/incidecoder_20260314_130516.csv"
OUTPUT_FILE = "data_products/incidecoder_with_prices.csv"

# ===== SPEED =====
MAX_WORKERS = 30


# ===== CLEAN CHAR =====
ILLEGAL_CHARACTERS_RE = re.compile(r'[\000-\010]|[\013-\014]|[\016-\037]')

def clean_excel(val):
    if isinstance(val, str):
        return ILLEGAL_CHARACTERS_RE.sub("", val)
    return val


# ===== GET PRICE FROM SHOPEE =====
def get_price(query):

    try:

        url = f"https://shopee.co.th/search?keyword={query}"

        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        r = requests.get(url, headers=headers, timeout=10)

        text = r.text

        # หา pattern ราคา
        match = re.search(r'฿\s?([\d,]+)', text)

        if match:
            return int(match.group(1).replace(",", ""))

    except:
        pass

    return None


def process_product(idx, row):

    brand = str(row.get("brand", ""))
    name = str(row.get("name", ""))

    # query ให้หาเจอง่ายขึ้น
    query = f"{brand} {name} skincare"

    price = get_price(query)

    return idx, price


# ===== MAIN =====
def main():

    print("Loading dataset...")

    df = pd.read_csv(INPUT_FILE)

    prices = [None] * len(df)

    print("Scraping prices from Shopee...")

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:

        futures = [
            executor.submit(process_product, idx, row)
            for idx, row in df.iterrows()
        ]

        for future in tqdm(as_completed(futures), total=len(futures)):

            idx, price = future.result()
            prices[idx] = price

    df["price_thb"] = prices

    print("Cleaning characters...")

    df = df.map(clean_excel)

    print("Saving file...")

    df.to_csv(OUTPUT_FILE, index=False)

    print("Done!")
    print("Saved:", OUTPUT_FILE)


if __name__ == "__main__":
    main()
