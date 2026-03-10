import React, { useState } from 'react';
import { Radar } from 'react-chartjs-2';
import {
  Chart as ChartJS, RadialLinearScale, PointElement,
  LineElement, Filler, Tooltip, Legend,
} from 'chart.js';
import BookmarkButton from '../Reviews/BookmarkButton';
import ReviewButton   from '../Reviews/ReviewButton';
import ProductReviews from '../Reviews/ProductReviews';
import '../SkinAdvisorCss/StepResults.css';

ChartJS.register(RadialLinearScale, PointElement, LineElement, Filler, Tooltip, Legend);

const CHART_KEYS = [
  { label: 'ลดสิว',     tag: 'acne_control' },
  { label: 'กระจ่างใส', tag: 'brightening'  },
  { label: 'ชุ่มชื้น',  tag: 'hydrating'    },
  { label: 'ลดริ้วรอย', tag: 'anti_aging'   },
  { label: 'อ่อนโยน',   tag: 'calming'      },
];

const TAG_LABELS = {
  acne_control: 'ลดสิว',      brightening:    'กระจ่างใส',
  hydrating:    'ชุ่มชื้น',   anti_aging:     'ลดริ้วรอย',
  calming:      'อ่อนโยน',    barrier_repair: 'ซ่อมแซมผิว',
  oil_control:  'คุมมัน',     lightweight:    'เบาสบาย',
  antioxidant:  'ต้านอนุมูล', sunscreen:      'กันแดด',
};

const getChartData = (functionTags) => {
  const tags = typeof functionTags === 'string'
    ? functionTags.split(',').map(t => t.trim()) : [];
  return {
    labels: CHART_KEYS.map(k => k.label),
    datasets: [{
      label: 'คะแนน',
      data: CHART_KEYS.map(k => tags.includes(k.tag) ? 8 : 3),
      backgroundColor: 'rgba(99,102,241,0.15)',
      borderColor: '#6366F1', borderWidth: 2,
      pointBackgroundColor: '#fff', pointBorderColor: '#6366F1', pointRadius: 4,
    }],
  };
};

const chartOptions = {
  scales: {
    r: {
      min: 0, max: 10, ticks: { display: false },
      pointLabels: { font: { size: 13, family: "'Prompt',sans-serif" }, color: '#64748B' },
      grid: { color: 'rgba(148,163,184,0.2)' },
    }
  },
  plugins: { legend: { display: false } },
  maintainAspectRatio: false,
};

const parseTags = (ft) =>
  ft ? ft.split(',').map(t => t.trim()).filter(Boolean).slice(0, 4) : [];

const SectionHeader = ({ icon, title, subtitle }) => (
  <div className="section-header">
    <h2 className="section-title">{icon} {title}</h2>
    <p className="section-subtitle">{subtitle}</p>
  </div>
);

const ProductCard = ({ product, matchPercent, email }) => {
  const [showReviews, setShowReviews] = useState(false);
  const tags = parseTags(product.function_tags);

  return (
    <div className="result-card">
      <div className="card-main">

        {/* ── ซ้าย ── */}
        <div className="card-left">
          <div className="card-badge-row">
            <span className="match-badge">{matchPercent}% Match</span>
          </div>

          <div className="card-img-wrap">
            {product.image_url
              ? <img src={product.image_url} alt={product.name}
                  className="card-img-thumb"
                  onError={e => e.target.style.display = 'none'} />
              : <div className="card-img-placeholder">🧴</div>
            }
          </div>

          <p className="brand-name">{product.brand || '-'}</p>
          <h3 className="product-name">{product.name}</h3>

          {tags.length > 0 && (
            <div className="card-tags">
              {tags.map((tag, i) => (
                <span key={i} className="card-tag">{TAG_LABELS[tag] || tag}</span>
              ))}
            </div>
          )}

          <div className="card-footer">
            <div className="price-tag">
              ฿{product.price ? parseInt(product.price).toLocaleString() : '-'}
            </div>
            <div className="card-actions">
              <BookmarkButton product={product} email={email} />
              <ReviewButton   product={product} email={email} userName="" />
            </div>
          </div>
        </div>

        {/* ── ขวา: chart ── */}
        <div className="card-right">
          <div className="chart-container">
            <Radar data={getChartData(product.function_tags)} options={chartOptions} />
          </div>
        </div>

      </div>

      {/* REVIEWS */}
      <div className="card-reviews-toggle">
        <button className="rv-toggle-btn" onClick={() => setShowReviews(v => !v)}>
          ⭐ รีวิวสินค้า {showReviews ? '▲' : '▼'}
        </button>
      </div>
      {showReviews && (
        <div className="card-reviews-body">
          <ProductReviews productName={product.name} />
        </div>
      )}
    </div>
  );
};

const RoutineCard = ({ product, email }) => (
  <div className="routine-card">
    <div className="routine-card-header">
      <span className="routine-step-icon">{product.step_icon}</span>
      <div className="routine-step-info">
        <div className="routine-step-num">STEP {product.step}</div>
        <div className="routine-step-label">{product.step_label}</div>
      </div>
    </div>
    <div className="routine-card-body">
      <div className="routine-img-box">
        {product.image_url
          ? <img src={product.image_url} alt={product.name} className="routine-img"
              onError={e => e.target.style.display = 'none'} />
          : <span className="routine-img-placeholder">🧴</span>
        }
      </div>
      <div className="routine-product-info">
        <div className="routine-brand">{product.brand}</div>
        <div className="routine-name">{product.name}</div>
        <div className="routine-tags">
          {product.function_tags && product.function_tags.split(',').slice(0, 2).map((tag, i) => (
            <span key={i} className="routine-tag">{tag.trim()}</span>
          ))}
        </div>
      </div>
      <div className="routine-price-col">
        <div className="routine-price">฿{product.price ? parseInt(product.price).toLocaleString() : '-'}</div>
        <BookmarkButton product={product} email={email} />
      </div>
    </div>
  </div>
);

const StepResults = ({ recommend, routine, user, onRestart }) => {
  const recList     = Array.isArray(recommend) ? recommend : [];
  const routineList = Array.isArray(routine)   ? routine   : [];
  const maxScore    = recList.length > 0
    ? Math.max(...recList.map(p => parseFloat(p.final_score) || 0)) : 1;
  const email = user?.email || null;

  return (
    <div className="step-content fadeIn">
      <SectionHeader icon="✨" title="สินค้าที่เหมาะกับคุณ"
        subtitle="Top 5 ที่ match กับสภาพผิวและปัญหาของคุณมากที่สุด" />

      {recList.length > 0 ? (
        <div className="results-grid results-grid-mb">
          {recList.map((product, i) => (
            <ProductCard key={i} product={product} email={email}
              matchPercent={maxScore > 0
                ? Math.round((parseFloat(product.final_score) / maxScore) * 100) : 0}
            />
          ))}
        </div>
      ) : (
        <div className="results-empty results-grid-mb">ไม่พบสินค้าที่ตรงกัน</div>
      )}

      <div className="results-divider" />

      <SectionHeader icon="📋" title="Skincare Routine ของคุณ"
        subtitle="เรียงตามลำดับการใช้งาน step 1 → 5" />

      {routineList.length > 0 ? (
        <div className="routine-list">
          {routineList.map((product, i) => (
            <RoutineCard key={i} product={product} email={email} />
          ))}
        </div>
      ) : (
        <div className="results-empty routine-mb">ไม่พบข้อมูล routine</div>
      )}

      <div className="button-group">
        <button className="btn-back" onClick={onRestart}>🔄 วิเคราะห์ใหม่</button>
      </div>
    </div>
  );
};

export default StepResults;