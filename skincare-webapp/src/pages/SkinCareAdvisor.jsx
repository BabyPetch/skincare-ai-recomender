import React, { useState } from 'react';
import './SkinCareAdvisor.css';

import StepSkinType    from '../components/SkinAdvisor/StepSkinType';
import StepAge         from '../components/SkinAdvisor/StepAge';
import StepGender      from '../components/SkinAdvisor/StepGender';
import StepHydration   from '../components/SkinAdvisor/StepHydration';
import StepEnvironment from '../components/SkinAdvisor/StepEnvironment';
import StepExperience  from '../components/SkinAdvisor/StepExperience';
import StepRoutineTime from '../components/SkinAdvisor/StepRoutineTime';
import StepConcerns    from '../components/SkinAdvisor/StepConcerns';
import StepPrice       from '../components/SkinAdvisor/StepPrice';
import StepLoading     from '../components/SkinAdvisor/StepLoading';
import StepResults     from '../components/SkinAdvisor/StepResults';

const API = 'http://127.0.0.1:5000/api';

const ageToGroup = (age) => {
  if (!age || age <= 0) return '';
  if (age >= 50) return 'senior';
  if (age >= 40) return 'mature';
  if (age >= 30) return 'adult';
  if (age >= 20) return 'young';
  return 'teen';
};

const SkinCareAdvisor = ({ user }) => {
  const isGuest   = !user || user.role === 'guest';
  const hasAge    = !isGuest && user.age > 0;
  const hasGender = !isGuest && user.gender && user.gender !== 'other';

  // step จริงใน internal logic: 1→2(age)→3(gender)→4→5→6→7→8→9→10(loading)→11(results)
  // steps ที่ข้าม: age=2, gender=3
  // TOTAL_STEPS สำหรับ progress bar
  const TOTAL_STEPS = 9 - (hasAge ? 1 : 0) - (hasGender ? 1 : 0);

  const [step,        setStep]        = useState(1);
  const [skinType,    setSkinType]    = useState('');
  const [age,         setAge]         = useState(() => hasAge ? ageToGroup(user.age) : '');
  const [gender,      setGender]      = useState(() => hasGender ? user.gender : '');
  const [hydration,   setHydration]   = useState('');
  const [environment, setEnvironment] = useState('');
  const [experience,  setExperience]  = useState('');
  const [routineTime, setRoutineTime] = useState('');
  const [concerns,    setConcerns]    = useState([]);
  const [priceRange,  setPriceRange]  = useState('');
  const [recommend,   setRecommend]   = useState([]);
  const [routine,     setRoutine]     = useState([]);

  // step แรกหลัง skin type ขึ้นอยู่กับ hasAge/hasGender
  const nextAfterSkinType = () => {
    if (hasAge && hasGender) return setStep(4);  // ข้ามทั้ง age + gender
    if (hasAge)              return setStep(3);  // ข้ามแค่ age → gender
    setStep(2);                                  // ไป age ปกติ
  };

  const nextAfterAge = () => {
    if (hasGender) return setStep(4);  // ข้าม gender
    setStep(3);
  };

  const backFromGender = () => {
    if (hasAge) return setStep(1);  // ข้ามกลับไป skin type
    setStep(2);
  };

  const backFromHydration = () => {
    if (hasGender) return hasAge ? setStep(1) : setStep(2);
    setStep(3);
  };

  const toggleConcern = (concern) =>
    setConcerns(prev =>
      prev.includes(concern) ? prev.filter(c => c !== concern) : [...prev, concern]
    );

  // loading/results step ขึ้นอยู่กับจำนวน steps ที่ข้าม
  const skipped      = (hasAge ? 1 : 0) + (hasGender ? 1 : 0);
  const LOADING_STEP = 98 - skipped;
  const RESULTS_STEP = 99 - skipped;
  const PRICE_STEP   = 9;

  const handleSubmit = async () => {
    setStep(LOADING_STEP);
    const payload = {
      skin_type:   skinType,
      concerns:    concerns,
      price_range: priceRange,
      email:       user?.email || '',
      context:     { age, gender, hydration, environment, experience, routine_time: routineTime },
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
      setStep(RESULTS_STEP);
    } catch (err) {
      console.error(err);
      alert('เกิดข้อผิดพลาดในการเชื่อมต่อกับเซิร์ฟเวอร์');
      setStep(9); // กลับไปหน้า price เพื่อให้ลอง submit ใหม่
    }
  };

  const handleRestart = () => {
    setStep(1);
    setSkinType('');
    setAge(hasAge ? ageToGroup(user.age) : '');
    setGender(hasGender ? user.gender : '');
    setHydration(''); setEnvironment(''); setExperience(''); setRoutineTime('');
    setConcerns([]); setPriceRange('');
    setRecommend([]); setRoutine([]);
  };

  // progress display
  const skippedSoFar = (hasAge && step >= 3 ? 1 : 0) + (hasGender && step >= 4 ? 1 : 0);
  const displayStep  = step - skippedSoFar;
  const progressPct  = Math.min((displayStep / TOTAL_STEPS) * 100, 100);
  const showProgress = step <= PRICE_STEP;

  return (
    <div id="skin-advisor-scope">
      <div className="advisor-wrapper">
        <div className="advisor-container">

          {showProgress && (
            <>
              <div className="progress-container">
                <div className="progress-bar" style={{ width: `${progressPct}%` }} />
              </div>
              <div className="progress-label">{displayStep} / {TOTAL_STEPS}</div>
            </>
          )}

          {step === 1 && (
            <StepSkinType
              currentSelection={skinType}
              onSelect={setSkinType}
              userName={user?.name}
              onNext={nextAfterSkinType}
            />
          )}

          {step === 2 && !hasAge && (
            <StepAge
              value={age}
              onSelect={setAge}
              onBack={() => setStep(1)}
              onNext={nextAfterAge}
            />
          )}

          {step === 3 && !hasGender && (
            <StepGender
              value={gender}
              onSelect={setGender}
              onBack={backFromGender}
              onNext={() => setStep(4)}
            />
          )}

          {step === 4 && (
            <StepHydration
              value={hydration}
              onSelect={setHydration}
              onBack={backFromHydration}
              onNext={() => setStep(5)}
            />
          )}

          {step === 5 && (
            <StepEnvironment
              value={environment}
              onSelect={setEnvironment}
              onBack={() => setStep(4)}
              onNext={() => setStep(6)}
            />
          )}

          {step === 6 && (
            <StepExperience
              value={experience}
              onSelect={setExperience}
              onBack={() => setStep(5)}
              onNext={() => setStep(7)}
            />
          )}

          {step === 7 && (
            <StepRoutineTime
              value={routineTime}
              onSelect={setRoutineTime}
              onBack={() => setStep(6)}
              onNext={() => setStep(8)}
            />
          )}

          {step === 8 && (
            <StepConcerns
              concerns={concerns}
              toggleConcern={toggleConcern}
              onBack={() => setStep(7)}
              onNext={() => setStep(9)}
            />
          )}

          {step === PRICE_STEP && (
            <StepPrice
              currentPrice={priceRange}
              onSelect={setPriceRange}
              onBack={() => setStep(8)}
              onSubmit={handleSubmit}
            />
          )}

          {step === LOADING_STEP && <StepLoading userAge={user?.age} />}

          {step === RESULTS_STEP && (
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