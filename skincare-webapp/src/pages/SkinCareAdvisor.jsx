import React, { useState } from 'react';
import './SkinCareAdvisor.css'; // <-- Import CSS ที่เราเพิ่งสร้าง

const SkinCareAdvisor = () => {
  // --- State ---
  const [skinType, setSkinType] = useState('All');
  const [concerns, setConcerns] = useState([]);
  const [age, setAge] = useState(20);
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const concernOptions = ["สิว", "ริ้วรอย", "หน้ามัน", "รอยดำ", "ผิวแพ้ง่าย", "รูขุมขนกว้าง", "หมองคล้ำ"];

  const toggleConcern = (c) => {
    setConcerns(prev => prev.includes(c) ? prev.filter(item => item !== c) : [...prev, c]);
  };

  const handleAnalyze = async () => {
    setLoading(true);
    setError('');
    setRecommendations([]);

    try {
      const res = await fetch('http://127.0.0.1:5000/api/recommend', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          skinType, 
          concerns,
          age: parseInt(age) 
        })
      });
      
      const data = await res.json();
      if (data.success) {
        setRecommendations(data.recommendations);
      } else {
        setError('เกิดข้อผิดพลาดในการวิเคราะห์');
      }
    } catch (err) {
      setError('เชื่อมต่อ Server ไม่ได้ (กรุณาเปิด app.py)');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="advisor-container">
      
      {/* Header */}
      <header className="advisor-header">
        <h2>🤖 AI Skincare Advisor</h2>
        <p>วิเคราะห์ผิวและจัดลำดับ Routine ด้วยระบบอัจฉริยะ</p>
      </header>

      {/* Input Form */}
      <div className="form-card">
        
        {/* Row 1: Skin Type & Age */}
        <div className="form-row">
          <div className="input-group">
            <label className="input-label">สภาพผิว:</label>
            <select 
              className="form-select"
              value={skinType} 
              onChange={(e) => setSkinType(e.target.value)}
            >
              <option value="All">ทุกสภาพผิว / ไม่แน่ใจ</option>
              <option value="Oily">ผิวมัน (Oily)</option>
              <option value="Dry">ผิวแห้ง (Dry)</option>
              <option value="Combination">ผิวผสม (Combination)</option>
              <option value="Sensitive">ผิวแพ้ง่าย (Sensitive)</option>
            </select>
          </div>

          <div className="input-group">
            <label className="input-label">ช่วงอายุ:</label>
            <select 
              className="form-select"
              value={age}
              onChange={(e) => setAge(parseInt(e.target.value))}
            >
              <option value="20">ต่ำกว่า 25 ปี (เน้นป้องกัน)</option>
              <option value="30">25 - 34 ปี (เริ่มมีริ้วรอย)</option>
              <option value="40">35 ปีขึ้นไป (ฟื้นฟูลึก)</option>
            </select>
          </div>
        </div>

        {/* Row 2: Concerns */}
        <div style={{ marginBottom: '30px' }}>
          <label className="input-label">ปัญหาที่กังวล:</label>
          <div className="concern-wrapper">
            {concernOptions.map(c => (
              <button
                key={c}
                onClick={() => toggleConcern(c)}
                // ใช้ Logic เลือก Class ถ้าถูกเลือกให้เติม class 'active'
                className={`concern-btn ${concerns.includes(c) ? 'active' : ''}`}
              >
                {concerns.includes(c) && '✓ '} {c}
              </button>
            ))}
          </div>
        </div>

        {/* Submit Button */}
        <button 
          className="analyze-btn"
          onClick={handleAnalyze} 
          disabled={loading}
        >
          {loading ? '⏳ กำลังประมวลผล...' : '🔍 วิเคราะห์และจัดตาราง'}
        </button>

        {error && <p className="error-msg">⚠️ {error}</p>}
      </div>

      {/* Results Section */}
      {recommendations.length > 0 && (
        <div className="results-section">
          <h3 className="results-title">✨ ตารางดูแลผิวสำหรับคุณ</h3>
          
          <div className="result-list">
            {recommendations.map((item, index) => (
              <div key={index} className="result-card">
                
                {/* Step Badge */}
                <div className="step-badge">
                  <span className="step-label">STEP</span>
                  <span className="step-number">{item.routine_step}</span>
                </div>

                {/* Content */}
                <div className="card-content">
                  <div className="card-header">
                    <h4 className="product-name">{item.name}</h4>
                    <div className="match-badge">Match: {item.score}%</div>
                  </div>
                  
                  <div className="product-meta">
                    <span className="brand-highlight">{item.brand}</span> | {item.type}
                  </div>
                  
                  {/* AI Insight */}
                  <div className="ai-insight-box">
                    <p className="ai-text">{item.ai_insight}</p>
                  </div>
                  
                  <div className="price-tag">
                    ฿{item.price.toLocaleString()}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

    </div>
  );
};

export default SkinCareAdvisor;