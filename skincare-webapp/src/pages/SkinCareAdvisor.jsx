import React, { useState } from 'react';
import './SkinCareAdvisor.css';

import StepSkinType    from '../components/SkinAdvisor/StepSkinType';
import StepAge         from '../components/SkinAdvisor/StepAge';
import StepHydration   from '../components/SkinAdvisor/StepHydration';
import StepEnvironment from '../components/SkinAdvisor/StepEnvironment';
import StepExperience  from '../components/SkinAdvisor/StepExperience';
import StepRoutineTime from '../components/SkinAdvisor/StepRoutineTime';
import StepConcerns    from '../components/SkinAdvisor/StepConcerns';
import StepPrice       from '../components/SkinAdvisor/StepPrice';
import StepLoading     from '../components/SkinAdvisor/StepLoading';
import StepResults     from '../components/SkinAdvisor/StepResults';

const API         = 'http://127.0.0.1:5000/api';
const TOTAL_STEPS = 8;

const SkinCareAdvisor = ({ user }) => {
  const [step,        setStep]        = useState(1);
  const [skinType,    setSkinType]    = useState('');
  const [age,         setAge]         = useState('');
  const [hydration,   setHydration]   = useState('');
  const [environment, setEnvironment] = useState('');
  const [experience,  setExperience]  = useState('');
  const [routineTime, setRoutineTime] = useState('');
  const [concerns,    setConcerns]    = useState([]);
  const [priceRange,  setPriceRange]  = useState('');
  const [recommend,   setRecommend]   = useState([]);
  const [routine,     setRoutine]     = useState([]);

  const toggleConcern = (concern) =>
    setConcerns(prev =>
      prev.includes(concern) ? prev.filter(c => c !== concern) : [...prev, concern]
    );

  const handleSubmit = async () => {
    setStep(9);
    const payload = {
      skin_type:   skinType,
      concerns:    concerns,
      price_range: priceRange,
      email:       user?.email || '',
      context:     { age, hydration, environment, experience, routine_time: routineTime },
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
      setStep(10);
    } catch (err) {
      console.error(err);
      alert('เกิดข้อผิดพลาดในการเชื่อมต่อกับเซิร์ฟเวอร์');
      setStep(8);
    }
  };

  const handleRestart = () => {
    setStep(1);
    setSkinType(''); setAge(''); setHydration('');
    setEnvironment(''); setExperience(''); setRoutineTime('');
    setConcerns([]); setPriceRange('');
    setRecommend([]); setRoutine([]);
  };

  const progressPct = step <= TOTAL_STEPS ? (step / TOTAL_STEPS) * 100 : 100;

  return (
    <div id="skin-advisor-scope">
      <div className="advisor-wrapper">
        <div className="advisor-container">

          {step <= TOTAL_STEPS && (
            <>
              <div className="progress-container">
                <div className="progress-bar" style={{ width: `${progressPct}%` }} />
              </div>
              <div className="progress-label">{step} / {TOTAL_STEPS}</div>
            </>
          )}

          {step === 1 && (
            <StepSkinType
              currentSelection={skinType}
              onSelect={setSkinType}
              userName={user?.name}
              onNext={() => setStep(2)}
            />
          )}

          {step === 2 && (
            <StepAge
              value={age}
              onSelect={setAge}
              onBack={() => setStep(1)}
              onNext={() => setStep(3)}
            />
          )}

          {step === 3 && (
            <StepHydration
              value={hydration}
              onSelect={setHydration}
              onBack={() => setStep(2)}
              onNext={() => setStep(4)}
            />
          )}

          {step === 4 && (
            <StepEnvironment
              value={environment}
              onSelect={setEnvironment}
              onBack={() => setStep(3)}
              onNext={() => setStep(5)}
            />
          )}

          {step === 5 && (
            <StepExperience
              value={experience}
              onSelect={setExperience}
              onBack={() => setStep(4)}
              onNext={() => setStep(6)}
            />
          )}

          {step === 6 && (
            <StepRoutineTime
              value={routineTime}
              onSelect={setRoutineTime}
              onBack={() => setStep(5)}
              onNext={() => setStep(7)}
            />
          )}

          {step === 7 && (
            <StepConcerns
              concerns={concerns}
              toggleConcern={toggleConcern}
              onBack={() => setStep(6)}
              onNext={() => setStep(8)}
            />
          )}

          {step === 8 && (
            <StepPrice
              currentPrice={priceRange}
              onSelect={setPriceRange}
              onBack={() => setStep(7)}
              onSubmit={handleSubmit}
            />
          )}

          {step === 9  && <StepLoading userAge={user?.age} />}
          {step === 10 && (
            <StepResults
              recommend={recommend}
              routine={routine}
              user={user}
              onRestart={handleRestart}
            />
          )}

        </div>
      </div>
    </div>
  );
};

export default SkinCareAdvisor;