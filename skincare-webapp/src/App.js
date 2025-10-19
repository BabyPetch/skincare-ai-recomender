import React, { useState } from 'react';
import { ChevronRight, Check } from 'lucide-react'; // npm install lucide-react

export default function SkinCareAdvisor() {
  const [step, setStep] = useState(0);
  const [userProfile, setUserProfile] = useState({
    skinType: null,
    concerns: [],
    productType: null,
    maxPrice: null,
    brand: null
  });
  const [recommendations, setRecommendations] = useState([]);

  // ข้อมูลผลิตภัณฑ์ตัวอย่าง (ในอนาคตจะมาจาก backend)
  const mockProducts = [
    { id: 1, name: 'Cleanser Pro', brand: 'CeraVe', type: 'Cleanser', skintype: 'oily', price: 450, score: 85 },
    { id: 2, name: 'Hydra Serum', brand: 'The Ordinary', type: 'Serum', skintype: 'dry', price: 250, score: 88 },
    { id: 3, name: 'Sensitive Shield', brand: 'La Roche', type: 'Moisturizer', skintype: 'sensitive', price: 650, score: 90 },
    { id: 4, name: 'Oil Control', brand: 'Neutrogena', type: 'Moisturizer', skintype: 'oily', price: 350, score: 82 },
    { id: 5, name: 'Daily SPF50', brand: 'Sunscreen Pro', type: 'Sunscreen', skintype: 'normal', price: 550, score: 87 }
  ];

  const skinTypeOptions = [
    "มันมาก (บริเวณ T-zone และทั้งหน้า)",
    "มันปานกลาง (เฉพาะบริเวณ T-zone)",
    "แห้งตึง ไม่ค่อยมีความมัน",
    "ปกติ สบาย ไม่แห้งไม่มัน"
  ];

  const concernsOptions = [
    "สิว หัวดำ รูขุมขนกว้าง",
    "ผิวแห้ง ลอก คัน",
    "ผิวแพ้ง่าย แดง ระคายเคือง",
    "ไม่มีปัญหาเป็นพิเศษ"
  ];

  const productTypeOptions = [
    "Cleanser (ล้างหน้า)",
    "Moisturizer (ครีมบำรุง)",
    "Serum (เซรั่ม)",
    "Sunscreen (กันแดด)",
    "ทุกประเภท"
  ];

  const budgetOptions = [
    { label: "ไม่เกิน 300 บาท", value: 300 },
    { label: "300-700 บาท", value: 700 },
    { label: "700-1500 บาท", value: 1500 },
    { label: "มากกว่า 1500 บาท", value: 5000 }
  ];

  const determineSkinType = (answer) => {
    if (answer.includes("มันมาก")) return "oily";
    if (answer.includes("มันปานกลาง")) return "combination";
    if (answer.includes("แห้งตึง")) return "dry";
    return "normal";
  };

  const extractConcerns = (answer) => {
    const concerns = [];
    if (answer.includes("สิว")) concerns.push("สิว", "ควบคุมความมัน");
    if (answer.includes("แห้ง")) concerns.push("ผิวแห้ง");
    if (answer.includes("แพ้ง่าย")) concerns.push("ผิวแพ้ง่าย");
    if (concerns.length === 0) concerns.push("ดูแลทั่วไป");
    return concerns;
  };

  const handleStep1 = (answer) => {
    const skinType = determineSkinType(answer);
    setUserProfile(prev => ({
      ...prev,
      skinType,
      concerns: extractConcerns(answer)
    }));
    setStep(2);
  };

  const handleStep2 = (answer) => {
    setUserProfile(prev => ({
      ...prev,
      productType: answer
    }));
    setStep(3);
  };

  const handleStep3 = (budget) => {
    setUserProfile(prev => ({
      ...prev,
      maxPrice: budget
    }));
    setStep(4);
  };

  const handleRecommend = () => {
    let filtered = mockProducts;

    if (userProfile.skinType) {
      filtered = filtered.filter(p => p.skintype === userProfile.skinType);
    }

    if (userProfile.productType && !userProfile.productType.includes("ทุกประเภท")) {
      const productKeyword = userProfile.productType.split(' ')[0];
      filtered = filtered.filter(p => p.type.toLowerCase().includes(productKeyword.toLowerCase()));
    }

    if (userProfile.maxPrice) {
      filtered = filtered.filter(p => p.price <= userProfile.maxPrice);
    }

    filtered.sort((a, b) => b.score - a.score);
    setRecommendations(filtered);
    setStep(5);
  };

  const translateSkinType = (type) => {
    const map = {
      oily: 'ผิวมัน',
      dry: 'ผิวแห้ง',
      combination: 'ผิวผสม',
      normal: 'ผิวปกติ',
      sensitive: 'ผิวแพ้ง่าย'
    };
    return map[type] || type;
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-pink-50 to-purple-50">
      <div className="max-w-2xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-800 mb-2">✨ Skin Care AI Advisor</h1>
          <p className="text-gray-600">ระบบแนะนำผลิตภัณฑ์ดูแลผิวอัจฉริยะ</p>
        </div>

        {/* Progress */}
        <div className="mb-8">
          <div className="flex justify-between mb-2">
            <span className="text-sm font-semibold text-gray-700">ความคืบหน้า</span>
            <span className="text-sm text-gray-600">{Math.min(step, 5)}/5</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-gradient-to-r from-pink-500 to-purple-500 h-2 rounded-full transition-all"
              style={{ width: `${(Math.min(step, 5) / 5) * 100}%` }}
            ></div>
          </div>
        </div>

        {/* Content */}
        <div className="bg-white rounded-2xl shadow-lg p-8">
          {step === 0 && (
            <div className="text-center space-y-6">
              <h2 className="text-2xl font-bold text-gray-800">ยินดีต้อนรับ! 👋</h2>
              <p className="text-gray-600 text-lg">
                ระบบจะวิเคราะห์ผิวของคุณและแนะนำผลิตภัณฑ์ที่เหมาะสมที่สุด
              </p>
              <button
                onClick={() => setStep(1)}
                className="bg-gradient-to-r from-pink-500 to-purple-500 text-white px-8 py-3 rounded-lg font-semibold hover:shadow-lg transition-all flex items-center justify-center gap-2 mx-auto"
              >
                เริ่มต้น <ChevronRight size={20} />
              </button>
            </div>
          )}

          {step === 1 && (
            <div className="space-y-4">
              <h2 className="text-2xl font-bold text-gray-800 mb-6">ขั้นตอนที่ 1: วิเคราะห์ประเภทผิว</h2>
              <p className="text-gray-600 mb-4">หลังล้างหน้า 2-3 ชั่วโมง ผิวหน้าของคุณรู้สึกอย่างไร?</p>
              <div className="space-y-3">
                {skinTypeOptions.map((option, idx) => (
                  <button
                    key={idx}
                    onClick={() => handleStep1(option)}
                    className="w-full p-4 text-left border-2 border-gray-200 rounded-lg hover:border-pink-500 hover:bg-pink-50 transition-all"
                  >
                    {option}
                  </button>
                ))}
              </div>
            </div>
          )}

          {step === 2 && (
            <div className="space-y-4">
              <h2 className="text-2xl font-bold text-gray-800 mb-6">ขั้นตอนที่ 2: คุณมีปัญหาผิวอะไรบ้าง?</h2>
              <div className="space-y-3">
                {concernsOptions.map((option, idx) => (
                  <button
                    key={idx}
                    onClick={() => {
                      setUserProfile(prev => ({
                        ...prev,
                        concerns: extractConcerns(option)
                      }));
                      setStep(3);
                    }}
                    className="w-full p-4 text-left border-2 border-gray-200 rounded-lg hover:border-pink-500 hover:bg-pink-50 transition-all"
                  >
                    {option}
                  </button>
                ))}
              </div>
            </div>
          )}

          {step === 3 && (
            <div className="space-y-4">
              <h2 className="text-2xl font-bold text-gray-800 mb-6">คุณกำลังหาผลิตภัณฑ์ประเภทไหน?</h2>
              <div className="space-y-3">
                {productTypeOptions.map((option, idx) => (
                  <button
                    key={idx}
                    onClick={() => handleStep2(option)}
                    className="w-full p-4 text-left border-2 border-gray-200 rounded-lg hover:border-pink-500 hover:bg-pink-50 transition-all"
                  >
                    {option}
                  </button>
                ))}
              </div>
            </div>
          )}

          {step === 4 && (
            <div className="space-y-4">
              <h2 className="text-2xl font-bold text-gray-800 mb-6">งบประมาณของคุณ?</h2>
              <div className="space-y-3">
                {budgetOptions.map((option, idx) => (
                  <button
                    key={idx}
                    onClick={() => handleStep3(option.value)}
                    className="w-full p-4 text-left border-2 border-gray-200 rounded-lg hover:border-pink-500 hover:bg-pink-50 transition-all"
                  >
                    {option.label}
                  </button>
                ))}
              </div>

              {/* Summary */}
              <div className="mt-8 p-4 bg-gray-50 rounded-lg space-y-2">
                <h3 className="font-semibold text-gray-800">📋 สรุปข้อมูลของคุณ:</h3>
                <p className="text-sm text-gray-600">🧴 ผิว: {translateSkinType(userProfile.skinType)}</p>
                <p className="text-sm text-gray-600">⚠️ ปัญหา: {userProfile.concerns.join(', ')}</p>
                <p className="text-sm text-gray-600">📦 ประเภท: {userProfile.productType}</p>
              </div>

              <button
                onClick={handleRecommend}
                className="w-full bg-gradient-to-r from-pink-500 to-purple-500 text-white py-3 rounded-lg font-semibold hover:shadow-lg transition-all mt-6"
              >
                รับคำแนะนำ ✨
              </button>
            </div>
          )}

          {step === 5 && (
            <div className="space-y-4">
              <h2 className="text-2xl font-bold text-gray-800 mb-6">🏆 ผลิตภัณฑ์ที่แนะนำ</h2>
              {recommendations.length === 0 ? (
                <p className="text-gray-600 text-center py-8">ไม่พบผลิตภัณฑ์ที่ตรงกับเงื่อนไข</p>
              ) : (
                <div className="space-y-4">
                  {recommendations.map((product, idx) => (
                    <div
                      key={product.id}
                      className="p-4 border-2 border-pink-200 rounded-lg bg-gradient-to-r from-pink-50 to-purple-50"
                    >
                      <div className="flex items-start gap-3">
                        <span className="text-2xl">
                          {idx === 0 ? '🥇' : idx === 1 ? '🥈' : idx === 2 ? '🥉' : '🔸'}
                        </span>
                        <div className="flex-1">
                          <h3 className="font-bold text-gray-800">{product.name}</h3>
                          <p className="text-sm text-gray-600">💼 {product.brand}</p>
                          <p className="text-sm text-gray-600">🧴 {product.type}</p>
                          <p className="text-sm text-gray-600">💰 {product.price} บาท</p>
                          <div className="flex items-center gap-2 mt-2">
                            <span className="text-sm font-semibold text-purple-600">⭐ {product.score}/100</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}

              <button
                onClick={() => {
                  setStep(0);
                  setUserProfile({
                    skinType: null,
                    concerns: [],
                    productType: null,
                    maxPrice: null,
                    brand: null
                  });
                  setRecommendations([]);
                }}
                className="w-full bg-gray-300 text-gray-800 py-3 rounded-lg font-semibold hover:bg-gray-400 transition-all mt-6"
              >
                ทำการประเมินใหม่
              </button>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="text-center mt-8 text-gray-600 text-sm">
          <p>✨ ระบบแนะนำผลิตภัณฑ์ดูแลผิวอัจฉริยะ</p>
        </div>
      </div>
    </div>
  );
}