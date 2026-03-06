import React, { useState } from 'react';
import './SkinCareAdvisor.css';

import StepSkinType from '../components/SkinAdvisor/StepSkinType';
import StepConcerns from '../components/SkinAdvisor/StepConcerns';
import StepLoading  from '../components/SkinAdvisor/StepLoading';
import StepResults  from '../components/SkinAdvisor/StepResults';
import StepPrice    from '../components/SkinAdvisor/StepPrice';

const API = 'http://127.0.0.1:5000/api';

const SkinCareAdvisor = ({ user }) => {
  const [step, setStep]             = useState(1);
  const [skinType, setSkinType]     = useState('');
  const [concerns, setConcerns]     = useState([]);
  const [priceRange, setPriceRange] = useState('');
  const [recommend, setRecommend]   = useState([]);
  const [routine, setRoutine]       = useState([]);

  const selectSkin = (type) => {
    setSkinType(type);
    setTimeout(() => setStep(2), 300);
  };

  const toggleConcern = (concern) => {
    setConcerns(prev =>
      prev.includes(concern) ? prev.filter(c => c !== concern) : [...prev, concern]
    );
  };

  const handleSubmit = async () => {
    setStep(4);
    const payload = {
      skin_type:   skinType,
      concerns:    concerns,
      price_range: priceRange,
      email:       user?.email || "",
    };

    try {
      const res  = await fetch(`${API}/recommend-all`, {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
        body:    JSON.stringify(payload),
      });
      const data = await res.json();
      setRecommend(Array.isArray(data.recommend) ? data.recommend : []);
      setRoutine(Array.isArray(data.routine)     ? data.routine   : []);
      setStep(5);
    } catch (error) {
      console.error('Error:', error);
      alert('เกิดข้อผิดพลาดในการเชื่อมต่อกับเซิร์ฟเวอร์');
      setStep(3);
    }
  };

  const handleRestart = () => {
    setStep(1); setConcerns([]); setPriceRange(''); setSkinType('');
    setRecommend([]); setRoutine([]);
  };

  return (
    <div id="skin-advisor-scope">
      <div className="advisor-wrapper">
        <div className="advisor-container fadeIn">
          <div className="progress-container">
            <div className="progress-bar" style={{ width: `${(step / 5) * 100}%` }}></div>
          </div>
          {step === 1 && <StepSkinType onSelect={selectSkin} currentSelection={skinType} userName={user?.name} />}
          {step === 2 && <StepConcerns concerns={concerns} toggleConcern={toggleConcern} onBack={() => setStep(1)} onNext={() => setStep(3)} />}
          {step === 3 && <StepPrice currentPrice={priceRange} onSelect={setPriceRange} onBack={() => setStep(2)} onSubmit={handleSubmit} />}
          {step === 4 && <StepLoading userAge={user?.age} />}
          {step === 5 && <StepResults recommend={recommend} routine={routine} onRestart={handleRestart} />}
        </div>
      </div>
    </div>
  );
};

export default SkinCareAdvisor;