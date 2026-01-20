import React from 'react';
import '../SkinAdvisorCss/StepConcerns.css'; // ✅ เพิ่มบรรทัดนี้


const StepConcerns = ({ concerns, toggleConcern, onBack, onNext }) => {
  
  const concernList = [
    { id: 'acne', label: 'สิว', icon: '🌋' },
    { id: 'brightening', label: 'หมองคล้ำ', icon: '🌞' },
    { id: 'aging', label: 'ริ้วรอย', icon: '👵' },
    { id: 'moisturizing', label: 'แห้งกร้าน', icon: '🍂' },
    { id: 'dark_spot', label: 'จุดด่างดำ', icon: '🐞' },
    { id: 'pore', label: 'รูขุมขนกว้าง', icon: '🕳️' }
  ];

  return (
    <div className="step-content fadeIn">
      <h2 className="step-title">กังวลเรื่องอะไรเป็นพิเศษ?</h2>
      <p className="step-subtitle">เลือกได้มากกว่า 1 ข้อ เพื่อให้เราเน้นการแก้ไขที่ตรงจุด</p>

      {/* ✅ เรียกใช้ Grid Layout */}
      <div className="concerns-grid">
        {concernList.map((item) => (
          <button
            key={item.id}
            // ✅ ใส่ Class: concern-card
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
        
        {/* ปุ่มไปหน้าถัดไป */}
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