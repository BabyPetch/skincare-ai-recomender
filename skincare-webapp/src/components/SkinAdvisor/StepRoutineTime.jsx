import React from 'react';
import '../SkinAdvisorCss/StepShared.css';

const OPTIONS = [
  { id: 'morning', label: 'เช้าอย่างเดียว',  sub: 'Cleanser → Toner → SPF',              icon: '' },
  { id: 'evening', label: 'เย็นอย่างเดียว',  sub: 'Double cleanse → Serum → Moisturizer', icon: '' },
  { id: 'both',    label: 'ทั้งเช้าและเย็น',  sub: 'Full AM + PM routine',                 icon: '' },
];

const StepRoutineTime = ({ value, onSelect, onBack, onNext }) => (
  <div className="step-content fadeIn">
    <h2 className="step-title">ทำ Skincare ตอนไหน?</h2>
    <p className="step-subtitle">จะได้แนะนำสินค้าที่เหมาะกับช่วงเวลาที่คุณใช้</p>

    <div className="shared-grid shared-grid-3">
      {OPTIONS.map(item => (
        <button key={item.id}
          className={`shared-card shared-card-tall ${value === item.id ? 'selected' : ''}`}
          onClick={() => onSelect(item.id)}>
          <div className="shared-icon shared-icon-lg">{item.icon}</div>
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

export default StepRoutineTime;