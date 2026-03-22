import React from 'react';
import '../SkinAdvisorCss/StepShared.css';

const OPTIONS = [
    {
        id: 'female',
        label: 'หญิง',
        icon: '',
        sub: 'ผิวบาง แห้งง่าย ฮอร์โมนมีผล',
    },
    {
        id: 'male',
        label: 'ชาย',
        icon: '',
        sub: 'ผิวหนา มันกว่า รูขุมขนกว้าง',
    },
    {
        id: 'other',
        label: 'ไม่ระบุ',
        icon: '',
        sub: 'ไม่นำเพศมาคำนวณ',
    },
];

const StepGender = ({ value, onSelect, onBack, onNext }) => (
    <div className="step-content fadeIn">
        <h2 className="step-title">เพศของคุณ?</h2>
        <p className="step-subtitle">เพศมีผลต่อลักษณะผิวและฮอร์โมน ช่วยให้แนะนำได้แม่นขึ้น</p>

        <div className="shared-grid shared-grid-3">
        {OPTIONS.map(item => (
            <button
            key={item.id}
            className={`shared-card shared-card-tall ${value === item.id ? 'selected' : ''}`}
            onClick={() => onSelect(item.id)}
            >
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

export default StepGender;