import React from 'react';
import '../SkinAdvisorCss/StepSkinType.css'; // ✅ เพิ่มบรรทัดนี้

const StepSkinType = ({ onSelect, currentSelection, userName }) => {
  const skinTypes = [
    { id: 'oily', label: 'หน้ามัน', icon: '🍋' },
    { id: 'dry', label: 'หน้าแห้ง', icon: '🌵' },
    { id: 'combination', label: 'ผิวผสม', icon: '⚖️' },
    { id: 'sensitive', label: 'แพ้ง่าย', icon: '🛡️' },
    { id: 'normal', label: 'ผิวธรรมดา', icon: '✨' }
  ];

  return (
    <div className="step-content fadeIn">
      <h2 className="step-title">สภาพผิวของคุณเป็นแบบไหน?</h2>
      <p className="step-subtitle">สวัสดีคุณ {userName || 'Guest'} เราจะช่วยเลือกสิ่งที่ดีที่สุดให้คุณ</p>

      {/* ✅ เรียกใช้ Grid Layout */}
      <div className="skin-type-grid">
        {skinTypes.map((type) => (
          <button
            key={type.id}
            // ✅ ใส่ Class ให้ตรงกับ CSS: skin-type-card และเช็คว่าถูกเลือกไหม
            className={`skin-type-card ${currentSelection === type.id ? 'selected' : ''}`}
            onClick={() => onSelect(type.id)}
          >
            <div className="icon-wrapper">{type.icon}</div>
            <div className="label-text">{type.label}</div>
          </button>
        ))}
      </div>
    </div>
  );
};

export default StepSkinType;