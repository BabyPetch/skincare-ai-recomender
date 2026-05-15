import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import './DashboardPage.css';

const API = import.meta.env.VITE_API_URL || 'http://127.0.0.1:5000/api';

const CONCERN_LABELS = {
  acne_control:   { label: 'สิว',             icon: '', color: '#F97316' },
  brightening:    { label: 'หมองคล้ำ/ฝ้า',    icon: '', color: '#EAB308' },
  anti_aging:     { label: 'ริ้วรอย',          icon: '', color: '#8B5CF6' },
  hydrating:      { label: 'แห้งกร้าน',        icon: '', color: '#3B82F6' },
  barrier_repair: { label: 'ผิวเสีย/แพ้ง่าย', icon: '', color: '#10B981' },
  calming:        { label: 'ผิวแดง/อักเสบ',   icon: '', color: '#06B6D4' },
  exfoliating:    { label: 'รูขุมขนกว้าง',    icon: '', color: '#6366F1' },
  antioxidant:    { label: 'ริ้วรอยดำ/กระ',   icon: '', color: '#EC4899' },
};

const SKIN_LABELS = {
  oily:        { label: 'หน้ามัน',   icon: '', color: '#EAB308' },
  dry:         { label: 'หน้าแห้ง',  icon: '', color: '#F97316' },
  combination: { label: 'ผิวผสม',    icon: '', color: '#8B5CF6' },
  sensitive:   { label: 'แพ้ง่าย',  icon: '', color: '#EC4899' },
  normal:      { label: 'ผิวธรรมดา', icon: '', color: '#10B981' },
};

const CAT_LABELS = {
  moisturizer: 'มอยส์เจอไรเซอร์',
  serum:       'เซรั่ม',
  sunscreen:   'กันแดด',
  toner:       'โทนเนอร์',
  cleanser:    'คลีนเซอร์',
  mask:        'มาส์ก',
  exfoliator:  'เอ็กซ์โฟเลียเตอร์',
  eye_care:    'ครีมตา',
};

/* ---- helpers ---- */
const parseJSON = (v) => {
  if (!v) return [];
  if (Array.isArray(v)) return v;
  try { return JSON.parse(v); } catch { return []; }
};

const fmtDate = (str) => {
  if (!str) return '';
  const d = new Date(str);
  return isNaN(d) ? str : d.toLocaleDateString('th-TH', { day: 'numeric', month: 'short', year: '2-digit' });
};

/* ---- stat computation ---- */
const computeStats = (history) => {
  const concernCount = {};
  const skinCount    = {};
  const catCount     = {};
  let   totalSpend   = 0;
  let   spendCount   = 0;

  history.forEach(h => {
    // skin type
    if (h.skin_type) skinCount[h.skin_type] = (skinCount[h.skin_type] || 0) + 1;

    // concerns
    parseJSON(h.concerns).forEach(c => {
      concernCount[c] = (concernCount[c] || 0) + 1;
    });

    // products from recommend
    parseJSON(h.results).forEach(p => {
      if (p.major_category) catCount[p.major_category] = (catCount[p.major_category] || 0) + 1;
      if (p.price) { totalSpend += parseInt(p.price); spendCount++; }
    });
  });

  const topConcerns  = Object.entries(concernCount).sort((a,b) => b[1]-a[1]).slice(0,4);
  const topSkin      = Object.entries(skinCount).sort((a,b) => b[1]-a[1])[0];
  const topCats      = Object.entries(catCount).sort((a,b) => b[1]-a[1]).slice(0,5);
  const avgPrice     = spendCount > 0 ? Math.round(totalSpend / spendCount) : 0;

  return { topConcerns, topSkin, topCats, avgPrice, totalSessions: history.length };
};

/* =============================== */
const DashboardPage = ({ user }) => {
  const navigate = useNavigate();
  const [history,  setHistory]  = useState([]);
  const [loading,  setLoading]  = useState(true);
  const [stats,    setStats]    = useState(null);

  const fetchHistory = useCallback(async () => {
    if (!user?.email) return;
    try {
      const res  = await fetch(`${API}/user/${user.email}`);
      const data = await res.json();
      const hist = data.history || [];
      setHistory(hist);
      setStats(computeStats(hist));
    } catch (e) { console.error(e); }
    finally { setLoading(false); }
  }, [user]);

  useEffect(() => { fetchHistory(); }, [fetchHistory]);

  if (!user) { navigate('/login'); return null; }

  if (loading) return (
    <div className="dash-page">
      <div className="dash-loading"><div className="dash-spinner" /><p>กำลังวิเคราะห์ข้อมูลผิว...</p></div>
    </div>
  );

  if (history.length === 0) return (
    <div className="dash-page">
      <div className="dash-empty">
        <div className="dash-empty-icon">📊</div>
        <h2>ยังไม่มีข้อมูลเพียงพอ</h2>
        <p>วิเคราะห์ผิวอย่างน้อย 1 ครั้งเพื่อดู Dashboard</p>
        <button className="dash-btn-primary" onClick={() => navigate('/advisor')}>เริ่มวิเคราะห์ผิว ✨</button>
      </div>
    </div>
  );

  const { topConcerns, topSkin, topCats, avgPrice, totalSessions } = stats;
  const maxConcern = topConcerns[0]?.[1] || 1;
  const maxCat     = topCats[0]?.[1]     || 1;

  return (
    <div className="dash-page">
      <div className="dash-inner">

        {/* ===== Header ===== */}
        <div className="dash-header">
          <div>
            <h1 className="dash-title">Dashboard ผิวของคุณ</h1>
            <p className="dash-subtitle">วิเคราะห์จาก {totalSessions} ครั้งที่ผ่านมา</p>
          </div>
          <button className="dash-back-btn" onClick={() => navigate(-1)}>← กลับ</button>
        </div>

        {/* ===== Top Summary Cards ===== */}
        <div className="dash-summary-row">

          <div className="dash-stat-card dash-stat-purple">
            <div className="dash-stat-icon">🔬</div>
            <div className="dash-stat-num">{totalSessions}</div>
            <div className="dash-stat-label">ครั้งที่วิเคราะห์</div>
          </div>

          <div className="dash-stat-card dash-stat-indigo">
            <div className="dash-stat-icon">{topSkin ? SKIN_LABELS[topSkin[0]]?.icon : '?'}</div>
            <div className="dash-stat-num">{topSkin ? SKIN_LABELS[topSkin[0]]?.label : '-'}</div>
            <div className="dash-stat-label">ประเภทผิวบ่อยสุด</div>
          </div>

          <div className="dash-stat-card dash-stat-violet">
            <div className="dash-stat-icon">💰</div>
            <div className="dash-stat-num">฿{avgPrice.toLocaleString()}</div>
            <div className="dash-stat-label">ราคาเฉลี่ยที่แนะนำ</div>
          </div>

          <div className="dash-stat-card dash-stat-fuchsia">
            <div className="dash-stat-icon">{topConcerns[0] ? CONCERN_LABELS[topConcerns[0][0]]?.icon : '?'}</div>
            <div className="dash-stat-num" style={{ fontSize: '16px' }}>
              {topConcerns[0] ? CONCERN_LABELS[topConcerns[0][0]]?.label : '-'}
            </div>
            <div className="dash-stat-label">ปัญหาที่พบบ่อยสุด</div>
          </div>

        </div>

        {/* ===== Two Column ===== */}
        <div className="dash-grid-2">

          {/* Concerns Bar */}
          <div className="dash-card">
            <h3 className="dash-card-title">ปัญหาผิวที่พบบ่อย</h3>
            {topConcerns.length === 0
              ? <p className="dash-empty-text">ไม่มีข้อมูล</p>
              : topConcerns.map(([key, count]) => {
                  const info = CONCERN_LABELS[key] || { label: key, icon: '●', color: '#6366F1' };
                  const pct  = Math.round((count / maxConcern) * 100);
                  return (
                    <div key={key} className="dash-bar-row">
                      <div className="dash-bar-label">
                        <span>{info.icon}</span>
                        <span>{info.label}</span>
                      </div>
                      <div className="dash-bar-track">
                        <div className="dash-bar-fill" style={{ width: `${pct}%`, background: info.color }} />
                      </div>
                      <div className="dash-bar-count">{count}x</div>
                    </div>
                  );
                })
            }
          </div>

          {/* Category Bar */}
          <div className="dash-card">
            <h3 className="dash-card-title">ประเภทสินค้าที่ได้รับแนะนำ</h3>
            {topCats.length === 0
              ? <p className="dash-empty-text">ไม่มีข้อมูล</p>
              : topCats.map(([key, count]) => {
                  const pct = Math.round((count / maxCat) * 100);
                  return (
                    <div key={key} className="dash-bar-row">
                      <div className="dash-bar-label">
                        <span style={{ fontSize: '13px' }}>{CAT_LABELS[key] || key}</span>
                      </div>
                      <div className="dash-bar-track">
                        <div className="dash-bar-fill" style={{ width: `${pct}%`, background: 'linear-gradient(90deg,#4F46E5,#8B5CF6)' }} />
                      </div>
                      <div className="dash-bar-count">{count}x</div>
                    </div>
                  );
                })
            }
          </div>
        </div>

        {/* ===== Skin Type Trend ===== */}
        <div className="dash-card">
          <h3 className="dash-card-title">ประเภทผิวในแต่ละครั้ง</h3>
          <div className="dash-timeline">
            {history.slice(0, 8).map((h, i) => {
              const skin = SKIN_LABELS[h.skin_type] || { label: h.skin_type, icon: '●', color: '#94A3B8' };
              const concerns = parseJSON(h.concerns);
              return (
                <div key={i} className="dash-timeline-item">
                  <div className="dash-timeline-dot" style={{ background: skin.color }} />
                  <div className="dash-timeline-body">
                    <div className="dash-timeline-top">
                      <span className="dash-timeline-skin" style={{ color: skin.color }}>
                        {skin.icon} {skin.label}
                      </span>
                      <span className="dash-timeline-date">{fmtDate(h.date)}</span>
                    </div>
                    {concerns.length > 0 && (
                      <div className="dash-timeline-concerns">
                        {concerns.slice(0, 3).map(c => (
                          <span key={c} className="dash-concern-chip">
                            {CONCERN_LABELS[c]?.icon} {CONCERN_LABELS[c]?.label || c}
                          </span>
                        ))}
                        {concerns.length > 3 && <span className="dash-concern-chip">+{concerns.length - 3}</span>}
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* ===== Top Recommended Products ===== */}
        <div className="dash-card">
          <h3 className="dash-card-title">สินค้าที่ได้รับแนะนำล่าสุด</h3>
          <div className="dash-product-list">
            {(() => {
              const seen = new Set();
              const products = [];
              for (const h of history) {
                for (const p of parseJSON(h.results)) {
                  if (!seen.has(p.name) && products.length < 5) {
                    seen.add(p.name);
                    products.push(p);
                  }
                }
                if (products.length >= 5) break;
              }
              return products.map((p, i) => (
                <div key={i} className="dash-product-row">
                  <div className="dash-product-img">
                    {p.image_url
                      ? <img src={p.image_url} alt={p.name} onError={e => e.target.style.display='none'} />
                      : <span>🧴</span>}
                  </div>
                  <div className="dash-product-info">
                    <div className="dash-product-brand">{p.brand}</div>
                    <div className="dash-product-name">{p.name}</div>
                  </div>
                  <div className="dash-product-price">
                    ฿{p.price ? parseInt(p.price).toLocaleString() : '-'}
                  </div>
                </div>
              ));
            })()}
          </div>
        </div>

        {/* CTA */}
        <div className="dash-cta-row">
          <button className="dash-btn-primary" onClick={() => navigate('/advisor')}>✨ วิเคราะห์ผิวใหม่</button>
          <button className="dash-btn-outline" onClick={() => navigate('/search')}>🔍 ค้นหาสินค้า</button>
          <button className="dash-btn-outline" onClick={() => navigate('/bookmarks')}>🔖 สินค้าที่บันทึก</button>
        </div>

      </div>
    </div>
  );
};

export default DashboardPage;