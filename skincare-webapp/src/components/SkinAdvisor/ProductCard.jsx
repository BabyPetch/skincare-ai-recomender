import React from 'react';
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

// Register ChartJS ครั้งเดียวที่นี่
ChartJS.register(
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
  Legend
);

const ProductCard = ({ product }) => {
  // Logic กราฟ ย้ายมาซ่อนไว้ในนี้
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
    <div className="product-card-react">
      <div className="card-header">
        <div className="step-badge">Step {product.routine_step}</div>
        <div className="match-badge">{product.ai_insight}</div>
      </div>

      <div className="product-info">
        <h3 className="brand-name">{product.brand}</h3>
        <h4 className="product-name">{product.name}</h4>
      </div>

      <div className="highlights">
        {product.highlights?.map((h, i) => (
          <span key={i} className="ing-tag">🧪 {h}</span>
        ))}
      </div>

      <div className="chart-container">
        <div className="chart-wrapper">
          <Radar data={getChartData(product.benefits)} options={chartOptions} />
        </div>
      </div>

      <div className="card-footer">
        <div className="price">฿{product.price.toLocaleString()}</div>
      </div>
    </div>
  );
};

export default ProductCard;