import React from 'react';
import '../SkinAdvisorCss/StepConcerns.css';

const StepConcerns = ({ concerns, toggleConcern, onBack, onNext }) => {
  
  const concernList = [
    { id: 'acne_control',   label: 'สิว',              icon: '🌋' },
    { id: 'brightening',    label: 'หมองคล้ำ/ฝ้า',     icon: '🌞' },
    { id: 'anti_aging',     label: 'ริ้วรอย',           icon: '👵' },
    { id: 'hydrating',      label: 'แห้งกร้าน',         icon: '🍂' },
    { id: 'barrier_repair', label: 'ผิวเสีย/แพ้ง่าย',   icon: '🛡️' },
    { id: 'calming',        label: 'ผิวแดง/อักเสบ',     icon: '❄️' },
    { id: 'exfoliating',    label: 'รูขุมขนกว้าง',      icon: '🕳️' },
    { id: 'antioxidant',    label: 'ริ้วรอยดำ/กระ',     icon: '🐞' },
  ];

  return (
    <div className="step-content fadeIn">
      <h2 className="step-title">กังวลเรื่องอะไรเป็นพิเศษ?</h2>
      <p className="step-subtitle">เลือกได้มากกว่า 1 ข้อ เพื่อให้เราเน้นการแก้ไขที่ตรงจุด</p>

      <div className="concerns-grid">
        {concernList.map((item) => (
          <button
            key={item.id}
            className={`concern-card ${concerns.includes(item.id) ? 'selected' : ''}`}
            onClick={() => toggleConcern(item.id)}
          >
            <div className="concern-icon">{item.icon}</div>
            <div className="concern-label">{item.label}</div>
          </button>
        ))}
      </div>

      <div className="button-group">
        <button className="btn-back" onClick={onBack}>ย้อนกลับ</button>
        <button 
          className="btn-next" 
          onClick={onNext}
          disabled={concerns.length === 0}
        >
          ไปเลือกช่วงราคา 💰
        </button>
      </div>
    </div>
  );
};

export default StepConcerns;