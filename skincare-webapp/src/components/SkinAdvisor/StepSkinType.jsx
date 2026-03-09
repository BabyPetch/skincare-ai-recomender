import React from 'react';
import '../SkinAdvisorCss/StepSkinType.css';

const skinTypes = [
  { id: 'oily',        label: 'หน้ามัน',   icon: '🍋' },
  { id: 'dry',         label: 'หน้าแห้ง',  icon: '🌵' },
  { id: 'combination', label: 'ผิวผสม',    icon: '⚖️' },
  { id: 'sensitive',   label: 'แพ้ง่าย',  icon: '🛡️' },
  { id: 'normal',      label: 'ผิวธรรมดา', icon: '✨' },
];

const StepSkinType = ({ onSelect, onNext, currentSelection, userName }) => (
  <div className="step-content fadeIn">
    <h2 className="step-title">สภาพผิวของคุณเป็นแบบไหน?</h2>
    <p className="step-subtitle">สวัสดีคุณ {userName || 'Guest'} เราจะช่วยเลือกสิ่งที่ดีที่สุดให้คุณ</p>

    <div className="skin-type-grid">
      {skinTypes.map((type) => (
        <button key={type.id}
          className={`skin-type-card ${currentSelection === type.id ? 'selected' : ''}`}
          onClick={() => onSelect(type.id)}>
          <div className="icon-wrapper">{type.icon}</div>
          <div className="label-text">{type.label}</div>
        </button>
      ))}
    </div>

    <div className="button-group">
      <button className="btn-next" onClick={onNext} disabled={!currentSelection}>
        ถัดไป →
      </button>
    </div>
  </div>
);

export default StepSkinType;