# 🧴 SkinCare AI — Personalized Skincare Recommendation System

> ระบบแนะนำสกินแคร์อัจฉริยะที่วิเคราะห์สภาพผิวและแนะนำผลิตภัณฑ์ที่เหมาะกับคุณโดยเฉพาะ

![React](https://img.shields.io/badge/React-18-61DAFB?style=flat-square&logo=react)
![Flask](https://img.shields.io/badge/Flask-3.x-000000?style=flat-square&logo=flask)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?style=flat-square&logo=postgresql)
![scikit-learn](https://img.shields.io/badge/scikit--learn-ML-F7931E?style=flat-square&logo=scikit-learn)
![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=flat-square&logo=python)

---

## ✨ Features

| Feature | Description |
|---|---|
| 🤖 **AI Recommendation Engine** | Multi-layer scoring: ML concern matching + TF-IDF cosine similarity + context boost |
| 🧪 **Ingredient Classifier** | Multi-label ML classifier บน active ingredients 200+ ชนิด ใน 9 หมวดหมู่ |
| 📋 **9-Step Skin Assessment** | วิเคราะห์ผิวแบบ step-by-step (ผิว, อายุ, เพศ, ความชุ่มชื้น, สภาพแวดล้อม ฯลฯ) |
| 🔖 **Bookmark & Review** | บันทึกสินค้าและเขียนรีวิวพร้อม rating system |
| ⚖️ **Product Compare** | เปรียบเทียบสินค้าสูงสุด 4 รายการด้วย Radar Chart |
| 📊 **Personal Dashboard** | วิเคราะห์แนวโน้มผิวและสถิติการใช้งานจากประวัติ |
| 🌙 **Dark / Light Mode** | รองรับ dark mode พร้อม theme toggle |
| 🛡️ **Admin Panel** | จัดการผู้ใช้งานพร้อม dashboard สรุปข้อมูล |

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                     React Frontend                       │
│  SkinAdvisor Quiz → Results → Compare / Bookmark        │
└─────────────────────────┬───────────────────────────────┘
                          │ REST API (HTTP/JSON)
┌─────────────────────────▼───────────────────────────────┐
│                   Flask Backend                          │
│  auth_routes  │  ai_routes  │  bookmark  │  review       │
└──────┬──────────────┬───────────────────────────────────┘
       │              │
┌──────▼──────┐ ┌─────▼──────────────────────────────────┐
│ PostgreSQL  │ │         AI Engine v2                    │
│  users      │ │  Layer 1: Concern ML Score (55%)        │
│  products   │ │  Layer 2: TF-IDF Cosine    (25%)        │
│  history    │ │  Layer 3: Context Boost    (20%)        │
│  bookmarks  │ │  Hard Filter: Skin Type                 │
│  reviews    │ └─────────────────────────────────────────┘
└─────────────┘
```

---

## 🤖 AI Recommendation Engine

ระบบแนะนำสินค้าใช้ **3-layer scoring formula**:

```
final_score = (concern_score × 0.55) + (cosine_score × 0.25) + (context_score × 0.20)
```

### Layer 1 — Concern ML Score (55%)
- ฝึก `OneVsRestClassifier` + `LogisticRegression` บน active ingredients 200+ ชนิด
- map ingredient → 9 หมวด: `acne`, `whitening`, `wrinkle`, `hydration`, `barrierrepair`, `soothing`, `oilcontrol`, `exfoliation`, `antioxidant`
- แต่ละ user concern มี weighted sub-category (เช่น `acne_control` → acne ×1.0, oilcontrol ×0.85, exfoliation ×0.70)

### Layer 2 — TF-IDF Cosine Similarity (25%)
- Vectorize `skintype + function_tags + brand + ingredients` ด้วย `char_wb` n-gram (3–5)
- cosine similarity ระหว่าง user input vector กับ product matrix

### Layer 3 — Context Boost (20%)
- ปรับ score ตาม age group, gender, hydration level, environment, experience, routine time
- เช่น `ac_all_day` → `hydrating +0.20`, `barrier_repair +0.15`

### Skin Type — Hard Filter
- กรองผลิตภัณฑ์ก่อน scoring ให้ตรงกับ skin type ของ user เสมอ

---

## 🛠️ Tech Stack

### Backend
- **Python 3.9+** — Flask, Flask-CORS
- **scikit-learn** — TF-IDF Vectorizer, Cosine Similarity, OneVsRest Classifier
- **PostgreSQL** — psycopg2, RealDictCursor
- **joblib** — model serialization

### Frontend
- **React 18** — Hooks, Context API, React Router v6
- **Chart.js / Recharts** — Radar Chart, Pie Chart
- **CSS Variables** — Dark/Light theme system

### Database Schema
```
users       — id, email, password, name, role, birthdate, gender
products    — id, name, brand, category, skintype, ingredients, function_tags, price, ...
history     — id, user_email, skin_type, concerns, recommended_products, routine_products
bookmarks   — id, user_email, product_name, brand, price, ...
reviews     — id, user_email, product_name, rating, title, body
active_ingredients — ingredient, acne, whitening, wrinkle, ... (9 boolean columns)
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.9+
- PostgreSQL 14+
- Node.js 18+

### 1. Clone the repository
```bash
git clone https://github.com/your-username/skincare-ai.git
cd skincare-ai
```

### 2. Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Environment Variables
สร้างไฟล์ `backend/config.py`:
```python
class Config:
    SECRET_KEY = "your-secret-key"
    DEBUG = True
```

และแก้ไข `backend/database/db.py`:
```python
DB_CONFIG = {
    "dbname":   "skincareCollectionDB",
    "user":     "your_db_user",
    "password": "your_db_password",
    "host":     "127.0.0.1",
    "port":     "5432"
}
```

### 4. Initialize Database & Run Backend
```bash
# สร้าง DB ก่อนใน PostgreSQL
createdb skincareCollectionDB

# รัน backend (จะ init schema + import data อัตโนมัติ)
python app.py
```

### 5. Train ML Model (optional — มี pre-trained ให้แล้ว)
```bash
cd backend/training
python train_concern_model.py
```

### 6. Frontend Setup
```bash
cd skincare-webapp
npm install
npm start
```

แอปจะรันที่ `http://localhost:3000` และ backend ที่ `http://localhost:5000`

### 7. Default Admin Account
```
Email:    admin@admin.com
Password: admin1234
```

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/login` | เข้าสู่ระบบ |
| `POST` | `/api/register` | สมัครสมาชิก |
| `POST` | `/api/recommend-all` | รับผลแนะนำสินค้า + routine พร้อมกัน |
| `POST` | `/api/recommend` | แนะนำสินค้า top N |
| `POST` | `/api/routine` | สร้าง skincare routine 5 ขั้นตอน |
| `GET`  | `/api/search?q=` | ค้นหาสินค้า |
| `GET`  | `/api/user/:email` | ดูข้อมูล + ประวัติ user |
| `POST` | `/api/bookmark` | toggle บันทึกสินค้า |
| `GET`  | `/api/bookmarks/:email` | ดึง bookmarks ของ user |
| `POST` | `/api/review` | เพิ่ม/แก้ไข review |
| `GET`  | `/api/reviews/:product_name` | ดู reviews ของสินค้า |
| `GET`  | `/api/admin/users` | ดูรายชื่อ users ทั้งหมด (admin) |
| `DELETE` | `/api/admin/users/:email` | ลบ user (admin) |

---

## 📁 Project Structure

```
skincare-ai/
├── backend/
│   ├── app.py                        # Flask entry point
│   ├── config.py                     # App config
│   ├── database/
│   │   ├── db.py                     # DB connection + init
│   │   ├── schema.sql                # Database schema
│   │   └── repository.py            # DB queries
│   ├── routes/
│   │   ├── auth_routes.py
│   │   ├── ai_routes.py
│   │   ├── bookmark_routes.py
│   │   ├── review_routes.py
│   │   ├── user_routes.py
│   │   └── admin_routes.py
│   ├── services/
│   │   ├── ai_engine_v2.py           # ⭐ Main AI engine
│   │   ├── user_manager.py
│   │   ├── data_loader.py
│   │   └── thai_mapping.py          # Thai → EN concern mapping
│   └── training/
│       ├── train_concern_model.py    # ML training script
│       └── model/
│           ├── concern_classifier.pkl
│           └── concern_meta.json
│
└── skincare-webapp/
    └── src/
        ├── App.js
        ├── pages/
        │   ├── SkinCareAdvisor.jsx   # ⭐ Main quiz flow
        │   ├── SearchPage.jsx
        │   ├── BookmarkPage.jsx
        │   ├── DashboardPage.jsx
        │   ├── ComparePage.jsx
        │   ├── UserProfile.jsx
        │   ├── AdminPage.jsx
        │   └── LoginPage.jsx
        └── components/
            ├── SkinAdvisor/          # Quiz step components
            └── Reviews/              # Bookmark, Review, ProductReviews
```

---

## 📸 Screenshots

> *(Add screenshots here)*

| Skin Assessment Quiz | Product Results | Compare Page |
|---|---|---|
| ![quiz]() | ![results]() | ![compare]() |

---

## 🧪 Algorithm Testing

มี test script สำหรับ validate recommendation algorithm:

```bash
cd backend/services
python ai_engine.py   # รัน 7 test cases (positive + negative)
```

Test cases ครอบคลุม: ผิวมันสิว, ผิวแห้งริ้วรอย, ผิวแพ้ง่ายฝ้า, edge case ไม่มี concern, และ negative test เพื่อตรวจว่า algorithm ไม่แนะนำสินค้าผิดประเภท

---

## 👤 Author

**[Attawat Kammas]**
- GitHub: [@your-username](https://github.com/BabyPetch)
- LinkedIn: [your-linkedin](https://www.linkedin.com/in/attawat-kammas-1b8115400 )

---

## 📄 License

MIT License — feel free to use this project as a reference or learning resource.
