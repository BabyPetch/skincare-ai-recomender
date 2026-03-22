import React from 'react';
import '../SkinAdvisorCss/StepShared.css';

const OPTIONS = [
  { id: 'beginner',     label: 'มือใหม่',            sub: 'เพิ่งเริ่มสนใจ ยังไม่มีรูทีน',   icon: '', tip: 'แนะนำสินค้าใช้ง่าย ขั้นตอนน้อย' },
  { id: 'intermediate', label: 'ใช้อยู่แล้ว',         sub: 'มีรูทีนบ้างแล้ว อยากพัฒนา',     icon: '', tip: 'แนะนำสินค้าที่ช่วย upgrade รูทีน' },
  { id: 'advanced',     label: 'สกินแคร์จริงจัง',    sub: 'รู้จักส่วนผสม ชอบลองของใหม่',   icon: '', tip: 'แนะนำ active ingredient และ layering' },
];

const StepExperience = ({ value, onSelect, onBack, onNext }) => (
  <div className="step-content fadeIn">
    <h2 className="step-title">ประสบการณ์สกินแคร์ของคุณ?</h2>
    <p className="step-subtitle">จะได้แนะนำสินค้าที่เหมาะกับระดับของคุณ</p>

    <div className="shared-grid shared-grid-3">
      {OPTIONS.map(item => (
        <button key={item.id}
          className={`shared-card shared-card-tall ${value === item.id ? 'selected' : ''}`}
          onClick={() => onSelect(item.id)}>
          <div className="shared-icon shared-icon-lg">{item.icon}</div>
          <div className="shared-label">{item.label}</div>
          <div className="shared-sub">{item.sub}</div>
          {value === item.id && (
            <div className="shared-tip">{item.tip}</div>
          )}
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

export default StepExperience;