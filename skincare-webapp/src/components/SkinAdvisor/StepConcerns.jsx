import React from 'react';

const StepConcerns = ({ concerns, toggleConcern, onBack, onSubmit, userAge }) => {
  const options = [
    { name: 'สิว', icon: '🌋' },
    { name: 'หมองคล้ำ', icon: '☀️' },
    { name: 'ริ้วรอย', icon: '👵' },
    { name: 'แห้งกร้าน', icon: '🍂' },
  ];

  return (
    <div className="step-content">
      <h2 className="step-title">กังวลเรื่องอะไรเป็นพิเศษ?</h2>
      <p className="step-subtitle">อายุ {userAge || 25} ปี ผิวต้องการการดูแลเฉพาะจุด</p>
      <div className="options-grid">
        {options.map(({ name, icon }) => (
          <div
            key={name}
            className={`option-card ${concerns.includes(name) ? 'selected' : ''}`}
            onClick={() => toggleConcern(name)}
          >
            <div className="icon-wrapper">{icon}</div>
            <span>{name}</span>
          </div>
        ))}
      </div>
      <div className="btn-group">
        <button className="btn-back" onClick={onBack}>ย้อนกลับ</button>
        <button className="btn-next" onClick={onSubmit}>วิเคราะห์ผลลัพธ์ ✨</button>
      </div>
    </div>
  );
};

export default StepConcerns;