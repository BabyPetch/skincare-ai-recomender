AI Skincare Assistant (ASA) - Recommendation System
โปรเจกต์นี้คือระบบแนะนำผลิตภัณฑ์ดูแลผิวเบื้องต้น (Rule-Based Recommendation System) ที่พัฒนาด้วยภาษา Python และ Pandas โดยระบบจะทำการแนะนำผลิตภัณฑ์จากชุดข้อมูลที่รวบรวมไว้ให้เหมาะสมกับสภาพผิวและปัญหาผิวของผู้ใช้งาน

📋 สิ่งที่ต้องมี (Prerequisites)
ก่อนจะเริ่มใช้งาน คุณต้องติดตั้งโปรแกรมต่อไปนี้บนเครื่องคอมพิวเตอร์ของคุณ:

Python: เวอร์ชั่น 3.7 หรือสูงกว่า

วิธีตรวจสอบ: เปิด Terminal (macOS/Linux) หรือ Command Prompt (Windows) แล้วพิมพ์ python --version

วิธีติดตั้ง: ดาวน์โหลดได้ที่ python.org

⚙️ การติดตั้ง (Setup)
Clone a Repository (ถ้ามี):
หากโปรเจกต์อยู่บน Git ให้ทำการ clone repository ลงมาที่เครื่องของคุณ

Bash

git clone [your-repository-url]
cd [repository-folder]
ติดตั้ง Library ที่จำเป็น:
โปรเจกต์นี้จำเป็นต้องใช้ library pandas ในการจัดการข้อมูล ให้ทำการติดตั้งผ่าน pip (ตัวจัดการแพ็คเกจของ Python) โดยรันคำสั่งต่อไปนี้ใน Terminal หรือ Command Prompt:

Bash

pip install pandas
เตรียมไฟล์ข้อมูล:

ดาวน์โหลดหรือเตรียมไฟล์ข้อมูลผลิตภัณฑ์ Data_Collection_ASA.xlsx - data.csv

สำคัญมาก: ต้องนำไฟล์ข้อมูลนี้มาวางไว้ในโฟลเดอร์ เดียวกัน กับไฟล์โค้ด recommender.py

โครงสร้างโฟลเดอร์ของคุณควรจะมีลักษณะดังนี้:

/your-project-folder
|-- recommender.py       <-- ไฟล์โค้ดหลัก
|-- Data_Collection_ASA.xlsx - data.csv  <-- ไฟล์ข้อมูล
|-- README.md            <-- ไฟล์อธิบายนี้
🚀 วิธีการรันโปรแกรม (How to Run)
เปิด Terminal หรือ Command Prompt ขึ้นมา

ใช้คำสั่ง cd เพื่อเข้าไปยังโฟลเดอร์ของโปรเจกต์ที่คุณเก็บไฟล์ไว้

รันสคริปต์ Python ด้วยคำสั่งต่อไปนี้:

Bash

python recommender.py
โปรแกรมจะทำการประมวลผลและแสดงผลลัพธ์ผลิตภัณฑ์ที่แนะนำสำหรับ "ผิวมัน" (oily) ออกมาทางหน้าจอ ตามที่ได้ตั้งค่าไว้เบื้องต้นในโค้ด

🔧 การปรับแต่ง (Customization)
คุณสามารถทดลองเปลี่ยนประเภทผิวที่ต้องการค้นหาได้โดยการแก้ไขค่าของตัวแปร user_input_skin_type ในไฟล์ recommender.py

ตัวอย่าง: หากต้องการค้นหาผลิตภัณฑ์สำหรับ "ผิวแห้ง" ให้แก้ไขโค้ดบรรทัดล่างๆ ดังนี้:

จาก:

Python

user_input_skin_type = 'oily'
เป็น:

Python

user_input_skin_type = 'dry'
จากนั้นบันทึกไฟล์และรันโปรแกรมอีกครั้ง
