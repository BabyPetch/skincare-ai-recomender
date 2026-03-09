import React from 'react';
import '../SkinAdvisorCss/StepPrice.css';

const StepPrice = ({ currentPrice, onSelect, onBack, onSubmit }) => {

  const priceRanges = [
    { label: 'ประหยัด (< 500 บาท)',        value: 'low'    },
    { label: 'ปานกลาง (500 - 1,500 บาท)',  value: 'medium' },
    { label: 'พรีเมียม (> 1,500 บาท)',      value: 'high'   },
    { label: 'ไม่จำกัดงบ',                  value: 'any'    },
  ];

  return (
    <div className="step-content fadeIn">
      <h2 className="step-title">💰 งบประมาณของคุณ?</h2>
      <p className="step-subtitle">เลือกช่วงราคาที่คุณสะดวก เพื่อให้เราแนะนำได้ตรงใจ</p>

      <div className="price-grid">
        {priceRanges.map((range) => (
          <button
            key={range.value}
            className={`price-card ${currentPrice === range.value ? 'selected' : ''}`}
            onClick={() => onSelect(range.value)}
          >
            {range.label}
          </button>
        ))}
      </div>

      <div className="button-group">
        <button className="btn-back" onClick={onBack}>ย้อนกลับ</button>
        <button
          className="btn-next"
          onClick={onSubmit}
          disabled={!currentPrice}
        >
          วิเคราะห์ผล ✨
        </button>
      </div>
    </div>
  );
};

export default StepPrice;