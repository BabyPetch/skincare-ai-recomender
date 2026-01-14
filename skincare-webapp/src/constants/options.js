export const SKIN_TYPE_OPTIONS = [
    "มันมาก (บริเวณ T-zone และทั้งหน้า)",
    "มันปานกลาง (เฉพาะบริเวณ T-zone)",
    "แห้งตึง ไม่ค่อยมีความมัน",
    "ปกติ สบาย ไม่แห้งไม่มัน"
];

export const CONCERNS_OPTIONS = [
    "สิว หัวดำ รูขุมขนกว้าง",
    "ผิวแห้ง ลอก คัน",
    "ผิวแพ้ง่าย แดง ระคายเคือง",
    "ไม่มีปัญหาเป็นพิเศษ"
];

export const PRODUCT_TYPE_OPTIONS = [
    "Cleanser (ล้างหน้า)",
    "Moisturizer (ครีมบำรุง)",
    "Serum (เซรั่ม)",
    "Sunscreen (กันแดด)",
    "ทุกประเภท"
];

export const BUDGET_OPTIONS = [
    { label: "ไม่เกิน 300 บาท", value: { min: 0, max: 300 } },
    { label: "300 - 700 บาท", value: { min: 300, max: 700 } },
    { label: "700 - 1500 บาท", value: { min: 700, max: 1500 } },
    { label: "มากกว่า 1500 บาท", value: { min: 1500, max: null } },
    { label: "ทุกช่วงราคา / ไม่จำกัด", value: { min: 0, max: null } }
];