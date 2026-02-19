from database.repository import get_all_products

products = get_all_products()

print("จำนวนสินค้า:", len(products))

if products:
    print("ตัวอย่างสินค้า:")
    print(products[0])