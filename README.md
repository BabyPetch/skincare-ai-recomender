# 🧴 SkinCare AI — Personalized Skincare Recommendation System

> ระบบแนะนำสกินแคร์อัจฉริยะที่วิเคราะห์สภาพผิวและแนะนำผลิตภัณฑ์ที่เหมาะกับคุณโดยเฉพาะ

![React](https://img.shields.io/badge/React-18-61DAFB?style=flat-square\&logo=react)
![Flask](https://img.shields.io/badge/Flask-3.x-000000?style=flat-square\&logo=flask)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?style=flat-square\&logo=postgresql)
![scikit-learn](https://img.shields.io/badge/scikit--learn-ML-F7931E?style=flat-square\&logo=scikit-learn)
![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=flat-square\&logo=python)

---

## ✨ Features

| Feature                         | Description                                                                         |
| ------------------------------- | ----------------------------------------------------------------------------------- |
| 🤖 **AI Recommendation Engine** | Multi-layer scoring: ML concern matching + TF-IDF cosine similarity + context boost |
| 🧪 **Ingredient Classifier**    | Multi-label ML classifier บน active ingredients 200+ ชนิด ใน 9 หมวดหมู่             |
| 📋 **9-Step Skin Assessment**   | วิเคราะห์ผิวแบบ step-by-step เช่น สภาพผิว อายุ เพศ ความชุ่มชื้น และสภาพแวดล้อม      |
| 🔖 **Bookmark & Review**        | บันทึกสินค้าและเขียนรีวิวพร้อมระบบให้คะแนน                                          |
| ⚖️ **Product Compare**          | เปรียบเทียบสินค้าสูงสุด 4 รายการด้วย Radar Chart                                    |
| 📊 **Personal Dashboard**       | วิเคราะห์แนวโน้มผิวและสถิติการใช้งานจากประวัติ                                      |
| 🌙 **Dark / Light Mode**        | รองรับ dark mode พร้อม theme toggle                                                 |
| 🛡️ **Admin Panel**             | จัดการผู้ใช้งานพร้อม dashboard สรุปข้อมูล                                           |

---

## 🏗️ Architecture Overview

```text
┌─────────────────────────────────────────────────────────┐
│                    React Frontend                       │
│       SkinAdvisor Quiz → Results → Compare / Bookmark   │
└─────────────────────────┬───────────────────────────────┘
                          │ REST API (HTTP/JSON)
┌─────────────────────────▼───────────────────────────────┐
│                    Flask Backend                        │
│      auth_routes │ ai_routes │ bookmark │ review         │
└────────┬───────────────────────────┬────────────────────┘
         │                           │
┌────────▼─────────┐  ┌──────────────▼────────────────────┐
│   PostgreSQL     │  │             AI Engine             │
│   users          │  │  Layer 1: Concern ML Score (55%)  │
│   products       │  │  Layer 2: TF-IDF Cosine (25%)     │
│   history        │  │  Layer 3: Context Boost (20%)     │
│   bookmarks      │  │  Hard Filter: Skin Type           │
│   reviews        │  └───────────────────────────────────┘
└──────────────────┘
```

---

## 🤖 AI Recommendation Engine

ระบบแนะนำสินค้าใช้ **3-layer scoring formula**

```text
final_score = (concern_score × 0.55)
            + (cosine_score × 0.25)
            + (context_score × 0.20)
```

### Layer 1 — Concern ML Score (55%)

* ใช้ `OneVsRestClassifier` ร่วมกับ `LogisticRegression` สำหรับจำแนก active ingredients
* รองรับส่วนผสมมากกว่า 200 ชนิด และจัดกลุ่มเป็น 9 หมวดหมู่
* หมวดหมู่ ได้แก่ `acne`, `whitening`, `wrinkle`, `hydration`, `barrierrepair`, `soothing`, `oilcontrol`, `exfoliation` และ `antioxidant`
* จับคู่ user concerns กับหมวดหมู่ส่วนผสมโดยใช้น้ำหนักที่กำหนด

### Layer 2 — TF-IDF Cosine Similarity (25%)

* Vectorize ข้อมูล `skintype`, `function_tags`, `brand` และ `ingredients`
* ใช้ `char_wb` n-gram ขนาด 3–5
* คำนวณ cosine similarity ระหว่างข้อมูลความต้องการของผู้ใช้กับข้อมูลสินค้า

### Layer 3 — Context Boost (20%)

* ปรับคะแนนตามอายุ เพศ ระดับความชุ่มชื้น สภาพแวดล้อม ประสบการณ์ และช่วงเวลาของ routine
* ปรับคะแนนให้สอดคล้องกับบริบทของผู้ใช้ตามกฎที่กำหนดในระบบ

### Skin Type — Hard Filter

* กรองผลิตภัณฑ์ตามประเภทผิวก่อนเข้าสู่ขั้นตอน scoring

---

## 🛠️ Tech Stack

### Backend

* **Python 3.9+** — Flask, Flask-CORS
* **scikit-learn** — TF-IDF Vectorizer, Cosine Similarity, OneVsRest Classifier
* **PostgreSQL** — psycopg2, RealDictCursor
* **joblib** — model serialization

### Frontend

* **React** — Hooks, Context API, React Router
* **Chart.js** — กราฟและการแสดงผลข้อมูล
* **CSS Variables** — Dark/Light theme system

### Database Schema

| Table                | Description                          |
| -------------------- | ------------------------------------ |
| `users`              | ข้อมูลผู้ใช้งาน                      |
| `products`           | ข้อมูลผลิตภัณฑ์                      |
| `history`            | ประวัติการประเมินผิวและผลแนะนำสินค้า |
| `bookmarks`          | รายการสินค้าที่บันทึกไว้             |
| `reviews`            | รีวิวและคะแนนสินค้า                  |
| `active_ingredients` | ข้อมูลส่วนผสมและหมวดหมู่             |

รายละเอียดคอลัมน์จริงขึ้นอยู่กับ schema ที่อยู่ในโปรเจกต์

---

## 🚀 Getting Started

คู่มือนี้ใช้สำหรับติดตั้งโปรเจกต์ใหม่หลัง Clone จาก GitHub บนเครื่อง Windows โดยแยก Frontend, Backend และ PostgreSQL ออกจากกัน

### Prerequisites

ติดตั้งโปรแกรมต่อไปนี้ก่อนเริ่มต้น

* Git
* Node.js และ npm
* Python
* PostgreSQL

แนะนำให้ใช้ Python เวอร์ชันที่รองรับโดย dependencies ของโปรเจกต์ และตรวจสอบเวอร์ชัน Node.js จากข้อกำหนดของ Frontend

### 1. Clone the Repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd skincare-ai-recomender
```

> เปลี่ยน `<YOUR_GITHUB_REPOSITORY_URL>` เป็น URL ของ repository จริงบน GitHub

### 2. Backend Setup

สร้าง virtual environment ที่โฟลเดอร์หลักของโปรเจกต์

**Windows PowerShell**

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

ไฟล์ `requirements.txt` ที่โฟลเดอร์หลักใช้สำหรับติดตั้ง Python dependencies ของโปรเจกต์

หาก PowerShell ไม่อนุญาตให้เปิดใช้งาน virtual environment สามารถเรียก Python โดยตรงได้:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### 3. PostgreSQL Setup

ติดตั้งและเปิด PostgreSQL Server จากนั้นสร้างฐานข้อมูลชื่อ `skincareCollectionDB`

```sql
CREATE DATABASE "skincareCollectionDB";
```

ตรวจสอบการตั้งค่าการเชื่อมต่อใน Backend ให้ตรงกับเครื่องของคุณ:

* Host: `127.0.0.1`
* Port: `5432`
* Database: `skincareCollectionDB`
* Username: ชื่อผู้ใช้ PostgreSQL ของคุณ
* Password: รหัสผ่าน PostgreSQL ของคุณ

ค่าข้างต้นเป็นค่าตัวอย่างสำหรับการติดตั้งในเครื่อง หากโค้ด Backend ใช้ Environment Variables ให้กำหนดค่าตามชื่อที่โค้ดรองรับ

> อย่า commit รหัสผ่านหรือข้อมูลลับลง GitHub และอย่าสมมติว่าฐานข้อมูลจะถูกสร้างขึ้นเอง เว้นแต่โค้ด initialization ของโปรเจกต์จะรองรับไว้จริง

### 4. Run Backend

จากโฟลเดอร์หลัก ให้รัน:

```powershell
.\.venv\Scripts\python.exe backend\app.py
```

หาก Backend เชื่อมต่อฐานข้อมูลสำเร็จ ให้ตรวจสอบ URL และ port ที่แสดงใน Terminal

หากพบข้อผิดพลาด `ModuleNotFoundError` ให้ตรวจสอบว่าได้ติดตั้ง dependencies ใน virtual environment ที่ถูกต้องแล้ว

หากพบข้อผิดพลาด `database does not exist` ให้ตรวจสอบชื่อฐานข้อมูลและสร้างฐานข้อมูลก่อนเริ่ม Backend

### 5. Frontend Setup

เปิด Terminal อีกหน้าต่าง แล้วเข้าโฟลเดอร์ Frontend:

```powershell
cd skincare-webapp
npm ci
```

สร้างไฟล์ `.env` จากตัวอย่าง:

```powershell
Copy-Item .env.example .env
```

ตั้งค่า API URL ใน `skincare-webapp/.env`:

```env
REACT_APP_API_URL=http://127.0.0.1:5000/api
```

ค่าดังกล่าวใช้กับ Create React App และต้องตรงกับ URL ที่ Backend ให้บริการจริง

เริ่มรัน Frontend:

```powershell
npm start
```

โดยปกติ Frontend จะเปิดที่ `http://localhost:3000`

> หาก repository ยังไม่มีไฟล์ `.env.example` ให้สร้างไฟล์นี้ตามค่าตัวอย่างข้างต้นก่อนใช้คำสั่ง `Copy-Item`

### 6. API Configuration

Frontend และ Backend ต้องใช้ Base URL และ API prefix ที่ตรงกัน

| Environment       | API URL                                                     |
| ----------------- | ----------------------------------------------------------- |
| Local development | `http://127.0.0.1:5000/api`                                 |
| Production        | URL ของ Backend ที่ Deploy แล้ว พร้อม API prefix ที่ถูกต้อง |

เมื่อเปลี่ยนค่า Environment Variables ของ Create React App ต้อง Restart development server หรือ Build ใหม่เพื่อให้ค่าถูกนำไปใช้

อย่าใส่ API URL ของเครื่องตัวเองแบบ hardcode กระจายตามไฟล์หลายหน้า ให้เรียกใช้ Environment Variable กลางที่โปรเจกต์กำหนด

**หมายเหตุ:** ตัวแปร `REACT_APP_API_URL` เหมาะกับ Create React App หากโปรเจกต์เปลี่ยนไปใช้ Vite ให้ใช้ `VITE_API_URL` แทนตามระบบ build ที่เลือกใช้จริง ห้ามใช้สองรูปแบบปะปนกันโดยไม่ตั้งค่าให้ถูกต้อง

### 7. Train ML Model (Optional)

หากต้องการฝึกโมเดลใหม่ ให้ตรวจสอบไฟล์ training ที่มีอยู่ในโปรเจกต์ก่อน แล้วรันสคริปต์ที่รองรับ

ตัวอย่าง:

```powershell
.\.venv\Scripts\python.exe backend\training\train_concern_model.py
```

หากมี pre-trained model ที่ใช้งานได้อยู่แล้ว อาจไม่จำเป็นต้องฝึกโมเดลใหม่

### 8. Production Build

ตรวจสอบว่า Frontend Build ผ่านก่อน Deploy:

```powershell
cd skincare-webapp
npm run build
```

---

## 🔌 API Endpoints

รายการต่อไปนี้เป็น endpoint ที่ระบุไว้ในเอกสารของโปรเจกต์ ควรตรวจสอบกับ routes ใน Backend ก่อนใช้งานจริง

| Method   | Endpoint                     | Description                     |
| -------- | ---------------------------- | ------------------------------- |
| `POST`   | `/api/login`                 | เข้าสู่ระบบ                     |
| `POST`   | `/api/register`              | สมัครสมาชิก                     |
| `POST`   | `/api/recommend-all`         | รับผลแนะนำสินค้าและ routine     |
| `POST`   | `/api/recommend`             | แนะนำสินค้าตามจำนวนที่กำหนด     |
| `POST`   | `/api/routine`               | สร้าง skincare routine          |
| `GET`    | `/api/search?q=`             | ค้นหาสินค้า                     |
| `GET`    | `/api/user/:email`           | ดูข้อมูลและประวัติผู้ใช้        |
| `POST`   | `/api/bookmark`              | บันทึกหรือยกเลิกการบันทึกสินค้า |
| `GET`    | `/api/bookmarks/:email`      | ดึงรายการ bookmarks             |
| `POST`   | `/api/review`                | เพิ่มหรือแก้ไขรีวิว             |
| `GET`    | `/api/reviews/:product_name` | ดูรีวิวของสินค้า                |
| `GET`    | `/api/admin/users`           | ดูรายชื่อผู้ใช้สำหรับ Admin     |
| `DELETE` | `/api/admin/users/:email`    | ลบผู้ใช้สำหรับ Admin            |

---

## 📁 Project Structure

```text
skincare-ai-recomender/
├── requirements.txt
├── README.md
├── backend/
│   ├── app.py
│   ├── database/
│   ├── routes/
│   ├── services/
│   ├── feature_engineering/
│   ├── scraper/
│   ├── training/
│   └── data/
└── skincare-webapp/
    ├── package.json
    ├── package-lock.json
    ├── public/
    └── src/
        ├── App.js
        ├── pages/
        ├── components/
        └── services/
```

โครงสร้างนี้เป็นภาพรวม ควรตรวจสอบชื่อไฟล์และโฟลเดอร์จริงใน repository ก่อนอ้างอิงเป็นโครงสร้างแบบละเอียด

---

## 🧪 Troubleshooting

### Frontend แสดงหน้าจอขาว

1. เปิด Developer Tools แล้วตรวจสอบ Console
2. ตรวจสอบว่าตัวแปร API ใช้รูปแบบที่ตรงกับระบบ build
3. ตรวจสอบว่า dependencies ติดตั้งสำเร็จ
4. รัน `npm start` ใหม่หลังแก้ `.env`

### API Request Failed

1. ตรวจสอบว่า Backend กำลังทำงาน
2. ตรวจสอบ Base URL และ API prefix
3. ตรวจสอบ CORS configuration ของ Flask
4. ตรวจสอบ URL ที่แสดงใน Network tab ของเบราว์เซอร์

### Python Module Not Found

เปิดใช้งาน virtual environment และติดตั้ง dependencies ใหม่ตาม `requirements.txt`

### PostgreSQL Connection Error

ตรวจสอบว่า PostgreSQL Server ทำงานอยู่ และค่าการเชื่อมต่อถูกต้อง รวมถึงชื่อฐานข้อมูลและสิทธิ์ผู้ใช้

---

## 📸 Screenshots

> เพิ่มภาพหน้าจอของระบบในส่วนนี้

| Skin Assessment Quiz | Product Results | Compare Page   |
| -------------------- | --------------- | -------------- |
| Add screenshot       | Add screenshot  | Add screenshot |

---

## 👤 Author

**Attawat Kammas**

* GitHub: [@BabyPetch](https://github.com/BabyPetch)
* LinkedIn: [attawat-kammas](https://www.linkedin.com/in/attawat-kammas-1b8115400/)

---

## 📄 License

MIT License — feel free to use this project as a reference or learning resource.