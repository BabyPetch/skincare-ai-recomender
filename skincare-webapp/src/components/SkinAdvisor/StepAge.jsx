import React from 'react';
import '../SkinAdvisorCss/StepShared.css';

const AGE_RANGES = [
  { id: 'teen',   label: 'วัยรุ่น',     sub: '13–19 ปี',    icon: '' },
  { id: 'young',  label: 'วัยหนุ่มสาว', sub: '20–29 ปี',    icon: '' },
  { id: 'adult',  label: 'วัยทำงาน',    sub: '30–39 ปี',    icon: '' },
  { id: 'mature', label: 'วัยกลางคน',   sub: '40–49 ปี',    icon: '' },
  { id: 'senior', label: 'วัยผู้ใหญ่',  sub: '50 ปีขึ้นไป', icon: '' },
];

const StepAge = ({ value, onSelect, onBack, onNext }) => (
  <div className="step-content fadeIn">
    <h2 className="step-title">ช่วงอายุของคุณ?</h2>
    <p className="step-subtitle">ผิวแต่ละวัยมีความต้องการที่แตกต่างกัน</p>

    <div className="shared-grid shared-grid-5">
      {AGE_RANGES.map(item => (
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

export default StepAge;