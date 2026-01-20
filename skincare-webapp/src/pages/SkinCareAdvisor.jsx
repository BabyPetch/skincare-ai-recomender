import React, { useState } from 'react';
import './SkinCareAdvisor.css';

// Import Components เดิม
import StepSkinType from '../components/SkinAdvisor/StepSkinType';
import StepConcerns from '../components/SkinAdvisor/StepConcerns';
import StepLoading from '../components/SkinAdvisor/StepLoading';
import StepResults from '../components/SkinAdvisor/StepResults';

// ✅ 1. Import Component หน้าเลือกราคา (ต้องสร้างไฟล์นี้ด้วยนะครับ)
import StepPrice from '../components/SkinAdvisor/StepPrice'; 

const SkinCareAdvisor = ({ user }) => {
  const [step, setStep] = useState(1);
  const [skinType, setSkinType] = useState('');
  const [concerns, setConcerns] = useState([]);
  const [priceRange, setPriceRange] = useState(''); // ✅ 2. เพิ่ม State เก็บราคา
  const [results, setResults] = useState([]);

  // --- Logic Functions ---
  const selectSkin = (type) => {
    setSkinType(type);
    setTimeout(() => setStep(2), 300);
  };

  const toggleConcern = (concern) => {
    if (concerns.includes(concern)) {
      setConcerns(concerns.filter((c) => c !== concern));
    } else {
      setConcerns([...concerns, concern]);
    }
  };

  const handleSubmit = async () => {
    setStep(4); // ✅ ย้ายไปหน้า Loading (Step 4)
    const userAge = user?.age || 25;
    const userEmail = user?.email || "";

    const payload = {
      skin_type: skinType,
      concerns: concerns,
      price_range: priceRange, // ✅ 3. ส่งช่วงราคาไปให้ Backend
      age: userAge,
      email: userEmail
    };

try {
      const response = await fetch('http://127.0.0.1:5000/api/recommend', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      if (!response.ok) throw new Error('Network response was not ok');
      
      const data = await response.json();

      // 🛑 เพิ่มบรรทัดนี้เพื่อเช็คของครับ
      console.log("🔥 สิ่งที่ Backend ส่งมา:", data); 

      // ⚠️ เช็คโครงสร้างข้อมูลนิดนึง (บางที Backend ส่งมาในรูปแบบ { data: [...] })
      // ถ้า data เป็น Array ตรงๆ ให้ใช้บรรทัดเดิม
      // แต่ถ้า data อยู่ในตัวแปรย่อย (เช่น data.products) ต้องแก้เป็น setResults(data.products);
      if (Array.isArray(data)) {
          setResults(data);
      } else if (data.products && Array.isArray(data.products)) {
          setResults(data.products);
      } else if (data.data && Array.isArray(data.data)) {
          setResults(data.data);
      } else {
          console.warn("Format ข้อมูลแปลกๆ ระบบจะใช้ Array ว่างป้องกัน Error");
          setResults([]);
      }

      setStep(5); // ✅ ไปหน้าผลลัพธ์ (Step 5)
    } catch (error) {
      console.error('Error:', error);
      alert('เกิดข้อผิดพลาดในการเชื่อมต่อกับเซิร์ฟเวอร์');
      setStep(3); // ถ้า Error ให้กลับมาหน้าเลือกราคา
    }
  };

// --- Render ---
  return (
    // ✅ 1. เพิ่ม ID นี้ครอบทับทั้งหมด (เพื่อให้ CSS Scoping ทำงาน)
    <div id="skin-advisor-scope">
      
      <div className="advisor-wrapper">
        <div className="advisor-container fadeIn">
          <div className="progress-container">
            {/* ✅ ปรับ Progress bar ให้หาร 5 */}
            <div className="progress-bar" style={{width: `${(step / 5) * 100}%`}}></div>
          </div>

          {/* Step 1: เลือกสภาพผิว */}
          {step === 1 && (
            <StepSkinType 
              onSelect={selectSkin} 
              currentSelection={skinType} 
              userName={user?.name} 
            />
          )}

          {/* Step 2: เลือกปัญหาผิว */}
          {step === 2 && (
            <StepConcerns 
              concerns={concerns} 
              toggleConcern={toggleConcern} 
              onBack={() => setStep(1)} 
              // ✅ ต้องแน่ใจว่าบรรทัดนี้มีอยู่ และส่ง setStep(3)
              onNext={() => setStep(3)} 
              userAge={user?.age} 
            />
          )}

          {/* ✅ Step 3: เลือกช่วงราคา (เพิ่มใหม่) */}
          {step === 3 && (
            <StepPrice 
              currentPrice={priceRange}
              onSelect={setPriceRange}
              onBack={() => setStep(2)}
              onSubmit={handleSubmit} // ปุ่ม "วิเคราะห์ผล" อยู่หน้านี้แทน
            />
          )}

          {/* Step 4: Loading */}
          {step === 4 && <StepLoading userAge={user?.age} />}

          {/* Step 5: Results */}
          {step === 5 && (
            <StepResults 
              results={results} 
              user={user} 
              onRestart={() => {
                  setStep(1);
                  setConcerns([]);
                  setPriceRange('');
                  setSkinType('');
              }} 
            />
          )}
        </div>
      </div>

    </div> // ✅ อย่าลืมปิด div ของ skin-advisor-scope ตรงนี้ด้วยครับ
  );
};

export default SkinCareAdvisor;