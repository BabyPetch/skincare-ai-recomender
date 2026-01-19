import React, { useState } from 'react';
import './SkinCareAdvisor.css';
import {
  Chart as ChartJS,
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
  Legend,
} from 'chart.js';
import { Radar } from 'react-chartjs-2';

ChartJS.register(
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
  Legend
);

// ✅ รับ props 'user' เข้ามาเพื่อใช้อายุ
const SkinCareAdvisor = ({ user }) => {
  const [step, setStep] = useState(1);
  const [skinType, setSkinType] = useState('');
  // ❌ ลบ state age ออก เพราะจะใช้ user.age แทน
  const [concerns, setConcerns] = useState([]);
  const [results, setResults] = useState([]);

  // เลือกผิวเสร็จ ไป Step 2 (หน้าเลือกปัญหาผิวเลย ไม่ต้องถามอายุแล้ว)
  const selectSkin = (type) => {
    setSkinType(type);
    setTimeout(() => setStep(2), 300);
  };

  const toggleConcern = (concern) => {
    if (concerns.includes(concern)) {
      setConcerns(concerns.filter((c) => c !== concern));
    } else {
      setConcerns([...concerns, concern]);
    }
  };

  // ในไฟล์ src/pages/SkinCareAdvisor.jsx

  const handleSubmit = async () => {
    setStep(3); // ไปหน้า Loading

    // 1. เตรียมข้อมูลที่จะส่ง (Payload)
    const userAge = user?.age || 25;
    const userEmail = user?.email || ""; // ดึง email ของ user มา

    const payload = {
      skin_type: skinType,
      concerns: concerns, // ส่งเป็น array ได้เลย ["สิว", "ริ้วรอย"]
      age: userAge,
      email: userEmail    // 👈 สำคัญ! ต้องส่ง email ไปด้วยเพื่อบันทึก History
    };

    console.log("🚀 Sending Data:", payload); // เช็คใน Console browser ว่าข้อมูลถูกต้องไหม

    try {
      // 2. ส่ง Request แบบ JSON (ต้องมี Headers และ JSON.stringify)
      const response = await fetch('http://127.0.0.1:5000/api/recommend', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json', // 👈 บรรทัดนี้สำคัญมาก! แก้ Error 415
        },
        body: JSON.stringify(payload), // 👈 ต้องแปลง Object เป็น String JSON
      });

      if (!response.ok) {
        throw new Error('Network response was not ok');
      }

      const data = await response.json();
      setResults(data);
      setStep(4); // ไปหน้าแสดงผล
      
    } catch (error) {
      console.error('Error:', error);
      alert('เกิดข้อผิดพลาดในการเชื่อมต่อกับเซิร์ฟเวอร์');
      setStep(2); // กลับไปหน้าเลือกปัญหา
    }
  };
  
  const getChartData = (benefits) => {
    const safeBenefits = benefits || { acne: 0, brightening: 0, moisturizing: 0, aging: 0, gentle: 0 };
    return {
      labels: ['ลดสิว/มัน', 'กระจ่างใส', 'ชุ่มชื้น', 'ลดริ้วรอย', 'อ่อนโยน'],
      datasets: [
        {
          label: 'คะแนน',
          data: [
            safeBenefits.acne || 0,
            safeBenefits.brightening || 0,
            safeBenefits.moisturizing || 0,
            safeBenefits.aging || 0,
            safeBenefits.gentle || 0,
          ],
          backgroundColor: 'rgba(99, 102, 241, 0.2)',
          borderColor: '#6366F1',
          borderWidth: 2,
          pointBackgroundColor: '#6366F1',
          pointBorderColor: '#fff',
          pointHoverBackgroundColor: '#fff',
          pointHoverBorderColor: '#6366F1',
        },
      ],
    };
  };

  const chartOptions = {
    scales: {
      r: {
        min: 0,
        max: 10,
        ticks: { display: false, stepSize: 2 },
        grid: { color: 'rgba(0, 0, 0, 0.05)' },
        pointLabels: { font: { size: 12, family: "'Kanit', sans-serif" }, color: '#64748b' }
      }
    },
    plugins: { legend: { display: false } },
    maintainAspectRatio: false
  };

  return (
    <div className="advisor-wrapper">
      <div className="advisor-container fadeIn">
        {/* Progress Bar (ปรับเหลือ 4 ขั้นตอน) */}
        <div className="progress-container">
          <div className="progress-bar" style={{width: `${(step / 4) * 100}%`}}></div>
        </div>

        {/* Step 1: เลือกสภาพผิว */}
        {step === 1 && (
          <div className="step-content">
            <h2 className="step-title">สภาพผิวของคุณเป็นแบบไหน?</h2>
            <p className="step-subtitle">สวัสดีคุณ {user?.name || 'Guest'} เราจะช่วยเลือกสิ่งที่ดีที่สุดให้คุณ</p>
            <div className="options-grid">
              {[
                { type: 'Oily', icon: '🍋', label: 'หน้ามัน' },
                { type: 'Dry', icon: '🌵', label: 'หน้าแห้ง' },
                { type: 'Combination', icon: '⚖️', label: 'ผิวผสม' },
                { type: 'Sensitive', icon: '🛡️', label: 'แพ้ง่าย' },
              ].map(({ type, icon, label }) => (
                <div
                  key={type}
                  className={`option-card ${skinType === type ? 'selected' : ''}`}
                  onClick={() => selectSkin(type)}
                >
                  <div className="icon-wrapper">{icon}</div>
                  <span>{label}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* ❌ ตัดหน้าเลือกอายุออกไปแล้ว */}

        {/* Step 2: เลือกปัญหาผิว (ขยับขึ้นมาแทน) */}
        {step === 2 && (
          <div className="step-content">
            <h2 className="step-title">กังวลเรื่องอะไรเป็นพิเศษ?</h2>
            <p className="step-subtitle">อายุ {user?.age || 25} ปี ผิวต้องการการดูแลเฉพาะจุด</p>
            <div className="options-grid">
              {[
                { name: 'สิว', icon: '🌋' },
                { name: 'หมองคล้ำ', icon: '☀️' },
                { name: 'ริ้วรอย', icon: '👵' },
                { name: 'แห้งกร้าน', icon: '🍂' },
              ].map(({ name, icon }) => (
                <div
                  key={name}
                  className={`option-card ${concerns.includes(name) ? 'selected' : ''}`}
                  onClick={() => toggleConcern(name)}
                >
                  <div className="icon-wrapper">{icon}</div>
                  <span>{name}</span>
                </div>
              ))}
            </div>
            <div className="btn-group">
              <button className="btn-back" onClick={() => setStep(1)}>ย้อนกลับ</button>
              <button className="btn-next" onClick={handleSubmit}>วิเคราะห์ผลลัพธ์ ✨</button>
            </div>
          </div>
        )}

        {/* Step 3: Loading */}
        {step === 3 && (
          <div className="loading-screen">
            <div className="loading-spinner"></div>
            <h3>AI กำลังประมวลผล...</h3>
            <p>กำลังค้นหาสกินแคร์รูทีนที่เหมาะกับวัย {user?.age || 25} ปี ของคุณ</p>
          </div>
        )}

        {/* Step 4: Result List */}
        {step === 4 && (
          <div className="results-content">
            <div className="results-header">
              <div>
                <h2 className="step-title">✨ สกินแคร์รูทีนเพื่อคุณ</h2>
                <p className="step-subtitle">สำหรับ: {user?.name} (อายุ {user?.age} ปี)</p>
              </div>
              <button className="btn-restart" onClick={() => setStep(1)}>🔄 เริ่มใหม่</button>
            </div>
            
            <div className="product-list">
              {Array.isArray(results) && results.length > 0 ? (
                results.map((p, idx) => (
                  <div key={idx} className="product-card-react">
                    <div className="card-header">
                      <div className="step-badge">Step {p.routine_step}</div>
                      <div className="match-badge">{p.ai_insight}</div>
                    </div>

                    <div className="product-info">
                      <h3 className="brand-name">{p.brand}</h3>
                      <h4 className="product-name">{p.name}</h4>
                    </div>

                    <div className="highlights">
                      {p.highlights?.map((h, i) => (
                        <span key={i} className="ing-tag">🧪 {h}</span>
                      ))}
                    </div>

                    <div className="chart-container">
                      <div className="chart-wrapper">
                        <Radar data={getChartData(p.benefits)} options={chartOptions} />
                      </div>
                    </div>

                    <div className="card-footer">
                      <div className="price">฿{p.price.toLocaleString()}</div>
                    </div>
                  </div>
                ))
              ) : (
                <div className="empty-state">
                  <span className="empty-icon">😕</span>
                  <h3>ไม่พบข้อมูลสินค้า</h3>
                  <p>ลองปรับเปลี่ยนเงื่อนไข หรือตรวจสอบการเชื่อมต่อ</p>
                  <button className="btn-restart-large" onClick={() => setStep(1)}>เริ่มทำแบบทดสอบใหม่</button>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default SkinCareAdvisor;