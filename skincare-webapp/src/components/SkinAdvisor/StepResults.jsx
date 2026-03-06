import React from 'react';
import { Radar } from 'react-chartjs-2';
import {
  Chart as ChartJS, RadialLinearScale, PointElement,
  LineElement, Filler, Tooltip, Legend,
} from 'chart.js';
import BookmarkButton from '../BookmarkButton';

ChartJS.register(RadialLinearScale, PointElement, LineElement, Filler, Tooltip, Legend);

const CHART_KEYS = [
  { label: 'ลดสิว',     tag: 'acne_control' },
  { label: 'กระจ่างใส', tag: 'brightening'  },
  { label: 'ชุ่มชื้น',  tag: 'hydrating'    },
  { label: 'ลดริ้วรอย', tag: 'anti_aging'   },
  { label: 'อ่อนโยน',   tag: 'calming'      },
];

const getChartData = (functionTags) => {
  const tags = typeof functionTags === 'string'
    ? functionTags.split(',').map(t => t.trim()) : [];
  return {
    labels: CHART_KEYS.map(k => k.label),
    datasets: [{
      label: 'คะแนน',
      data: CHART_KEYS.map(k => tags.includes(k.tag) ? 8 : 3),
      backgroundColor: 'rgba(99,102,241,0.2)',
      borderColor: '#6366F1', borderWidth: 2,
      pointBackgroundColor: '#fff', pointBorderColor: '#6366F1', pointRadius: 3,
    }],
  };
};

const chartOptions = {
  scales: {
    r: {
      min: 0, max: 10, ticks: { display: false },
      pointLabels: { font: { size: 11, family: "'Prompt',sans-serif" }, color: '#64748B' },
      grid: { color: '#E2E8F0' }
    }
  },
  plugins: { legend: { display: false } },
  maintainAspectRatio: false,
};

const getCategoryLabel = (cat) => ({
  moisturizer: 'มอยส์เจอไรเซอร์', serum: 'เซรั่ม', sunscreen: 'กันแดด',
  toner: 'โทนเนอร์', cleanser: 'คลีนเซอร์', mask: 'มาส์ก',
  exfoliator: 'เอ็กซ์โฟเลียเตอร์', eye_care: 'ครีมตา',
}[cat] || cat || '-');

const SectionHeader = ({ icon, title, subtitle }) => (
  <div style={{ marginBottom: '20px' }}>
    <h2 style={{ fontSize: '22px', fontWeight: '700', color: '#1E293B', margin: '0 0 4px' }}>
      {icon} {title}
    </h2>
    <p style={{ color: '#64748B', margin: 0, fontSize: '14px' }}>{subtitle}</p>
  </div>
);

const ProductCard = ({ product, matchPercent, email }) => (
  <div className="result-card">
    <div className="card-header">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <span className="match-badge">{matchPercent}% Match</span>
        <BookmarkButton product={product} email={email} />
      </div>
      <p className="brand-name">{product.brand || '-'}</p>
      <h3 className="product-name">{product.name}</h3>
    </div>
    {product.image_url && (
      <div style={{ textAlign: 'center', margin: '10px 0' }}>
        <img src={product.image_url} alt={product.name}
          style={{ width: '80px', height: '80px', objectFit: 'contain', borderRadius: '8px' }}
          onError={e => e.target.style.display = 'none'}
        />
      </div>
    )}
    <div className="chart-container">
      <Radar data={getChartData(product.function_tags)} options={chartOptions} />
    </div>
    <div className="card-footer">
      <div className="price-tag">฿{product.price ? parseInt(product.price).toLocaleString() : '-'}</div>
      <div className="tags"><span className="tag">{getCategoryLabel(product.major_category)}</span></div>
    </div>
  </div>
);

const RoutineCard = ({ product, email }) => (
  <div style={{
    background: 'white', borderRadius: '20px', border: '1px solid #E2E8F0',
    overflow: 'hidden', boxShadow: '0 4px 12px rgba(0,0,0,0.05)',
  }}>
    <div style={{
      background: 'linear-gradient(135deg, #4F46E5, #8B5CF6)',
      padding: '12px 20px', display: 'flex', alignItems: 'center', gap: '12px',
    }}>
      <span style={{ fontSize: '22px' }}>{product.step_icon}</span>
      <div style={{ flex: 1 }}>
        <div style={{ color: 'rgba(255,255,255,0.7)', fontSize: '11px', fontWeight: '600' }}>STEP {product.step}</div>
        <div style={{ color: 'white', fontSize: '15px', fontWeight: '700' }}>{product.step_label}</div>
      </div>
    </div>
    <div style={{ padding: '14px 18px', display: 'flex', gap: '14px', alignItems: 'center' }}>
      <div style={{
        width: '60px', height: '60px', borderRadius: '10px', flexShrink: 0,
        background: '#F1F5F9', display: 'flex', alignItems: 'center', justifyContent: 'center', overflow: 'hidden',
      }}>
        {product.image_url ? (
          <img src={product.image_url} alt={product.name}
            style={{ width: '100%', height: '100%', objectFit: 'contain' }}
            onError={e => e.target.style.display = 'none'}
          />
        ) : <span style={{ fontSize: '24px' }}>🧴</span>}
      </div>
      <div style={{ flex: 1, minWidth: 0 }}>
        <div style={{ fontSize: '11px', color: '#64748B', fontWeight: '600',
          textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: '2px' }}>
          {product.brand}
        </div>
        <div style={{ fontSize: '15px', fontWeight: '700', color: '#1E293B',
          overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', marginBottom: '5px' }}>
          {product.name}
        </div>
        <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
          {product.function_tags && product.function_tags.split(',').slice(0, 2).map((tag, i) => (
            <span key={i} style={{
              background: '#F1F5F9', color: '#475569', padding: '2px 8px',
              borderRadius: '20px', fontSize: '11px'
            }}>{tag.trim()}</span>
          ))}
        </div>
      </div>
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: '6px', flexShrink: 0 }}>
        <div style={{ fontSize: '18px', fontWeight: '800', color: '#4F46E5' }}>
          ฿{product.price ? parseInt(product.price).toLocaleString() : '-'}
        </div>
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
        <div className="results-grid" style={{ marginBottom: '40px' }}>
          {recList.map((product, i) => (
            <ProductCard key={i} product={product} email={email}
              matchPercent={maxScore > 0 ? Math.round((parseFloat(product.final_score) / maxScore) * 100) : 0}
            />
          ))}
        </div>
      ) : (
        <div style={{ textAlign: 'center', padding: '30px', color: '#64748B',
          background: '#F8FAFC', borderRadius: '12px', marginBottom: '40px' }}>
          ไม่พบสินค้าที่ตรงกัน
        </div>
      )}

      <div style={{ borderTop: '2px dashed #E2E8F0', margin: '10px 0 30px' }} />

      <SectionHeader icon="📋" title="Skincare Routine ของคุณ"
        subtitle="เรียงตามลำดับการใช้งาน step 1 → 5" />
      {routineList.length > 0 ? (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', marginBottom: '30px' }}>
          {routineList.map((product, i) => (
            <RoutineCard key={i} product={product} email={email} />
          ))}
        </div>
      ) : (
        <div style={{ textAlign: 'center', padding: '30px', color: '#64748B',
          background: '#F8FAFC', borderRadius: '12px', marginBottom: '30px' }}>
          ไม่พบข้อมูล routine
        </div>
      )}

      <div className="button-group">
        <button className="btn-back" onClick={onRestart}>🔄 วิเคราะห์ใหม่</button>
      </div>
    </div>
  );
};

export default StepResults;