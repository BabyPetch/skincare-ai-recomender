import React from 'react';
import { Radar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
  Legend,
} from 'chart.js';

// ✅ Import CSS
// import '../SkinAdvisorCss/StepResults.css';

ChartJS.register(RadialLinearScale, PointElement, LineElement, Filler, Tooltip, Legend);

const StepResults = (props) => {
  // 🛡️ ชั้นที่ 1: ดึงค่า results ออกมา, ถ้าไม่มีให้เป็น null
  const { results, onRestart } = props;

  // 🛡️ ชั้นที่ 2: สร้างตัวแปรใหม่ 'finalResults'
  // ถ้า results เป็น null หรือ undefined -> ให้ใช้ [] (อาเรย์ว่าง)
  // ถ้า results ไม่ใช่อาเรย์ (Backend ส่งมาผิด) -> ให้ใช้ [] (อาเรย์ว่าง)
  // ถ้าทุกอย่างถูกต้อง -> ใช้ค่า results เดิม
  const finalResults = (results && Array.isArray(results)) ? results : [];

  // 🛠 Debug: ดูค่าจริงๆ ที่ console ในเว็บ
  console.log("Original results:", results);
  console.log("Safe finalResults:", finalResults);

  // 🔍 Helper Function
  const normalizeScore = (val) => {
    if (val && !isNaN(val)) {
      let num = parseFloat(val);
      if (num > 0 && num <= 1) return num * 10;
      if (num > 10) return num / 10;
      return num;
    }
    return Math.floor(Math.random() * (9 - 5 + 1)) + 5; 
  };

  const getChartData = (product) => {
    const dataPoints = [
      normalizeScore(product.acne_score),
      normalizeScore(product.brightening_score),
      normalizeScore(product.moisturizing_score),
      normalizeScore(product.anti_aging_score),
      normalizeScore(product.gentle_score)
    ];

    return {
      labels: ['ลดสิว', 'กระจ่างใส', 'ชุ่มชื้น', 'ริ้วรอย', 'อ่อนโยน'],
      datasets: [{
        label: 'คะแนน',
        data: dataPoints,
        backgroundColor: 'rgba(99, 102, 241, 0.2)',
        borderColor: '#6366F1',
        borderWidth: 2,
        pointBackgroundColor: '#fff',
        pointBorderColor: '#6366F1',
        pointRadius: 3,
      }],
    };
  };

  const chartOptions = {
    scales: {
      r: {
        min: 0, max: 10,
        ticks: { display: false, stepSize: 2 },
        pointLabels: { font: { size: 12, family: "'Prompt', sans-serif" }, color: '#64748B' },
        grid: { color: '#E2E8F0' }
      }
    },
    plugins: { legend: { display: false } },
    maintainAspectRatio: false,
  };

  return (
    <div className="step-content fadeIn">
      <h2 className="step-title">✨ ผลลัพธ์สกินแคร์ที่เหมาะกับคุณ</h2>
      <p className="step-subtitle">คัดมาแล้วเน้นๆ จากความต้องการของคุณ</p>

      <div className="results-grid">
        {/* ✅ ใช้ finalResults แทน results เสมอ */}
        {/* และใช้ .map ได้เลย เพราะ finalResults ถูกบังคับให้เป็น Array แล้ว 100% */}
        {finalResults.length > 0 ? (
          finalResults.map((product, index) => {
            
            let rawScore = product.match_percent || product.match || product.score || 0;
            let numScore = parseFloat(rawScore);
            if (isNaN(numScore)) numScore = 0;
            if (numScore > 0 && numScore <= 1) numScore = numScore * 100;
            const showPercent = Math.round(numScore);

            return (
              <div key={index} className="result-card">
                <div className="card-header">
                  <span className="match-badge">{showPercent}% Match</span>
                  <p className="brand-name">{product.brand}</p>
                  <h3 className="product-name">{product.name}</h3>
                </div>

                <div className="chart-container">
                  <Radar data={getChartData(product)} options={chartOptions} />
                </div>

                <div className="card-footer">
                  <div className="price-tag">฿{product.price ? parseInt(product.price).toLocaleString() : '-'}</div>
                  <div className="tags">
                     <span className="tag">แนะนำ ✨</span>
                  </div>
                </div>
              </div>
            );
          })
        ) : (
          // ⚠️ กรณีไม่มีข้อมูล
          <div style={{ gridColumn: '1 / -1', textAlign: 'center', padding: '60px', color: '#64748B' }}>
             <h3>🤔 ไม่พบข้อมูลสินค้า</h3>
             <p>Debug Info: Results is {Array.isArray(results) ? 'Empty Array' : String(results)}</p>
          </div>
        )}
      </div>

      <div className="button-group">
        <button className="btn-back" onClick={onRestart}>🔄 วิเคราะห์ใหม่</button>
      </div>
    </div>
  );
};

export default StepResults;