import React, { useState, useEffect } from 'react';
import './SkinCareAdvisor.css';
import { CONCERN_OPTIONS, SKIN_TYPE_OPTIONS, AGE_RANGES } from '../constants/options';
import { getRecommendations } from '../services/api';

const SkinCareAdvisor = ({ user }) => {
  // --- State ---
  const [skinType, setSkinType] = useState('All');
  const [concerns, setConcerns] = useState([]);
  const [age, setAge] = useState(25); // ค่า Default กลางๆ ไว้ก่อน
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // ✅ เพิ่ม State สำหรับ Popup ของ Guest
  const [showGuestPopup, setShowGuestPopup] = useState(false);

  // --- Effect ---
  useEffect(() => {
    // ถ้าเป็น Guest ให้เด้ง Popup ถามอายุทันทีที่เข้ามา
    if (user?.role === 'guest') {
      setShowGuestPopup(true);
    } else if (user?.age) {
      // ถ้าเป็น User ปกติ ดึงอายุจาก Profile มาเลย
      setAge(user.age);
    }
  }, [user]);

  // --- Handlers ---
  const toggleConcern = (concern) => {
    setConcerns(prev => 
      prev.includes(concern) ? prev.filter(c => c !== concern) : [...prev, concern]
    );
  };

  const handleGuestAgeConfirm = () => {
    // พอกดเลือกอายุเสร็จ ให้ปิด Popup
    setShowGuestPopup(false);
  };

  const handleAnalyze = async () => {
    setLoading(true);
    setError('');
    setRecommendations([]);

    try {
      const data = await getRecommendations({ skinType, concerns, age: parseInt(age) });
      if (data.success) {
        setRecommendations(data.recommendations);
      } else {
        setError('เกิดข้อผิดพลาดในการวิเคราะห์ข้อมูล');
      }
    } catch (err) {
      setError('ไม่สามารถเชื่อมต่อกับเซิร์ฟเวอร์ได้');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="advisor-container">
      
      {/* --- ✅ ส่วน Popup (Modal) สำหรับ Guest --- */}
      {showGuestPopup && (
        <div className="modal-overlay">
          <div className="modal-content">
            <h3>🎂 ยินดีต้อนรับ Guest!</h3>
            <p>กรุณาเลือกช่วงอายุของคุณ เพื่อให้ AI วิเคราะห์ได้แม่นยำขึ้น</p>
            
            <select 
              className="form-select modal-select"
              value={age < 25 ? 20 : (age < 35 ? 30 : 40)} 
              onChange={(e) => setAge(parseInt(e.target.value))}
            >
              {AGE_RANGES.map(opt => (
                <option key={opt.value} value={opt.value}>{opt.label}</option>
              ))}
            </select>

            <button className="confirm-btn" onClick={handleGuestAgeConfirm}>
              ยืนยันอายุ
            </button>
          </div>
        </div>
      )}
      {/* ----------------------------------------- */}

      <header className="advisor-header">
        <h2>🤖 AI Skincare Advisor</h2>
        <p>สวัสดีคุณ <strong>{user?.name || 'Guest'}</strong> (อายุ {age} ปี)</p>
      </header>

      <div className="form-card">
        <div className="form-row">
          <InputGroup label="สภาพผิวของคุณ">
            <select className="form-select" value={skinType} onChange={(e) => setSkinType(e.target.value)}>
              {SKIN_TYPE_OPTIONS.map(opt => (
                <option key={opt.value} value={opt.value}>{opt.label}</option>
              ))}
            </select>
          </InputGroup>

          <InputGroup label="ช่วงอายุ">
            <select 
              className="form-select" 
              value={age < 25 ? 20 : (age < 35 ? 30 : 40)} 
              onChange={(e) => setAge(parseInt(e.target.value))}
              // ถ้าเป็น Guest ให้แก้ได้ตลอด แต่ถ้า User ล็อกไว้ (หรือจะปลดก็ได้)
              disabled={user?.role !== 'guest'} 
            >
              {AGE_RANGES.map(opt => (
                <option key={opt.value} value={opt.value}>{opt.label}</option>
              ))}
            </select>
          </InputGroup>
        </div>

        <div className="concern-section">
          <label className="input-label">ปัญหาผิวที่กังวล:</label>
          <div className="concern-wrapper">
            {CONCERN_OPTIONS.map(c => (
              <button key={c} onClick={() => toggleConcern(c)} className={`concern-btn ${concerns.includes(c) ? 'active' : ''}`}>
                {concerns.includes(c) && '✓ '} {c}
              </button>
            ))}
          </div>
        </div>

        <button className="analyze-btn" onClick={handleAnalyze} disabled={loading}>
          {loading ? '⏳ กำลังประมวลผล...' : '🔍 วิเคราะห์และจัดตาราง Routine'}
        </button>
        {error && <div className="error-msg">⚠️ {error}</div>}
      </div>

      {recommendations.length > 0 && (
        <div className="results-section">
          <h3 className="results-title">✨ ผลลัพธ์: ตารางดูแลผิวสำหรับคุณ</h3>
          <div className="result-list">
            {recommendations.map((item, index) => (
              <ProductCard key={index} item={item} />
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

// Sub-Components
const InputGroup = ({ label, children }) => (
  <div className="input-group"><label className="input-label">{label}</label>{children}</div>
);

const ProductCard = ({ item }) => (
  <div className="result-card">
    <div className="step-badge"><span className="step-label">STEP</span><span className="step-number">{item.routine_step}</span></div>
    <div className="card-content">
      <div className="card-header"><h4 className="product-name">{item.name}</h4><div className="match-badge">Match: {item.score}%</div></div>
      <div className="product-meta"><span className="brand-highlight">{item.brand}</span> | {item.type}</div>
      <div className="ai-insight-box"><p className="ai-text">{item.ai_insight}</p></div>
      <div className="price-tag">฿{item.price.toLocaleString()}</div>
    </div>
  </div>
);

export default SkinCareAdvisor;