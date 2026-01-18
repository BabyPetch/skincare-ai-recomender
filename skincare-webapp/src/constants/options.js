// src/constants/options.js

// 1. ตัวเลือกสภาพผิว (Map ภาษาไทย -> ค่าภาษาอังกฤษสำหรับคำนวณ)
export const SKIN_TYPE_OPTIONS = [
  { value: "All", label: "เลือกสภาพผิว..." }, // ค่า Default
  { value: "Oily", label: "มันมาก (บริเวณ T-zone และทั้งหน้า)" },
  { value: "Combination", label: "มันปานกลาง (เฉพาะบริเวณ T-zone)" },
  { value: "Dry", label: "แห้งตึง ไม่ค่อยมีความมัน" },
  { value: "Normal", label: "ปกติ สบาย ไม่แห้งไม่มัน" },
  { value: "Sensitive", label: "ผิวแพ้ง่าย (Sensitive)" }
];

// 2. ปัญหาผิวที่กังวล (ใช้ลิสต์ล่าสุดที่คุณให้มา)
export const CONCERN_OPTIONS = [
  "สิว", 
  "ริ้วรอย", 
  "หน้ามัน", 
  "รอยดำ", 
  "ผิวแพ้ง่าย", 
  "รูขุมขนกว้าง", 
  "หมองคล้ำ"
];

// 3. ช่วงอายุ
export const AGE_RANGES = [
  { value: 20, label: "ต่ำกว่า 25 ปี (เน้นป้องกัน)" },
  { value: 30, label: "25 - 34 ปี (เริ่มมีริ้วรอย)" },
  { value: 40, label: "35 ปีขึ้นไป (ฟื้นฟูลึก)" }
];

// 4. ประเภทสินค้า (เผื่อไว้ใช้กรองในอนาคต)
export const PRODUCT_TYPE_OPTIONS = [
  { value: "All", label: "ทุกประเภท" },
  { value: "Cleanser", label: "Cleanser (ล้างหน้า)" },
  { value: "Moisturizer", label: "Moisturizer (ครีมบำรุง)" },
  { value: "Serum", label: "Serum (เซรั่ม)" },
  { value: "Sunscreen", label: "Sunscreen (กันแดด)" }
];

// 5. งบประมาณ (เตรียมไว้เผื่อทำฟีเจอร์กรองราคา)
export const BUDGET_OPTIONS = [
  { label: "ทุกช่วงราคา / ไม่จำกัด", value: { min: 0, max: null } },
  { label: "ไม่เกิน 300 บาท", value: { min: 0, max: 300 } },
  { label: "300 - 700 บาท", value: { min: 300, max: 700 } },
  { label: "700 - 1500 บาท", value: { min: 700, max: 1500 } },
  { label: "มากกว่า 1500 บาท", value: { min: 1500, max: null } }
];