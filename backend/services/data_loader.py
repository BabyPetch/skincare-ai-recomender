import pandas as pd
from database.db import get_connection
from psycopg2.extras import RealDictCursor

class DataLoader:

    def load_products(self):
        conn = get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        cur.execute("SELECT * FROM products")
        rows = cur.fetchall()
        conn.close()

        if not rows:
            return pd.DataFrame()

        df = pd.DataFrame(rows)

        df['price'] = pd.to_numeric(df['price'], errors='coerce').fillna(0)

        for col in ['skintype', 'benefits', 'ingredients']:
            if col not in df.columns:
                df[col] = ""

        return df
