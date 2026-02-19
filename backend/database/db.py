import psycopg2
import os

DB_CONFIG = {
    "dbname": "skincareCollectionDB",
    "user": "postgres",
    "password": "1234",
    "host": "127.0.0.1",
    "port": "5432"
}

def get_connection():
    print("🔗 Connecting to DB...")
    return psycopg2.connect(**DB_CONFIG)


def init_database():
    conn = get_connection()
    try:
        cur = conn.cursor()

        schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")

        with open(schema_path, "r", encoding="utf-8") as f:
            cur.execute(f.read())

        conn.commit()
        print("✅ Database schema created successfully.")

    finally:
        conn.close()
