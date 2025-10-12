<div align="center">
  <img src="https://i.imgur.com/8a5g8fB.png" alt="ASA Logo" width="150"/>
  <h1>✨ AI Skincare Assistant (ASA) ✨</h1>
  <p>
    <strong>ระบบแนะนำผลิตภัณฑ์ดูแลผิวเบื้องต้น (Rule-Based Recommendation System)</strong>
    <br />
    พัฒนาด้วย Python 🐍 และ Pandas 🐼 เพื่อแนะนำสกินแคร์ที่ใช่สำหรับคุณ
  </p>
  <p>
    <img alt="Python Version" src="https://img.shields.io/badge/Python-3.7%2B-blue?logo=python&logoColor=yellow">
    <img alt="Pandas" src="https://img.shields.io/badge/Library-Pandas-brightgreen?logo=pandas">
    <img alt="Project Status" src="https://img.shields.io/badge/Status-In%20Development-orange">
  </p>
</div>

---

## 🎯 เกี่ยวกับโปรเจกต์ (About The Project)

**AI Skincare Assistant (ASA)** คือโครงงานต้นแบบที่ถูกสร้างขึ้นเพื่อแก้ปัญหาความสับสนในการเลือกซื้อผลิตภัณฑ์ดูแลผิว โดยระบบจะทำหน้าที่เป็นผู้ช่วยส่วนตัวในการคัดกรองและแนะนำสกินแคร์จากฐานข้อมูลที่รวบรวมไว้ ให้เหมาะสมกับสภาพผิวและปัญหาผิวของผู้ใช้งานแต่ละคน

## ⭐ คุณสมบัติเด่น (Features)

* **กรองตามสภาพผิว:** แนะนำผลิตภัณฑ์ที่ออกแบบมาเพื่อสภาพผิวของคุณโดยเฉพาะ (ผิวมัน, ผิวแห้ง, ผิวผสม, ฯลฯ)
* **กรองตามปัญหาผิว:** ค้นหาผลิตภัณฑ์ที่ช่วยแก้ปัญหาที่คุณกังวลได้อย่างตรงจุด (สิว, ริ้วรอย, ความชุ่มชื้น)
* **ทำงานบนข้อมูลจริง:** ใช้ฐานข้อมูลผลิตภัณฑ์ที่มีอยู่จริงในท้องตลาด
* **โครงสร้างพื้นฐานที่ต่อยอดได้:** สามารถพัฒนาไปสู่ระบบที่ซับซ้อนขึ้น เช่น Content-Based หรือ Collaborative Filtering ในอนาคต

## 📋 สิ่งที่ต้องมี (Prerequisites)

ก่อนจะเริ่มใช้งาน ตรวจสอบให้แน่ใจว่าคุณได้ติดตั้ง **Python** เวอร์ชั่น 3.7 ขึ้นไปแล้ว

* **วิธีตรวจสอบเวอร์ชั่น Python:**
    ```sh
    python --version
    ```
* **หากยังไม่มี:** สามารถดาวน์โหลดได้ที่ 👉 [python.org](https://www.python.org/downloads/)

## ⚙️ การติดตั้ง (Installation)

1.  **Clone a Repository (ถ้ามี):**
    หากโปรเจกต์อยู่บน Git ให้ทำการ clone repository ลงมาที่เครื่อง
    ```bash
    git clone [https://your-repository-url.git](https://your-repository-url.git)
    cd your-project-folder
    ```

2.  **ติดตั้ง Library ที่จำเป็น:**
    โปรเจกต์นี้ใช้ `pandas` ในการจัดการข้อมูล ติดตั้งผ่าน `pip` ด้วยคำสั่งเดียว:
    ```bash
    pip install pandas
    ```

## 📂 โครงสร้างไฟล์ (Project Structure)

เพื่อให้โปรแกรมทำงานได้อย่างถูกต้อง คุณต้องจัดวางไฟล์ตามโครงสร้างนี้:

```
/your-project-folder
|
|-- 📄 recommender.py       # <-- ไฟล์โค้ดหลักของระบบ
|-- 📊 Data_Collection_ASA.xlsx - data.csv  # <-- ฐานข้อมูลผลิตภัณฑ์
|-- 📖 README.md            # <-- ไฟล์ที่คุณกำลังอ่านอยู่
```
> **สำคัญมาก:** ไฟล์ `recommender.py` และไฟล์ `...data.csv` ต้องอยู่ในระดับเดียวกัน

## 🚀 วิธีการรันโปรแกรม (How to Run)

1.  เปิด Terminal (หรือ Command Prompt) ขึ้นมา
2.  ใช้คำสั่ง `cd` เพื่อเข้ามายังโฟลเดอร์ของโปรเจกต์
3.  รันสคริปต์ด้วยคำสั่ง:
    ```bash
    python recommender.py
    ```
4.  โปรแกรมจะแสดงผลลัพธ์ผลิตภัณฑ์ที่แนะนำสำหรับ **"ผิวมัน" (oily)** ออกมาทางหน้าจอ

## 🔧 การปรับแต่ง (Customization)

คุณสามารถทดลองเปลี่ยนประเภทผิวที่ต้องการค้นหาได้ง่ายๆ โดยการแก้ไขตัวแปร `user_input_skin_type` ในไฟล์ `recommender.py`

**ตัวอย่าง:** หากต้องการค้นหาผลิตภัณฑ์สำหรับ "ผิวแห้ง" ให้แก้ไขโค้ด:

**จาก:**
```python
user_input_skin_type = 'oily'
```
**เป็น:**
```python
user_input_skin_type = 'dry'
```
จากนั้นบันทึกไฟล์และรันโปรแกรมอีกครั้งเพื่อดูผลลัพธ์ใหม่!
