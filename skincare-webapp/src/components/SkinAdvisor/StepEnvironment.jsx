import React from 'react';
import '../SkinAdvisorCss/StepShared.css';

const OPTIONS = [
  { id: 'hot_humid',  label: 'ร้อนชื้น',    sub: 'อยู่กลางแจ้ง อากาศร้อน',  icon: '' },
  { id: 'ac_all_day', label: 'แอร์ตลอดวัน', sub: 'ทำงานออฟฟิศ อากาศแห้ง',   icon: '' },
  { id: 'mixed',      label: 'ผสมผสาน',      sub: 'เข้าออกแอร์ + ข้างนอก',   icon: '' },
  { id: 'pollution',  label: 'มลภาวะสูง',    sub: 'ฝุ่น PM2.5 จราจร',        icon: '' },
  { id: 'tropical',   label: 'ชายทะเล/ป่า',  sub: 'แดดจัด ลม เกลือ',         icon: '' },
];

const StepEnvironment = ({ value, onSelect, onBack, onNext }) => (
  <div className="step-content fadeIn">
    <h2 className="step-title">สภาพแวดล้อมที่คุณอยู่?</h2>
    <p className="step-subtitle">แวดล้อมส่งผลต่อผิวโดยตรง เลือกที่ตรงกับชีวิตประจำวันมากที่สุด</p>

    <div className="shared-grid shared-grid-5">
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

export default StepEnvironment;