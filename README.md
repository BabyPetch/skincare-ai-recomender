# 🧴 Skincare AI Recommender

ระบบแนะนำผลิตภัณฑ์ดูแลผิวโดย AI ที่ช่วยวิเคราะห์สภาพผิวและแนะนำสกินแคร์ที่เหมาะสมกับผู้ใช้แต่ละคน

---

## ✨ Features

- 🔍 **AI-Powered Recommendation** — แนะนำสกินแคร์โดยใช้ TF-IDF + Cosine Similarity
- 👤 **User Authentication** — สมัครสมาชิก / เข้าสู่ระบบ
- 📋 **History Tracking** — บันทึกประวัติการแนะนำผลิตภัณฑ์
- 🛡️ **Admin Panel** — จัดการผู้ใช้งานในระบบ
- 🧪 **Ingredient Analysis** — วิเคราะห์ส่วนประกอบจาก InciDecoder

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python, Flask, Flask-CORS |
| Database | PostgreSQL (psycopg2) |
| AI/ML | scikit-learn (TF-IDF, Cosine Similarity) |
| Frontend | React |
| Scraper | Python (Scrapy / BeautifulSoup) |

---

## 📁 Project Structure
```
skincare-ai-recommender/
├── backend/
│   ├── app.py              # Entry point
│   ├── config.py           # App config (ต้องสร้างเอง)
│   ├── database/
│   │   └── db.py           # DB connection
│   ├── routes/             # API routes
│   ├── services/           # Business logic & AI engine
│   └── scraper/            # Data scraping scripts
└── frontend/               # React frontend
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.9+
- PostgreSQL
- Node.js (สำหรับ frontend)

### 1. Clone the repo
```bash
git clone https://github.com/your-username/skincare-ai-recommender.git
cd skincare-ai-recommender
```

### 2. Setup Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. ตั้งค่า Environment Variables
สร้างไฟล์ `.env` ในโฟลเดอร์ `backend/`:
```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=skincare_db
DB_USER=your_db_user
DB_PASSWORD=your_db_password
SECRET_KEY=your_secret_key
```

### 4. รัน Backend
```bash
python app.py
```
Backend จะรันที่ `http://localhost:5000`

### 5. Setup Frontend
```bash
cd frontend
npm install
npm start
```

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/login` | เข้าสู่ระบบ |
| POST | `/auth/register` | สมัครสมาชิก |
| POST | `/ai/recommend` | ขอคำแนะนำสกินแคร์ |
| GET | `/user/profile` | ดูข้อมูลผู้ใช้ |
| GET | `/admin/users` | ดูรายชื่อผู้ใช้ทั้งหมด (admin) |

---

## 👥 Contributors

- [@your-username](https://github.com/your-username)

---

## 📄 License

MIT License
