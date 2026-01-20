import React from 'react';
import '../SkinAdvisorCss/StepResults.css'; // ใช้ CSS ร่วมกัน หรือจะแยกก็ได้

const StepPrice = ({ currentPrice, onSelect, onBack, onSubmit }) => {
  
  const priceRanges = [
    { label: 'ประหยัด (< 500 บาท)', value: 'low' },
    { label: 'ปานกลาง (500 - 1,500 บาท)', value: 'medium' },
    { label: 'พรีเมียม (> 1,500 บาท)', value: 'high' },
    { label: 'ไม่จำกัดงบ', value: 'any' }
  ];

  return (
    <div className="step-content fadeIn">
      <h2 className="step-title">💰 งบประมาณของคุณ?</h2>
      <p className="step-subtitle">เลือกช่วงราคาที่คุณสะดวก เพื่อให้เราแนะนำได้ตรงใจ</p>

      <div className="options-grid"> {/* ใช้ class เดียวกับหน้าอื่นๆ หรือปรับ CSS ตามชอบ */}
        {priceRanges.map((range) => (
          <button
            key={range.value}
            className={`option-card ${currentPrice === range.value ? 'selected' : ''}`}
            onClick={() => onSelect(range.value)}
            style={{ 
                padding: '20px', 
                fontSize: '1.1rem', 
                textAlign: 'center',
                border: currentPrice === range.value ? '2px solid #6366F1' : '1px solid #E2E8F0',
                background: currentPrice === range.value ? '#EEF2FF' : '#fff',
                borderRadius: '12px',
                cursor: 'pointer',
                margin: '10px 0'
            }}
          >
            {range.label}
          </button>
        ))}
      </div>

      <div className="button-group" style={{ marginTop: '30px' }}>
        <button className="btn-back" onClick={onBack}>ย้อนกลับ</button>
        <button 
          className="btn-next" 
          onClick={onSubmit}
          disabled={!currentPrice} // ห้ามกดถ้ายังไม่เลือกราคา
          style={{ 
             opacity: !currentPrice ? 0.5 : 1, 
             background: '#6366F1', 
             color: '#fff', 
             padding: '12px 24px', 
             borderRadius: '8px', 
             border: 'none', 
             cursor: !currentPrice ? 'not-allowed' : 'pointer'
          }}
        >
          วิเคราะห์ผล ✨
        </button>
      </div>
    </div>
  );
};

export default StepPrice;