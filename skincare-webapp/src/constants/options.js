// ข้อมูลเกณฑ์ในการเลือกสกินแคร์ (สำหรับนำไปคำนวณ)

export const SKINCARE_OPTIONS = {
  // 1. สภาพผิว (Skin Type)
  skinTypes: [
    { id: 'oily', label: 'ผิวมัน' },
    { id: 'dry', label: 'ผิวแห้ง' },
    { id: 'combination', label: 'ผิวผสม' },
    { id: 'normal', label: 'ผิวธรรมดา' },
    { id: 'sensitive', label: 'ผิวแพ้ง่าย' }
  ],

  // 2. ปัญหาผิว (Skin Problems) - เลือกได้หลายข้อ
  skinProblems: [
    { id: 'acne', label: 'สิว' },
    { id: 'wrinkles', label: 'ริ้วรอย' },
    { id: 'melasma', label: 'ฝ้า' },
    { id: 'dark_spots', label: 'จุดด่างดำ' },
    { id: 'pores', label: 'รูขุมขนกว้าง' },
    { id: 'dullness', label: 'ผิวหมองคล้ำ' },
    { id: 'dehydrated', label: 'ผิวขาดน้ำ' }
  ],

  // 3. ประเภทผลิตภัณฑ์ (Product Type)
  productTypes: [
    { id: 'cleansing', label: 'Cleansing (เช็ดเครื่องสำอาง)' },
    { id: 'cleanser', label: 'Cleanser (โฟมล้างหน้า)' },
    { id: 'essence', label: 'Essence (น้ำตบ)' },
    { id: 'serum', label: 'Serum (เซรั่ม)' },
    { id: 'moisturizer', label: 'Moisturizer (มอยส์เจอไรเซอร์)' },
    { id: 'sunscreen', label: 'Sunscreen (กันแดด)' }
  ],

  // 4. ราคา (Price Range) - ใส่ min/max ไว้เพื่อให้เขียนสูตรคำนวณง่าย
  priceRanges: [
    { id: 'p1', label: 'ไม่เกิน 500 บาท', min: 0, max: 500 },
    { id: 'p2', label: '500 - 1,000 บาท', min: 500, max: 1000 },
    { id: 'p3', label: '1,000 - 1,500 บาท', min: 1000, max: 1500 },
    { id: 'p4', label: '1,500 - 2,000 บาท', min: 1500, max: 2000 },
    { id: 'p5', label: '2,000 บาทขึ้นไป', min: 2000, max: 99999 }
  ]
};