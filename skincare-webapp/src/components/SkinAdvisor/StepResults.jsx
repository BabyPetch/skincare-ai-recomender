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

ChartJS.register(RadialLinearScale, PointElement, LineElement, Filler, Tooltip, Legend);

// แปลง function_tags string → radar chart data
const getChartData = (functionTags) => {
  const tags = typeof functionTags === 'string' 
    ? functionTags.split(',').map(t => t.trim()) 
    : [];

  const CHART_KEYS = [
    { label: 'ลดสิว',      tag: 'acne_control'   },
    { label: 'กระจ่างใส',  tag: 'brightening'    },
    { label: 'ชุ่มชื้น',   tag: 'hydrating'      },
    { label: 'ลดริ้วรอย',  tag: 'anti_aging'     },
    { label: 'อ่อนโยน',    tag: 'calming'        },
  ];

  return {
    labels: CHART_KEYS.map(k => k.label),
    datasets: [{
      label: 'คะแนน',
      data: CHART_KEYS.map(k => tags.includes(k.tag) ? 8 : 3),
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
      ticks: { display: false },
      pointLabels: { font: { size: 12, family: "'Prompt', sans-serif" }, color: '#64748B' },
      grid: { color: '#E2E8F0' }
    }
  },
  plugins: { legend: { display: false } },
  maintainAspectRatio: false,
};

// normalize final_score → % (0.0–1.0 → 0–100, เทียบกับ max ใน list)
const calcMatchPercent = (score, maxScore) => {
  if (!score || !maxScore || maxScore === 0) return 0;
  return Math.round((score / maxScore) * 100);
};

const getCategoryLabel = (category) => {
  const map = {
    moisturizer: '🔒 มอยส์เจอไรเซอร์',
    serum:       '✨ เซรั่ม',
    sunscreen:   '☀️ กันแดด',
    toner:       '💦 โทนเนอร์',
    cleanser:    '🧼 คลีนเซอร์',
    mask:        '🎭 มาส์ก',
    exfoliator:  '🌀 เอ็กซ์โฟเลียเตอร์',
    eye_care:    '👁️ ครีมตา',
  };
  return map[category] || category || '✨ บำรุงผิว';
};

const StepResults = ({ results, onRestart }) => {
  const finalResults = (results && Array.isArray(results)) ? results : [];

  // หา max score เพื่อ normalize
  const maxScore = finalResults.length > 0 
  ? Math.max(...finalResults.map(p => parseFloat(p.final_score) || 0))
  : 1;
  console.log("maxScore:", maxScore);
  console.log("scores:", finalResults.map(p => p.final_score));

  return (
    <div className="step-content fadeIn">
      <h2 className="step-title">✨ ผลลัพธ์สกินแคร์ที่เหมาะกับคุณ</h2>
      <p className="step-subtitle">คัดมาแล้วเน้นๆ จากความต้องการของคุณ</p>

      <div className="results-grid">
        {finalResults.length > 0 ? (
          finalResults.map((product, index) => {
            const matchPercent = calcMatchPercent(
              parseFloat(product.final_score), 
              maxScore
            );

            return (
              <div key={index} className="result-card">
                <div className="card-header">
                  <span className="match-badge">{matchPercent}% Match</span>
                  <p className="brand-name">{product.brand || '-'}</p>
                  <h3 className="product-name">{product.name}</h3>
                </div>

                {/* รูปสินค้า (ถ้ามี) */}
                {product.image_url && (
                  <div style={{ textAlign: 'center', margin: '10px 0' }}>
                    <img 
                      src={product.image_url} 
                      alt={product.name}
                      style={{ width: '80px', height: '80px', objectFit: 'contain', borderRadius: '8px' }}
                      onError={e => e.target.style.display = 'none'}
                    />
                  </div>
                )}

                <div className="chart-container">
                  <Radar data={getChartData(product.function_tags)} options={chartOptions} />
                </div>

                <div className="card-footer">
                  <div className="price-tag">{getCategoryLabel(product.major_category)}</div>
                  <div className="tags">
                    <span className="tag">{product.skintype || 'all'}</span>
                  </div>
                </div>
              </div>
            );
          })
        ) : (
          <div style={{ gridColumn: '1 / -1', textAlign: 'center', padding: '60px', color: '#64748B' }}>
            <h3>🤔 ไม่พบสินค้าที่ตรงกัน</h3>
            <p>ลองเลือกสภาพผิวหรือปัญหาผิวใหม่อีกครั้ง</p>
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
