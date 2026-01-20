import React from 'react';

const StepSkinType = ({ onSelect, currentSelection, userName }) => {
  const options = [
    { type: 'Oily', icon: '🍋', label: 'หน้ามัน' },
    { type: 'Dry', icon: '🌵', label: 'หน้าแห้ง' },
    { type: 'Combination', icon: '⚖️', label: 'ผิวผสม' },
    { type: 'Sensitive', icon: '🛡️', label: 'แพ้ง่าย' },
  ];

  return (
    <div className="step-content">
      <h2 className="step-title">สภาพผิวของคุณเป็นแบบไหน?</h2>
      <p className="step-subtitle">สวัสดีคุณ {userName || 'Guest'} เราจะช่วยเลือกสิ่งที่ดีที่สุดให้คุณ</p>
      <div className="options-grid">
        {options.map(({ type, icon, label }) => (
          <div
            key={type}
            className={`option-card ${currentSelection === type ? 'selected' : ''}`}
            onClick={() => onSelect(type)}
          >
            <div className="icon-wrapper">{icon}</div>
            <span>{label}</span>
          </div>
        ))}
      </div>
    </div>
  );
};

export default StepSkinType;