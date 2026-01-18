from pathlib import Path

# หา Path ปัจจุบันของโปรเจกต์
BASE_DIR = Path(__file__).parent

# Path ไปยังไฟล์ข้อมูล
DATA_FILE_PATH = BASE_DIR / 'data' / 'Data_Collection_ASA - data.csv'
USERS_FILE_PATH = BASE_DIR / 'data' / 'users.json'

# Mapping ลำดับการใช้สกินแคร์
ROUTINE_MAP = {
    "cleanser": 1, "toner": 2, "serum": 3, "essence": 3,
    "moisturizer": 4, "cream": 4, "sunscreen": 5
}