from fastapi import FastAPI, HTTPException
import psycopg2
from psycopg2.extras import RealDictCursor
from pydantic import BaseModel

app = FastAPI()

# ฟังก์ชันเชื่อมต่อฐานข้อมูล (ใช้การตั้งค่าเดียวกับตอน Migrate)
def get_db_connection():
    try:
        conn = psycopg2.connect(
            dbname="skincareCollectionDB",
            user="postgres",
            password="1234",     # <--- เช็ค Password อีกทีนะครับ
            host="127.0.0.1",    # ใช้ IP เพื่อกันเหนียวเรื่อง localhost
            port="5432"
        )
        return conn
    except Exception as e:
        print(f"Error connecting to DB: {e}")
        return None

# 1. หน้าแรก (Root) เอาไว้เช็คว่า Server ทำงานไหม
@app.get("/")
def read_root():
    return {"message": "Skincare AI API is running! 🚀"}

# 2. API ดึงข้อมูลสินค้าทั้งหมด
@app.get("/products")
def get_all_products():
    conn = get_db_connection()
    if conn is None:
        raise HTTPException(status_code=500, detail="Database Connection Failed")
    
    cur = conn.cursor(cursor_factory=RealDictCursor) # ดึงข้อมูลออกมาเป็น JSON สวยๆ
    cur.execute("SELECT * FROM products")
    products = cur.fetchall()
    
    cur.close()
    conn.close()
    return {"count": len(products), "data": products}

# 3. API ค้นหาสินค้าตามแบรนด์ (เช่น /products/search?brand=CeraVe)
@app.get("/products/search")
def search_products(brand: str = ""):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    # ใช้ ILIKE เพื่อให้ค้นหาแบบไม่สนตัวพิมพ์เล็ก-ใหญ่
    sql = "SELECT * FROM products WHERE brand ILIKE %s"
    cur.execute(sql, (f"%{brand}%",))
    products = cur.fetchall()
    
    cur.close()
    conn.close()
    return products