from pathlib import Path
import os

# หา Path ปัจจุบันของโปรเจกต์
BASE_DIR = Path(__file__).parent

# Path ไปยังไฟล์ข้อมูล
DATA_FILE_PATH = BASE_DIR / 'data' / 'Data_Collection_ASA - data.csv'
USERS_FILE_PATH = BASE_DIR / 'data' / 'users.json'

# Mapping ลำดับการใช้สกินแคร์ (เพิ่มคำศัพท์ให้ครอบคลุมมากขึ้น)
ROUTINE_MAP = {
    # Step 1: ล้างหน้า
    "cleanser": 1, 
    "cleansing": 1, 
    "foam": 1, 
    "wash": 1, 
    "soap": 1, 
    "micellar": 1,
    "makeup remover": 1,

    # Step 2: ปรับสภาพผิว
    "toner": 2, 
    "lotion": 2, # น้ำตบญี่ปุ่นมักเรียก Lotion
    "mist": 2,

    # Step 3: บำรุงเข้มข้น
    "serum": 3, 
    "essence": 3, 
    "ampoule": 3, 
    "treatment": 3,

    # Step 4: มอยส์เจอไรเซอร์
    "moisturizer": 4, 
    "cream": 4, 
    "emulsion": 4, 
    "gel": 4, 
    "balm": 4, 
    "soothing": 4,

    # Step 5: กันแดด
    "sunscreen": 5, 
    "sun": 5, 
    "spf": 5, 
    "uv": 5
}

class Config:
    DEBUG = True
    PORT = 5000
    AUTO_IMPORT = os.getenv("AUTO_IMPORT", "false")