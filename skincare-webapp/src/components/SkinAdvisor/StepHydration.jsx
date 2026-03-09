import React from 'react';
import '../SkinAdvisorCss/StepShared.css';

const OPTIONS = [
  { id: 'very_dry', label: 'แห้งตึงมาก',  sub: 'รู้สึกหน้าดึง ลอก',      icon: '🏜️' },
  { id: 'dry',      label: 'ค่อนข้างแห้ง', sub: 'แห้งบางส่วน ไม่สดชื่น',  icon: '🌵' },
  { id: 'normal',   label: 'โอเค',          sub: 'สมดุลดี ไม่มัน ไม่แห้ง', icon: '💚' },
  { id: 'oily',     label: 'มันเยิ้ม',      sub: 'มันทั้งหน้า ออกง่าย',    icon: '💧' },
];

const StepHydration = ({ value, onSelect, onBack, onNext }) => (
  <div className="step-content fadeIn">
    <h2 className="step-title">💧 ผิวตอนนี้รู้สึกยังไง?</h2>
    <p className="step-subtitle">ประเมินความชุ่มชื้นหน้าตอนนี้ก่อนใส่ครีมใดๆ</p>

    <div className="shared-grid shared-grid-4">
      {OPTIONS.map(item => (
        <button key={item.id}
          className={`shared-card ${value === item.id ? 'selected' : ''}`}
          onClick={() => onSelect(item.id)}>
          <div className="shared-icon">{item.icon}</div>
          <div className="shared-label">{item.label}</div>
          <div className="shared-sub">{item.sub}</div>
        </button>
      ))}
    </div>

    <div className="button-group">
      <button className="btn-back" onClick={onBack}>ย้อนกลับ</button>
      <button className="btn-next" onClick={onNext} disabled={!value}>
        ถัดไป →
      </button>
    </div>
  </div>
);

export default StepHydration;