export const determineSkinType = (answer) => {
    if (answer.includes("มันมาก")) return "oily";
    if (answer.includes("มันปานกลาง")) return "combination";
    if (answer.includes("แห้งตึง")) return "dry";
    return "normal";
};

export const extractConcerns = (answer) => {
    const concerns = new Set();
    if (answer.includes("สิว")) {
        concerns.add("สิว");
        concerns.add("ควบคุมความมัน");
    }
    if (answer.includes("แห้ง")) concerns.add("ผิวแห้ง");
    if (answer.includes("แพ้ง่าย")) concerns.add("ผิวแพ้ง่าย");
    if (concerns.size === 0) concerns.add("ดูแลทั่วไป");
    return Array.from(concerns);
};

// src/utils/helpers.js

// ฟังก์ชันคำนวณอายุจากวันเกิด (รองรับทั้ง String และ Date Object)
export const calculateAge = (birthdate) => {
  if (!birthdate) return 20; // Default fallback

  const birthDateObj = new Date(birthdate);
  const today = new Date();
  
  let age = today.getFullYear() - birthDateObj.getFullYear();
  const m = today.getMonth() - birthDateObj.getMonth();
  
  // เช็คเดือนและวันที่เพื่อความแม่นยำ
  if (m < 0 || (m === 0 && today.getDate() < birthDateObj.getDate())) {
      age--;
  }
  
  return age;
};

// (ฟังก์ชันเดิมของคุณอาจจะมีอยู่แล้ว ให้ต่อท้ายไปได้เลย)