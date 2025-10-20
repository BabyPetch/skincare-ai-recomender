import React, { useState } from 'react';

export default function SkinCareAdvisor() {
  const [step, setStep] = useState(0);
  const [loading, setLoading] = useState(false);
  const [userProfile, setUserProfile] = useState({
    skinType: null,
    concerns: [],
    productType: null,
    minPrice: null,
    maxPrice: null
  });
  const [recommendations, setRecommendations] = useState([]);

  // --- ตัวเลือกสำหรับแต่ละขั้นตอน ---
  const skinTypeOptions = [
    "มันมาก (บริเวณ T-zone และทั้งหน้า)",
    "มันปานกลาง (เฉพาะบริเวณ T-zone)",
    "แห้งตึง ไม่ค่อยมีความมัน",
    "ปกติ สบาย ไม่แห้งไม่มัน"
  ];

  const concernsOptions = [
    "สิว หัวดำ รูขุมขนกว้าง",
    "ผิวแห้ง ลอก คัน",
    "ผิวแพ้ง่าย แดง ระคายเคือง",
    "ไม่มีปัญหาเป็นพิเศษ"
  ];

  const productTypeOptions = [
    "Cleanser (ล้างหน้า)",
    "Moisturizer (ครีมบำรุง)",
    "Serum (เซรั่ม)",
    "Sunscreen (กันแดด)",
    "ทุกประเภท"
  ];

  // *** UPDATED: ปรับปรุงตัวเลือกงบประมาณ ***
  const budgetOptions = [
    { label: "ไม่เกิน 300 บาท", value: { min: 0, max: 300 } },
    { label: "300 - 700 บาท", value: { min: 300, max: 700 } },
    { label: "700 - 1500 บาท", value: { min: 700, max: 1500 } },
    { label: "มากกว่า 1500 บาท", value: { min: 1500, max: null } },
    { label: "ทุกช่วงราคา / ไม่จำกัด", value: { min: 0, max: null } } // เพิ่มตัวเลือกใหม่
  ];

  // --- ฟังก์ชันจัดการ Logic ---
  const determineSkinType = (answer) => {
    if (answer.includes("มันมาก")) return "oily";
    if (answer.includes("มันปานกลาง")) return "combination";
    if (answer.includes("แห้งตึง")) return "dry";
    return "normal";
  };

  const extractConcerns = (answer) => {
    const concerns = new Set(); // ใช้ Set เพื่อป้องกันค่าซ้ำ
    if (answer.includes("สิว")) {
        concerns.add("สิว");
        concerns.add("ควบคุมความมัน");
    }
    if (answer.includes("แห้ง")) concerns.add("ผิวแห้ง");
    if (answer.includes("แพ้ง่าย")) concerns.add("ผิวแพ้ง่าย");
    if (concerns.size === 0) concerns.add("ดูแลทั่วไป");
    return Array.from(concerns);
  };
  
  const translateSkinType = (type) => ({
      oily: 'ผิวมัน',
      dry: 'ผิวแห้ง',
      combination: 'ผิวผสม',
      normal: 'ผิวปกติ'
  }[type] || type);


  const handleSelection = (updateFunc, value, nextStep) => {
      updateFunc(value);
      setStep(nextStep);
  };
  
  const handleBudgetAndRecommend = async (budgetObject) => {
    setLoading(true);

    // สร้างโปรไฟล์ผู้ใช้ล่าสุดเพื่อส่งไป API ทันที
    const currentProfile = {
      ...userProfile,
      minPrice: budgetObject.min,
      maxPrice: budgetObject.max,
    };
    
    // อัปเดต State ของ UI ไปด้วย
    setUserProfile(currentProfile);

    try {
      const response = await fetch('http://localhost:5000/api/recommend', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(currentProfile)
      });
      const data = await response.json();
      if (data.success) {
        setRecommendations(data.recommendations);
      } else {
        alert(data.message || 'เกิดข้อผิดพลาดในการรับคำแนะนำ');
        setRecommendations([]);
      }
    } catch (error) {
      console.error('Error fetching recommendations:', error);
      alert('ไม่สามารถเชื่อมต่อกับเซิร์ฟเวอร์ได้');
    }
    setLoading(false);
    setStep(5); // ไปยังหน้าแสดงผลลัพธ์
  };

  const reset = () => {
    setStep(0);
    setUserProfile({
      skinType: null,
      concerns: [],
      productType: null,
      minPrice: null,
      maxPrice: null
    });
    setRecommendations([]);
  };

  // --- ส่วนของการแสดงผล (Render) ---
  const renderStepContent = () => {
    switch (step) {
      case 0:
        return (
          <div style={styles.welcome}>
            <h2>ยินดีต้อนรับ! 👋</h2>
            <p>ระบบจะวิเคราะห์ผิวของคุณและแนะนำผลิตภัณฑ์ที่เหมาะสมที่สุด</p>
            <button style={styles.btnPrimary} onClick={() => setStep(1)}>
              เริ่มต้น ➜
            </button>
          </div>
        );
      case 1:
        return (
          <QuestionStep
            title="ขั้นตอนที่ 1: วิเคราะห์ประเภทผิว"
            question="หลังล้างหน้า 2-3 ชั่วโมง ผิวหน้าของคุณรู้สึกอย่างไร?"
            options={skinTypeOptions}
            onSelect={(option) => handleSelection((val) => {
                const skinType = determineSkinType(val);
                setUserProfile(prev => ({...prev, skinType, concerns: extractConcerns(val)}));
            }, option, 2)}
          />
        );
      case 2:
        return (
          <QuestionStep
            title="ขั้นตอนที่ 2: ปัญหาผิวที่กังวล"
            question="คุณมีปัญหาผิวที่กังวลเป็นพิเศษหรือไม่?"
            options={concernsOptions}
            onSelect={(option) => handleSelection((val) => setUserProfile(prev => ({ ...prev, concerns: extractConcerns(val) })), option, 3)}
            onBack={() => setStep(1)}
          />
        );
      case 3:
        return (
          <QuestionStep
            title="ขั้นตอนที่ 3: ประเภทผลิตภัณฑ์"
            question="คุณกำลังมองหาผลิตภัณฑ์ประเภทไหนเป็นพิเศษ?"
            options={productTypeOptions}
            onSelect={(option) => handleSelection((val) => setUserProfile(prev => ({ ...prev, productType: val })), option, 4)}
            onBack={() => setStep(2)}
          />
        );
      case 4:
        return (
          <QuestionStep
            title="ขั้นตอนที่ 4: งบประมาณ"
            question="เลือกช่วงงบประมาณที่คุณสนใจ"
            options={budgetOptions.map(opt => opt.label)}
            onSelect={(label) => {
                const selectedBudget = budgetOptions.find(opt => opt.label === label);
                if (selectedBudget) {
                    handleBudgetAndRecommend(selectedBudget.value);
                }
            }}
            onBack={() => setStep(3)}
          />
        );
      case 5:
        return (
          <div>
            <h2>🏆 ผลิตภัณฑ์ที่แนะนำสำหรับคุณ</h2>
            {loading ? <p>กำลังประมวลผล...</p> : 
             recommendations.length > 0 ? (
              <div style={styles.options}>
                {recommendations.map((p, idx) => <ProductCard key={p.id || idx} product={p} rank={idx + 1} />)}
              </div>
            ) : (
              <p style={styles.noProducts}>ไม่พบผลิตภัณฑ์ที่ตรงกับเงื่อนไขของคุณ</p>
            )}
            <div style={styles.navigation}>
                <button style={styles.btnBack} onClick={() => setStep(4)}>ย้อนกลับ</button>
                <button style={styles.btnPrimary} onClick={reset}>เริ่มต้นใหม่</button>
            </div>
          </div>
        );
      default:
        return null;
    }
  };

  return (
    <div style={styles.container}>
        <div style={styles.header}>
            <h1>✨ AI Skincare Assistant</h1>
            <p>ค้นหาสกินแคร์ที่ใช่สำหรับคุณโดยเฉพาะ</p>
        </div>
        
        {step > 0 && (
            <div style={styles.progressContainer}>
                <div style={styles.progressBar}>
                    <div style={{ ...styles.progressFill, width: `${(step / 4) * 100}%` }}></div>
                </div>
            </div>
        )}

        <div style={styles.card}>
            {renderStepContent()}
        </div>

        <div style={styles.footer}>
            <p>ASA Project - 2025</p>
        </div>
    </div>
  );
}

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
                <div style={styles.productDetail}>📦{product.type}</div>
            </div>
            <div style={styles.productPriceContainer}>
                <div style={styles.productPrice}>{product.price.toLocaleString()} ฿</div>
                <div style={styles.productScore}>คะแนน: {product.score.toFixed(1)}</div>
            </div>
        </div>
    );
};


// --- Styles ---
const styles = {
    container: { fontFamily: "'Sarabun', sans-serif", background: 'linear-gradient(135deg, #fdf2f8 0%, #f5f3ff 100%)', minHeight: '100vh', padding: '2rem' },
    header: { textAlign: 'center', marginBottom: '2rem', color: '#1e293b' },
    progressContainer: { maxWidth: '600px', margin: '0 auto 2rem auto' },
    progressBar: { width: '100%', height: '8px', background: '#e5e7eb', borderRadius: '4px', overflow: 'hidden' },
    progressFill: { height: '100%', background: 'linear-gradient(90deg, #db2777 0%, #9333ea 100%)', transition: 'width 0.4s ease-in-out' },
    card: { maxWidth: '600px', margin: '0 auto', background: 'white', borderRadius: '1rem', boxShadow: '0 20px 25px -5px rgba(0,0,0,0.1), 0 10px 10px -5px rgba(0,0,0,0.04)', padding: '2rem' },
    welcome: { textAlign: 'center', padding: '2rem 0' },
    options: { display: 'flex', flexDirection: 'column', gap: '0.75rem', margin: '1.5rem 0' },
    btnOption: { padding: '1rem', border: '1px solid #d1d5db', background: 'white', borderRadius: '0.75rem', cursor: 'pointer', textAlign: 'left', fontSize: '1rem', transition: 'all 0.2s ease', color: '#374151', '&:hover': { borderColor: '#9333ea', background: '#f5f3ff'} },
    btnPrimary: { flex: 1, padding: '0.75rem 1.5rem', background: 'linear-gradient(90deg, #db2777 0%, #9333ea 100%)', color: 'white', border: 'none', borderRadius: '0.75rem', fontSize: '1rem', fontWeight: '600', cursor: 'pointer', transition: 'transform 0.2s ease', '&:hover': { transform: 'scale(1.02)' } },
    btnBack: { flex: 1, padding: '0.75rem 1.5rem', background: 'transparent', color: '#6b7280', border: '1px solid #d1d5db', borderRadius: '0.75rem', fontSize: '1rem', fontWeight: '600', cursor: 'pointer', '&:hover': { background: '#f3f4f6' } },
    navigation: { display: 'flex', gap: '1rem', marginTop: '1.5rem' },
    productCard: { border: '1px solid #e5e7eb', background: '#fafafa', padding: '1rem', borderRadius: '0.75rem', display: 'flex', alignItems: 'center', gap: '1rem' },
    rank: { fontSize: '1.75rem', color: '#6b7280' },
    productInfo: { flex: 1 },
    productName: { fontWeight: '600', color: '#1f293b' },
    productDetail: { fontSize: '0.875rem', color: '#6b7280', marginTop: '0.25rem' },
    productPriceContainer: { textAlign: 'right' },
    productPrice: { fontWeight: 'bold', fontSize: '1.125rem', color: '#db2777' },
    productScore: { fontSize: '0.75rem', color: '#9333ea', marginTop: '0.25rem' },
    noProducts: { textAlign: 'center', padding: '3rem 1rem', color: '#6b7280' },
    footer: { textAlign: 'center', marginTop: '3rem', color: '#9ca3af', fontSize: '0.875rem' },
};

