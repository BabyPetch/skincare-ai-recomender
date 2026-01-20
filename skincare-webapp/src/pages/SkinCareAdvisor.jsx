import React, { useState } from 'react';
import './SkinCareAdvisor.css';

// 1. Import มาจากไฟล์ที่เราแยกไว้ (เก็บไว้)
import StepSkinType from '../components/SkinAdvisor/StepSkinType';
import StepConcerns from '../components/SkinAdvisor/StepConcerns';
import StepLoading from '../components/SkinAdvisor/StepLoading';
import StepResults from '../components/SkinAdvisor/StepResults';

const SkinCareAdvisor = ({ user }) => {
  const [step, setStep] = useState(1);
  const [skinType, setSkinType] = useState('');
  const [concerns, setConcerns] = useState([]);
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
    setStep(3);
    const userAge = user?.age || 25;
    const userEmail = user?.email || "";
    const payload = {
      skin_type: skinType,
      concerns: concerns,
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
      setResults(data);
      setStep(4);
    } catch (error) {
      console.error('Error:', error);
      alert('เกิดข้อผิดพลาดในการเชื่อมต่อกับเซิร์ฟเวอร์');
      setStep(2);
    }
  };

  // --- Render (ไม่ต้องมีการประกาศ const Step... ซ้ำในนี้แล้ว) ---
  return (
    <div className="advisor-wrapper">
      <div className="advisor-container fadeIn">
        <div className="progress-container">
          <div className="progress-bar" style={{width: `${(step / 4) * 100}%`}}></div>
        </div>

        {step === 1 && (
          <StepSkinType 
            onSelect={selectSkin} 
            currentSelection={skinType} 
            userName={user?.name} 
          />
        )}

        {step === 2 && (
          <StepConcerns 
            concerns={concerns} 
            toggleConcern={toggleConcern} 
            onBack={() => setStep(1)} 
            onSubmit={handleSubmit} 
            userAge={user?.age} 
          />
        )}

        {step === 3 && <StepLoading userAge={user?.age} />}

        {step === 4 && (
          <StepResults 
            results={results} 
            user={user} 
            onRestart={() => setStep(1)} 
          />
        )}
      </div>
    </div>
  );
};

export default SkinCareAdvisor;