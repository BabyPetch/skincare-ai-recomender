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