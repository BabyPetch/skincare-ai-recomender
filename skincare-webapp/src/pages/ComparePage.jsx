import React from 'react';
import { Radar } from 'react-chartjs-2';
import {
  Chart as ChartJS, RadialLinearScale, PointElement,
  LineElement, Filler, Tooltip, Legend,
} from 'chart.js';
import { useNavigate } from 'react-router-dom';
import './ComparePage.css';

ChartJS.register(RadialLinearScale, PointElement, LineElement, Filler, Tooltip, Legend);

const CHART_KEYS = [
  { label: 'ลดสิว',     tag: 'acne_control' },
  { label: 'กระจ่างใส', tag: 'brightening'  },
  { label: 'ชุ่มชื้น',  tag: 'hydrating'    },
  { label: 'ลดริ้วรอย', tag: 'anti_aging'   },
  { label: 'อ่อนโยน',   tag: 'calming'      },
];

const COLORS    = ['#6366F1', '#F59E0B', '#10B981', '#EF4444'];
const COLORS_BG = [
  'rgba(99,102,241,0.15)',
  'rgba(245,158,11,0.15)',
  'rgba(16,185,129,0.15)',
  'rgba(239,68,68,0.15)',
];

const ROWS = [
  { key: 'major_category', label: 'ประเภทสินค้า' },
  { key: 'skintype',       label: 'เหมาะกับผิว' },
  { key: 'price',          label: 'ราคา',
    format: v => v ? `฿${parseInt(v).toLocaleString()}` : '-' },
  { key: 'function_tags',  label: 'คุณสมบัติ',
    format: v => v
      ? v.split(',').slice(0, 4).map(t => t.trim()).join(' · ')
      : '-' },
];

const getChartData = (products) => ({
  labels: CHART_KEYS.map(k => k.label),
  datasets: products.map((p, i) => {
    const tags = typeof p.function_tags === 'string'
      ? p.function_tags.split(',').map(t => t.trim()) : [];
    return {
      label: p.name.length > 20 ? p.name.slice(0, 20) + '…' : p.name,
      data: CHART_KEYS.map(k => tags.includes(k.tag) ? 8 : 3),
      backgroundColor: COLORS_BG[i],
      borderColor: COLORS[i],
      borderWidth: 2,
      pointBackgroundColor: '#fff',
      pointBorderColor: COLORS[i],
      pointRadius: 3,
    };
  }),
});

const chartOptions = {
  scales: {
    r: {
      min: 0, max: 10, ticks: { display: false },
      pointLabels: {
        font: { size: 13, family: "'Prompt',sans-serif" },
        color: '#64748B',
      },
      grid: { color: 'rgba(148,163,184,0.2)' },
    },
  },
  plugins: {
    legend: {
      display: true,
      position: 'bottom',
      labels: {
        font: { size: 11 }, color: '#94A3B8',
        boxWidth: 12, padding: 16,
      },
    },
  },
  maintainAspectRatio: false,
};

const ComparePage = ({ compareList, setCompareList }) => {
  const navigate  = useNavigate();
  const products  = compareList || [];

  const removeProduct = (name) =>
    setCompareList(products.filter(p => p.name !== name));

  if (products.length === 0) {
    return (
      <div className="compare-page">
        <div className="compare-inner">
          <div className="compare-empty">
            <div className="compare-empty-icon">⚖️</div>
            <h2>ยังไม่มีสินค้าที่เลือก</h2>
            <p>กดปุ่ม <strong>เปรียบเทียบ</strong> ที่สินค้าในหน้าค้นหาได้เลยครับ</p>
            <button className="cmp-back-btn" onClick={() => navigate('/search')}>
              ← ไปหน้าค้นหา
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="compare-page">
      <div className="compare-inner">

        {/* ── Header ── */}
        <div className="compare-header">
          <div>
            <h1>เปรียบเทียบสินค้า</h1>
            <p>
              {products.length} รายการ
              {products.length < 4 &&
                <span className="cmp-hint"> — เพิ่มได้อีก {4 - products.length} รายการ</span>}
            </p>
          </div>
          <div className="compare-header-actions">
            <button className="cmp-clear-btn" onClick={() => setCompareList([])}>
              🗑 ล้างทั้งหมด
            </button>
            <button className="cmp-back-btn" onClick={() => navigate('/search')}>
              + เพิ่มสินค้า
            </button>
          </div>
        </div>

        {/* ── Product card row ── */}
        <div className="cmp-card-row">
          {products.map((p, i) => (
            <div key={i} className="cmp-product-card"
              style={{ '--accent-col': COLORS[i] }}>
              <button className="cmp-remove-btn" onClick={() => removeProduct(p.name)}>×</button>
              <div className="cmp-product-img">
                {p.image_url
                  ? <img src={p.image_url} alt={p.name}
                      onError={e => e.target.style.display = 'none'} />
                  : <span>🧴</span>}
              </div>
              <div className="cmp-product-brand">{p.brand}</div>
              <div className="cmp-product-name">{p.name}</div>
              <div className="cmp-product-price">
                ฿{p.price ? parseInt(p.price).toLocaleString() : '-'}
              </div>
            </div>
          ))}
        </div>

        {/* ── Data table ── */}
        <div className="cmp-table">
          {ROWS.map(row => (
            <div key={row.key} className="cmp-table-row">
              <div className="cmp-table-label">{row.label}</div>
              {products.map((p, i) => (
                <div key={i} className="cmp-table-cell">
                  {row.format ? row.format(p[row.key]) : (p[row.key] || '-')}
                </div>
              ))}
            </div>
          ))}
        </div>

        {/* ── Radar chart ── */}
        <div className="cmp-chart-card">
          <h3>เปรียบเทียบคุณสมบัติ</h3>
          <div className="cmp-chart-wrap">
            <Radar data={getChartData(products)} options={chartOptions} />
          </div>
        </div>

        <div style={{ textAlign: 'center', marginTop: '24px' }}>
          <button className="cmp-back-btn" onClick={() => navigate('/search')}>
            ← กลับหน้าค้นหา
          </button>
        </div>

      </div>
    </div>
  );
};

export default ComparePage;