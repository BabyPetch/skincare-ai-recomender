import React, { useState, useEffect } from 'react';
import './ProductReviews.css';

const API = import.meta.env.VITE_API_URL || 'http://127.0.0.1:5000/api';

const StarDisplay = ({ rating, size = 14 }) => (
  <span style={{ fontSize: size, letterSpacing: '-1px', color: '#FBBF24' }}>
    {'★'.repeat(rating)}
    <span style={{ color: '#E2E8F0' }}>{'★'.repeat(5 - rating)}</span>
  </span>
);

const ProductReviews = ({ productName }) => {
  const [data,    setData]    = useState(null);
  const [loading, setLoading] = useState(true);
  const [expanded, setExpanded] = useState(false);

  useEffect(() => {
    if (!productName) return;
    fetch(`${API}/reviews/${encodeURIComponent(productName)}`)
      .then(r => r.json())
      .then(d => { setData(d); setLoading(false); })
      .catch(() => setLoading(false));
  }, [productName]);

  if (loading) return <div className="prv-loading">กำลังโหลดรีวิว...</div>;
  if (!data || data.total === 0) return (
    <div className="prv-empty">ยังไม่มีรีวิว — เป็นคนแรกที่รีวิวสินค้านี้!</div>
  );

  const visibleReviews = expanded ? data.reviews : data.reviews.slice(0, 3);

  return (
    <div className="prv-container">
      {/* Summary */}
      <div className="prv-summary">
        <div className="prv-avg-block">
          <div className="prv-avg-num">{data.average}</div>
          <StarDisplay rating={Math.round(data.average)} size={18} />
          <div className="prv-total">{data.total} รีวิว</div>
        </div>

        <div className="prv-dist">
          {[5,4,3,2,1].map(s => {
            const count = data.distribution[s] || 0;
            const pct   = data.total > 0 ? (count / data.total) * 100 : 0;
            return (
              <div key={s} className="prv-dist-row">
                <span className="prv-dist-label">{s}★</span>
                <div className="prv-dist-track">
                  <div className="prv-dist-fill" style={{ width: `${pct}%` }} />
                </div>
                <span className="prv-dist-count">{count}</span>
              </div>
            );
          })}
        </div>
      </div>

      {/* Review List */}
      <div className="prv-list">
        {visibleReviews.map((r, i) => (
          <div key={i} className="prv-item">
            <div className="prv-item-header">
              <div className="prv-avatar">{r.user_name?.[0] || '?'}</div>
              <div className="prv-item-meta">
                <div className="prv-item-name">{r.user_name || 'ไม่ระบุชื่อ'}</div>
                <StarDisplay rating={r.rating} size={13} />
              </div>
              <div className="prv-item-date">
                {new Date(r.created_at).toLocaleDateString('th-TH', {
                  day: 'numeric', month: 'short', year: '2-digit'
                })}
              </div>
            </div>
            {r.title && <div className="prv-item-title">{r.title}</div>}
            {r.body  && <div className="prv-item-body">{r.body}</div>}
          </div>
        ))}
      </div>

      {data.reviews.length > 3 && (
        <button className="prv-more-btn" onClick={() => setExpanded(v => !v)}>
          {expanded ? 'ซ่อนรีวิว ▲' : `ดูทั้งหมด ${data.reviews.length} รีวิว ▼`}
        </button>
      )}
    </div>
  );
};

export default ProductReviews;