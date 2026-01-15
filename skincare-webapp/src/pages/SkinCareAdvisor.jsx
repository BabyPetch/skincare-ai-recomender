import React, { useState } from 'react';
import { SKIN_TYPE_OPTIONS, CONCERNS_OPTIONS, PRODUCT_TYPE_OPTIONS, BUDGET_OPTIONS } from '../constants/options';
import { determineSkinType, extractConcerns } from '../utils/helpers';
import { getRecommendations } from '../services/api';
import { styles } from '../styles';

// --- Components ย่อย ---
const QuestionStep = ({ title, question, options, onSelect, onBack }) => (
  <div>
    <h2>{title}</h2>
    <p>{question}</p>
    <div style={styles.options}>
      {options.map((option, idx) => (
        <button key={idx} style={styles.btnOption} onClick={() => onSelect(option)}>
          {option}
        </button>
      ))}
    </div>
    {onBack && (
      <div style={styles.navigation}>
        <button style={styles.btnBack} onClick={onBack}>ย้อนกลับ</button>
      </div>
    )}
  </div>
);

const ProductCard = ({ product, rank }) => {
  const rankIcons = { 1: '🥇', 2: '🥈', 3: '🥉' };
  return (
    <div style={styles.productCard}>
      <span style={styles.rank}>{rankIcons[rank] || ` ${rank}. `}</span>
      <div style={styles.productInfo}>
        <div style={styles.productName}>{product.name}</div>
        <div style={styles.productDetail}>💼 {product.brand}</div>
        <div style={styles.productDetail}>📦 {product.type}</div>
      </div>
      <div style={styles.productPriceContainer}>
        <div style={styles.productPrice}>{product.price.toLocaleString()} ฿</div>
        <div style={styles.productScore}>คะแนน: {product.score}</div>
      </div>
    </div>
  );
};

export default function SkinCareAdvisor() {
  const [step, setStep] = useState(0);
  const [loading, setLoading] = useState(false);
  const [userProfile, setUserProfile] = useState({
    skinType: null, concerns: [], productType: null, minPrice: null, maxPrice: null
  });
  const [recommendations, setRecommendations] = useState([]);

  const handleSelection = (updateFunc, value, nextStep) => {
    updateFunc(value);
    setStep(nextStep);
  };

  const handleBudgetAndRecommend = async (budgetObject) => {
    setLoading(true);
    const updatedProfile = { ...userProfile, minPrice: budgetObject.min, maxPrice: budgetObject.max };
    setUserProfile(updatedProfile);

    try {
      const data = await getRecommendations(updatedProfile);
      if (data.success) {
        setRecommendations(data.recommendations);
      } else {
        alert(data.message || 'ไม่พบผลิตภัณฑ์ที่ตรงกับเงื่อนไข');
      }
    } catch (error) {
      alert('ไม่สามารถเชื่อมต่อกับเซิร์ฟเวอร์ได้');
    } finally {
      setLoading(false);
      setStep(5);
    }
  };

  const reset = () => {
    setStep(0);
    setUserProfile({ skinType: null, concerns: [], productType: null, minPrice: null, maxPrice: null });
    setRecommendations([]);
  };

  const renderStepContent = () => {
    switch (step) {
      case 0:
        return (
          <div style={styles.welcome}>
            <h2>ยินดีต้อนรับ! 👋</h2>
            <p>ระบบจะวิเคราะห์ผิวของคุณและแนะนำผลิตภัณฑ์ที่เหมาะสมที่สุด</p>
            <button style={styles.btnPrimary} onClick={() => setStep(1)}>เริ่มต้น ➜</button>
          </div>
        );
      case 1:
        return (
          <QuestionStep
            title="ขั้นตอนที่ 1"
            question="ผิวหน้าของคุณรู้สึกอย่างไรหลังล้างหน้า?"
            options={SKIN_TYPE_OPTIONS}
            onSelect={(option) => handleSelection((val) => {
                const skinType = determineSkinType(val);
                setUserProfile(prev => ({...prev, skinType, concerns: extractConcerns(val)}));
            }, option, 2)}
          />
        );
      case 2:
        return (
          <QuestionStep
            title="ขั้นตอนที่ 2"
            question="ปัญหาผิวที่กังวล?"
            options={CONCERNS_OPTIONS}
            onSelect={(option) => handleSelection((val) => setUserProfile(prev => ({ ...prev, concerns: extractConcerns(val) })), option, 3)}
            onBack={() => setStep(1)}
          />
        );
      case 3:
        return (
          <QuestionStep
            title="ขั้นตอนที่ 3"
            question="เลือกประเภทสินค้า?"
            options={PRODUCT_TYPE_OPTIONS}
            onSelect={(option) => handleSelection((val) => setUserProfile(prev => ({ ...prev, productType: val })), option, 4)}
            onBack={() => setStep(2)}
          />
        );
      case 4:
        return (
          <QuestionStep
            title="ขั้นตอนที่ 4"
            question="ช่วงงบประมาณ?"
            options={BUDGET_OPTIONS.map(opt => opt.label)}
            onSelect={(label) => {
                const selectedBudget = BUDGET_OPTIONS.find(opt => opt.label === label);
                if (selectedBudget) handleBudgetAndRecommend(selectedBudget.value);
            }}
            onBack={() => setStep(3)}
          />
        );
      case 5:
        return (
          <div>
            <h2>🏆 ผลิตภัณฑ์ที่แนะนำ</h2>
            {loading ? <p>กำลังวิเคราะห์...</p> : 
             recommendations.length > 0 ? (
              <div style={styles.options}>
                {recommendations.map((p, idx) => <ProductCard key={p.id || idx} product={p} rank={idx + 1} />)}
              </div>
            ) : <p style={styles.noProducts}>ไม่พบสินค้า</p>}
            <button style={styles.btnPrimary} onClick={reset}>เริ่มต้นใหม่</button>
          </div>
        );
      default: return null;
    }
  };

  return (
    <div style={styles.container}>
        <div style={styles.header}><h1>✨ AI Skincare</h1></div>
        {step > 0 && (
            <div style={styles.progressContainer}>
                <div style={styles.progressBar}>
                    <div style={{ ...styles.progressFill, width: `${(step / 4) * 100}%` }}></div>
                </div>
            </div>
        )}
        <div style={styles.card}>{renderStepContent()}</div>
    </div>
  );
}