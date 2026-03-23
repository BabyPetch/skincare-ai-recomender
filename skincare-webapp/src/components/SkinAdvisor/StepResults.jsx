import React, { useState, useMemo } from 'react';
import { createPortal } from 'react-dom';

import BookmarkButton from '../Reviews/BookmarkButton';
import ReviewButton   from '../Reviews/ReviewButton';
import ProductReviews from '../Reviews/ProductReviews';
import '../SkinAdvisorCss/StepResults.css';


const PAGE_SIZE = 10;

const TAG_LABELS = {
  acne_control: 'ลดสิว',      brightening:    'กระจ่างใส',
  hydrating:    'ชุ่มชื้น',   anti_aging:     'ลดริ้วรอย',
  calming:      'อ่อนโยน',    barrier_repair: 'ซ่อมแซมผิว',
  oil_control:  'คุมมัน',     lightweight:    'เบาสบาย',
  antioxidant:  'ต้านอนุมูล', sunscreen:      'กันแดด',
};

const parseTags = (ft) =>
  ft ? ft.split(',').map(t => t.trim()).filter(Boolean).slice(0, 4) : [];

const SectionHeader = ({ icon, title, subtitle }) => (
  <div className="section-header">
    <h2 className="section-title">{icon} {title}</h2>
    <p className="section-subtitle">{subtitle}</p>
  </div>
);

const getBadgeGrad = (rank) => {
  if (rank <= 3)  return 'linear-gradient(135deg, #6366F1, #8B5CF6)';
  if (rank <= 10) return 'linear-gradient(135deg, #0EA5E9, #38BDF8)';
  return 'linear-gradient(135deg, #64748B, #94A3B8)';
};

const getRankEmoji = (rank) => {
  if (rank === 1) return '🥇';
  if (rank === 2) return '🥈';
  if (rank === 3) return '🥉';
  return `#${rank}`;
};

/* ═══════════════════════════════
   Input Summary Bar
═══════════════════════════════ */
const SKIN_LABELS_S = {
  oily: 'หน้ามัน', dry: 'หน้าแห้ง',
  combination: 'ผิวผสม', sensitive: 'แพ้ง่าย', normal: 'ผิวธรรมดา',
};
const CONCERN_LABELS_S = {
  acne_control: 'สิว', brightening: 'หมองคล้ำ/ฝ้า',
  anti_aging: 'ริ้วรอย', hydrating: 'แห้งกร้าน',
  barrier_repair: 'ผิวเสีย', calming: 'ผิวแดง',
  exfoliating: 'รูขุมขน', antioxidant: 'กระ/ริ้วรอยดำ',
};
const AGE_LABELS_S = {
  teen: 'วัยรุ่น', young: '20–29', adult: '30–39',
  mature: '40–49', senior: '50+',
};
const PRICE_LABELS_S = {
  low: '< ฿500', medium: '฿500–1,500',
  high: '> ฿1,500', any: 'ไม่จำกัด',
};
const ENV_LABELS_S = {
  hot_humid: 'ร้อนชื้น', ac_all_day: 'แอร์ตลอดวัน',
  mixed: 'ผสมผสาน', pollution: 'มลภาวะสูง', tropical: 'ชายทะเล',
};

const Chip = ({ text }) => (
  <span style={{
    display: 'inline-flex', alignItems: 'center',
    background: 'var(--bg-subtle)', color: 'var(--text-secondary)',
    border: '1px solid var(--border)',
    padding: '3px 10px', borderRadius: '20px',
    fontSize: '12px', fontWeight: '600', whiteSpace: 'nowrap',
  }}>{text}</span>
);

const SummaryBar = ({ summary }) => {
  if (!summary) return null;
  const s = summary;
  const chips = [
    s.skinType    && SKIN_LABELS_S[s.skinType],
    s.age         && AGE_LABELS_S[s.age],
    s.environment && ENV_LABELS_S[s.environment],
    s.priceRange  && PRICE_LABELS_S[s.priceRange],
    ...(s.concerns || []).map(c => CONCERN_LABELS_S[c]).filter(Boolean),
  ].filter(Boolean);

  if (chips.length === 0) return null;

  return (
    <div style={{
      background: 'var(--bg-card)', borderRadius: '14px',
      border: '1px solid var(--border)', padding: '12px 16px',
      marginBottom: '16px', boxShadow: 'var(--shadow-sm)',
    }}>
      <div style={{
        fontSize: '11px', fontWeight: '800', color: 'var(--text-muted)',
        marginBottom: '8px', textTransform: 'uppercase', letterSpacing: '0.5px',
      }}>
        วิเคราะห์จาก
      </div>
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
        {chips.map((c, i) => <Chip key={i} text={c} />)}
      </div>
    </div>
  );
};

/* ═══════════════════════════════
   Explanation Modal
═══════════════════════════════ */
const ExplanationModal = ({ product, matchPercent, rank, onClose, userSkinType }) => {
  const explanation = product.explanation || {};

  const summaryList    = Array.isArray(explanation)
    ? explanation
    : (explanation.summary || []);
  const breakdown      = explanation.score_breakdown  || null;
  const concernReasons = explanation.concern_reasons  || [];
  const otherReasons   = explanation.other_reasons    || [];

  // ✅ FIX: ใช้ weight ใหม่ที่ตรงกับ ai_engine_v2.py
  // weight ตรงกับ ai_engine_v2.py: Concern 55%, Cosine 25%, Context 20%
  // skin type เป็น Hard Filter ไม่ใช่ weight → แสดงแยกต่างหาก
  const layerWeights = { concern: 0.55, tfidf: 0.25, context: 0.20 };

  const layers = breakdown ? [
    { key: 'concern', label: 'Concern Match',   desc: 'ส่วนผสมออกฤทธิ์ที่ตรงกับปัญหาผิว',   color: '#6366F1', weight: '55%' },
    { key: 'tfidf',   label: 'Text Similarity', desc: 'ความคล้ายคลึงของข้อมูลสินค้า',        color: '#0EA5E9', weight: '25%' },
    { key: 'context', label: 'Context Boost',   desc: 'บริบท อายุ สภาพแวดล้อม ประสบการณ์',  color: '#10B981', weight: '20%' },
  ] : [];

  // skin type status — userSkinType รับมาจาก prop (summary.skinType จาก StepResults)
  const productSkintype = (product.skintype || '').toLowerCase();
  const userSkintype    = (userSkinType || '').toLowerCase();

  const skinStatus = (() => {
    if (!productSkintype)
      return { label: 'ไม่ระบุ', color: '#94A3B8', bg: 'var(--bg-subtle)', icon: '❓' };
    if (productSkintype.includes('all') || productSkintype.includes('ทุกสภาพผิว'))
      return { label: `ใช้ได้ทุกผิว — ไม่ได้ระบุตรง ${userSkintype}`, 
            color: '#F59E0B', bg: '#FFFBEB', icon: '△' };
    if (userSkintype && productSkintype.includes(userSkintype))
      return { label: `ตรงผิวคุณ (${product.skintype})`, color: '#10B981', bg: '#ECFDF5', icon: '✓✓' };
    return { label: `ไม่ตรงผิวคุณ (${product.skintype})`, color: '#EF4444', bg: '#FEF2F2', icon: '✗' };
  })();

  return createPortal(
    <div
      onClick={onClose}
      style={{
        position: 'fixed', inset: 0,
        background: 'rgba(0,0,0,0.55)',
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        zIndex: 9999, padding: '20px',
      }}
    >
      <div
        onClick={e => e.stopPropagation()}
        style={{
          background: 'var(--bg-card)',
          borderRadius: '24px',
          padding: '40px 48px',
          width: '100%', maxWidth: '820px',
          maxHeight: '92vh', overflowY: 'auto',
          boxShadow: '0 20px 60px rgba(0,0,0,0.35)',
          border: '1px solid var(--border)',
          position: 'relative',
        }}
      >
        {/* close */}
        <button onClick={onClose} style={{
          position: 'absolute', top: '16px', right: '16px',
          width: '32px', height: '32px', borderRadius: '50%',
          border: 'none', background: 'var(--bg-subtle)',
          color: 'var(--text-secondary)', fontSize: '20px',
          cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center',
          transition: 'all 0.2s',
        }}
          onMouseEnter={e => Object.assign(e.currentTarget.style, { background: '#EF4444', color: 'white' })}
          onMouseLeave={e => Object.assign(e.currentTarget.style, { background: 'var(--bg-subtle)', color: 'var(--text-secondary)' })}
        >×</button>

        {/* header */}
        <div style={{ marginBottom: '20px', paddingRight: '32px' }}>
          <div style={{ fontSize: '11px', color: 'var(--text-muted)', fontWeight: '700', marginBottom: '4px', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
            {product.brand}
          </div>
          <h3 style={{ margin: '0 0 12px', fontSize: '20px', fontWeight: '800', color: 'var(--text-primary)', lineHeight: 1.4 }}>
            ทำไมถึงแนะนำ "{product.name}"?
          </h3>
          <div style={{ display: 'flex', gap: '6px' }}>
            <span style={{
              background: getBadgeGrad(rank), color: 'white',
              padding: '3px 10px', borderRadius: '20px', fontSize: '12px', fontWeight: '700',
            }}>{getRankEmoji(rank)} อันดับ {rank}</span>
            <span style={{
              background: getBadgeGrad(rank), color: 'white',
              padding: '3px 10px', borderRadius: '20px', fontSize: '12px', fontWeight: '700',
            }}>{matchPercent}% Match</span>
          </div>
        </div>

        {/* score breakdown */}
        {breakdown && (
          <div style={{ marginBottom: '20px' }}>
            <div style={{ fontSize: '14px', fontWeight: '800', color: 'var(--text-primary)', marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '6px' }}>
              Score Breakdown
              <span style={{ fontSize: '11px', color: 'var(--text-muted)', fontWeight: '400' }}>
                (คะแนนรวม {breakdown.final?.toFixed ? (breakdown.final * 100).toFixed(1) : '-'}%)
              </span>
            </div>
            {layers.map(l => {
              const layerData    = breakdown[l.key];
              const rawScore     = typeof layerData === 'object' ? (layerData?.score ?? 0) : (layerData ?? 0);
              const contribution = rawScore * layerWeights[l.key];
              const maxContrib   = layerWeights[l.key];
              const pct          = Math.round(rawScore * 100);
              const barPct       = maxContrib > 0
                ? Math.min(Math.round((contribution / maxContrib) * 100), 100)
                : 0;
              return (
                <div key={l.key} style={{ marginBottom: '10px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                    <div>
                      <span style={{ fontSize: '14px', fontWeight: '700', color: 'var(--text-primary)' }}>{l.label}</span>
                      <span style={{ fontSize: '12px', color: 'var(--text-muted)', marginLeft: '6px' }}>({l.weight})</span>
                    </div>
                    <span style={{ fontSize: '14px', fontWeight: '700', color: pct === 0 ? 'var(--text-muted)' : l.color }}>
                      {pct}%
                    </span>
                  </div>
                  <div style={{ height: '9px', background: 'var(--bg-subtle)', borderRadius: '10px', overflow: 'hidden' }}>
                    <div style={{
                      height: '100%',
                      width: `${barPct}%`,
                      background: pct === 0 ? 'var(--border)' : l.color,
                      borderRadius: '10px',
                      transition: 'width 0.6s ease',
                    }} />
                  </div>
                  <div style={{ fontSize: '10px', color: 'var(--text-muted)', marginTop: '2px', display: 'flex', justifyContent: 'space-between' }}>
                    <span>{l.desc}</span>
                    {pct === 0 && <span style={{ color: '#EF4444', fontWeight: '600' }}>ไม่ match</span>}
                  </div>
                </div>
              );
            })}
          </div>
        )}

        {/* skin type status block */}
        <div style={{
          display: 'flex', alignItems: 'center', gap: '10px',
          padding: '10px 14px', borderRadius: '12px',
          background: skinStatus.bg,
          border: `1.5px solid ${skinStatus.color}`,
          marginBottom: '16px',
        }}>
          <span style={{ fontSize: '18px', flexShrink: 0 }}></span>
          <div style={{ flex: 1 }}>
            <div style={{ fontSize: '12px', fontWeight: '800', color: 'var(--text-muted)', marginBottom: '4px', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
              Skin Type (Hard Filter)
            </div>
            <div style={{ fontSize: '15px', fontWeight: '700', color: skinStatus.color }}>
              {skinStatus.icon} {skinStatus.label}
            </div>
          </div>
          <span style={{
            fontSize: '11px', fontWeight: '700',
            background: skinStatus.color, color: 'white',
            padding: '2px 8px', borderRadius: '20px',
          }}>
            {productSkintype.includes('all') || productSkintype.includes('ทุกสภาพผิว')
              ? 'Universal'
              : userSkintype && productSkintype.includes(userSkintype)
                ? 'ตรง 100%'
                : 'ผ่าน Fallback'}
          </span>
        </div>

        <div style={{ borderTop: '1px dashed var(--border)', margin: '16px 0' }} />

        {/* concern reasons */}
        {concernReasons.length > 0 && (
          <div style={{ marginBottom: '16px' }}>
            <div style={{ fontSize: '14px', fontWeight: '800', color: 'var(--text-primary)', marginBottom: '12px' }}>
              ตรงกับปัญหาผิวของคุณ
            </div>
            {concernReasons.map((cr, i) => (
              <div key={i} style={{
                padding: '10px 12px', borderRadius: '10px',
                background: 'var(--bg-subtle)', marginBottom: '8px',
                border: '1px solid var(--border)',
              }}>
                <div style={{ fontSize: '13px', fontWeight: '700', color: '#6366F1', marginBottom: '6px' }}>
                  ✓ ช่วย{cr.label}
                  {cr.top_conf > 0 && (
                    <span style={{ fontSize: '10px', color: 'var(--text-muted)', fontWeight: '400', marginLeft: '6px' }}>
                      (ความมั่นใจ {Math.round(cr.top_conf * 100)}%)
                    </span>
                  )}
                </div>
                {cr.ingredients && cr.ingredients.length > 0 && (
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px' }}>
                    {cr.ingredients.map((ing, j) => (
                      <span key={j} style={{
                        background: '#EEF2FF', color: '#4F46E5',
                        padding: '4px 10px', borderRadius: '20px',
                        fontSize: '12px', fontWeight: '600',
                      }}>{ing}</span>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}

        {/* summary list (ai_engine เก่า — backward compat) */}
        {summaryList.length > 0 && concernReasons.length === 0 && (
          <div style={{ marginBottom: '16px' }}>
            <div style={{ fontSize: '12px', fontWeight: '800', color: 'var(--text-primary)', marginBottom: '10px' }}>
              เหตุผลที่แนะนำ
            </div>
            {summaryList.map((reason, i) => (
              <div key={i} style={{
                padding: '8px 12px', borderRadius: '10px',
                background: 'var(--bg-subtle)', marginBottom: '6px',
                fontSize: '12px', color: 'var(--text-secondary)',
                border: '1px solid var(--border)',
              }}>
                ✓ {reason}
              </div>
            ))}
          </div>
        )}

        {/* other reasons */}
        {otherReasons.length > 0 && (
          <div>
            <div style={{ fontSize: '12px', fontWeight: '800', color: 'var(--text-primary)', marginBottom: '10px' }}>
              ข้อมูลเพิ่มเติม
            </div>
            {otherReasons.map((r, i) => (
              <div key={i} style={{
                fontSize: '13px', color: 'var(--text-secondary)',
                padding: '7px 0',
                borderBottom: i < otherReasons.length - 1 ? '1px dashed var(--border)' : 'none',
              }}>• {r}</div>
            ))}
          </div>
        )}
      </div>
    </div>,
    document.body
  );
};

/* ═══════════════════════════════
   Product Card
═══════════════════════════════ */
const ProductCard = ({ product, matchPercent, rank, email, userName, onDismiss, userSkinType }) => {
  const [showReviews, setShowReviews] = useState(false);
  const [dismissing,  setDismissing]  = useState(false);
  const [showExplain, setShowExplain] = useState(false);
  const tags = parseTags(product.function_tags);

  const handleDismiss = () => {
    setDismissing(true);
    setTimeout(() => onDismiss(), 300);
  };

  return (
    <>
      {showExplain && (
        <ExplanationModal
          product={product}
          matchPercent={matchPercent}
          rank={rank}
          onClose={() => setShowExplain(false)}
          userSkinType={userSkinType}
        />
      )}

      <div
        className="result-card"
        style={{
          position: 'relative',
          transition: 'opacity 0.3s ease, transform 0.3s ease, max-height 0.32s ease, margin 0.32s ease',
          opacity:   dismissing ? 0 : 1,
          transform: dismissing ? 'translateX(56px) scale(0.95)' : 'none',
          maxHeight: dismissing ? '0' : '1400px',
          overflow:  dismissing ? 'hidden' : 'visible',
        }}
      >
        {/* ── × dismiss ── */}
        <button
          onClick={handleDismiss}
          title="ไม่ชอบ — เอาออก"
          style={{
            position: 'absolute', top: '12px', right: '12px',
            width: '30px', height: '30px', borderRadius: '50%',
            border: '1.5px solid var(--border)',
            background: 'var(--bg-subtle)', color: 'var(--text-muted)',
            fontSize: '18px', cursor: 'pointer',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            lineHeight: 1, transition: 'all 0.18s', zIndex: 10,
          }}
          onMouseEnter={e => Object.assign(e.currentTarget.style, {
            background: '#FEF2F2', borderColor: '#FCA5A5', color: '#EF4444',
            transform: 'scale(1.2) rotate(90deg)',
          })}
          onMouseLeave={e => Object.assign(e.currentTarget.style, {
            background: 'var(--bg-subtle)', borderColor: 'var(--border)',
            color: 'var(--text-muted)', transform: 'scale(1) rotate(0deg)',
          })}
        >×</button>

        <div className="card-main">

          {/* ── ซ้าย: รูป + ชื่อ + ราคา ── */}
          <div className="card-left">
            <div className="card-badge-row" style={{ display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
              <span className="match-badge" style={{ background: getBadgeGrad(rank) }}>
                {getRankEmoji(rank)} อันดับ {rank}
              </span>
              <span className="match-badge" style={{ background: getBadgeGrad(rank) }}>
                {matchPercent}% Match
              </span>
            </div>

            <div className="card-img-wrap">
              {product.image_url
                ? <img src={product.image_url} alt={product.name}
                    className="card-img-thumb"
                    onError={e => e.target.style.display = 'none'} />
                : <div className="card-img-placeholder">-</div>
              }
            </div>

            <p className="brand-name">{product.brand || '-'}</p>
            <h3 className="product-name">{product.name}</h3>

            {/* ── ปุ่ม "ทำไมถึงแนะนำ?" ── */}
            <button
              onClick={() => setShowExplain(true)}
              style={{
                marginTop: '10px', width: '100%',
                padding: '8px 12px', borderRadius: '10px',
                border: '1.5px solid #6366F1',
                background: 'var(--accent-light)', color: '#6366F1',
                fontSize: '12px', fontWeight: '700', cursor: 'pointer',
                fontFamily: "'Kanit', sans-serif", transition: 'all 0.18s',
                display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '6px',
              }}
              onMouseEnter={e => Object.assign(e.currentTarget.style, { background: '#6366F1', color: 'white' })}
              onMouseLeave={e => Object.assign(e.currentTarget.style, { background: 'var(--accent-light)', color: '#6366F1' })}
            >
              ทำไมถึงแนะนำ?
            </button>

            <div className="card-footer">
              <div className="price-tag">
                ฿{product.price ? parseInt(product.price).toLocaleString() : '-'}
              </div>
              <div className="card-actions">
                <BookmarkButton product={product} email={email} />
                <ReviewButton   product={product} email={email} userName={userName} />
              </div>
            </div>
          </div>

          {/* ── ขวา: Active Ingredients + Tags + Suitable For ── */}
          <div className="card-right" style={{ padding: '20px 24px', display: 'flex', flexDirection: 'column', gap: '16px', justifyContent: 'flex-start' }}>
            {(() => {
              const exp      = product.explanation || {};
              const concerns = Array.isArray(exp) ? [] : (exp.concern_reasons || []);
              const allIngr  = [];
              concerns.forEach(cr => {
                (cr.ingredients || []).forEach(ing => {
                  if (!allIngr.find(i => i.name === ing))
                    allIngr.push({ name: ing, label: cr.label, conf: cr.top_conf });
                });
              });
              const topIngr = allIngr; // แสดงทั้งหมด
              const otherR  = Array.isArray(exp) ? [] : (exp.other_reasons || []);
              const keyIngr = otherR.find(r => r.startsWith('Key ingredients:'));

              return (
                <>
                  {/* ── 1. Active Ingredients ── */}
                  <div>
                    <div style={{ fontSize: '11px', fontWeight: '800', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: '10px' }}>
                      Active Ingredients
                    </div>
                    {topIngr.length > 0 ? (
                      <div style={{
                        maxHeight: '180px', overflowY: 'auto',
                        display: 'flex', flexWrap: 'wrap', gap: '8px',
                        paddingRight: '4px',
                      }}>
                        {topIngr.map((ing, i) => (
                          <div key={i} style={{
                            background: 'var(--bg-subtle)', border: '1.5px solid #6366F1',
                            borderRadius: '12px', padding: '8px 14px',
                            fontSize: '12px', fontWeight: '700', color: 'var(--text-primary)',
                            display: 'flex', flexDirection: 'column', gap: '3px',
                            flexShrink: 0,
                          }}>
                            <span>{ing.name}</span>
                            <span style={{ fontSize: '10px', color: '#6366F1', fontWeight: '600' }}>
                              ช่วย{ing.label} · {Math.round(ing.conf * 100)}%
                            </span>
                          </div>
                        ))}
                      </div>
                    ) : keyIngr ? (
                      <div style={{
                        maxHeight: '180px', overflowY: 'auto',
                        display: 'flex', flexWrap: 'wrap', gap: '8px',
                        paddingRight: '4px',
                      }}>
                        {keyIngr.replace('Key ingredients: ', '').split(',').map((ing, i) => (
                          <div key={i} style={{
                            background: 'var(--bg-subtle)', border: '1.5px solid var(--border)',
                            borderRadius: '12px', padding: '8px 14px',
                            fontSize: '12px', fontWeight: '600', color: 'var(--text-secondary)',
                            flexShrink: 0,
                          }}>
                            {ing.trim()}
                          </div>
                        ))}
                      </div>
                    ) : (
                      <div style={{ color: 'var(--text-muted)', fontSize: '13px' }}>ไม่มีข้อมูลส่วนผสม</div>
                    )}
                  </div>

                  {/* ── 2. Tags (ย้ายมาจากซ้าย) ── */}
                  {tags.length > 0 && (
                    <div>
                      <div style={{ fontSize: '11px', fontWeight: '800', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: '10px' }}>
                        คุณสมบัติ
                      </div>
                      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                        {tags.map((tag, i) => (
                          <span key={i} style={{
                            background: 'var(--accent-light)', color: 'var(--accent-text)',
                            padding: '5px 12px', borderRadius: '20px',
                            fontSize: '12px', fontWeight: '600',
                            border: '1px solid var(--border-focus)',
                          }}>
                            {TAG_LABELS[tag] || tag}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* ── 3. Suitable For ── */}
                  <div style={{
                    padding: '12px 16px', borderRadius: '12px',
                    background: 'var(--bg-subtle)', border: '1px solid var(--border)',
                    display: 'flex', alignItems: 'center', gap: '10px',
                  }}>
                    
                    <div>
                      <div style={{ fontSize: '10px', fontWeight: '800', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: '3px' }}>
                        Suitable For
                      </div>
                      <div style={{ fontSize: '13px', fontWeight: '700', color: 'var(--text-primary)' }}>
                        {product.skintype || 'All Skin Types'}
                      </div>
                    </div>
                  </div>
                </>
              );
            })()}
          </div>
        </div>

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
    </>
  );
};

/* ═══════════════════════════════
   Pagination Bar
═══════════════════════════════ */
const PaginationBar = ({ currentPage, totalPages, onPage }) => {
  if (totalPages <= 1) return null;

  const pages = [];
  let start = Math.max(1, currentPage - 2);
  let end   = Math.min(totalPages, start + 4);
  if (end - start < 4) start = Math.max(1, end - 4);
  for (let i = start; i <= end; i++) pages.push(i);

  const btnBase = {
    width: '36px', height: '36px', borderRadius: '8px',
    border: '1.5px solid var(--border)',
    background: 'var(--bg-card)', color: 'var(--text-secondary)',
    fontSize: '14px', fontWeight: '600', cursor: 'pointer',
    fontFamily: "'Kanit', sans-serif", transition: 'all 0.15s',
    display: 'flex', alignItems: 'center', justifyContent: 'center',
  };
  const btnActive   = { ...btnBase, background: 'linear-gradient(135deg, #6366F1, #8B5CF6)', borderColor: '#6366F1', color: 'white' };
  const btnDisabled = { ...btnBase, opacity: 0.35, cursor: 'not-allowed' };

  return (
    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '6px', margin: '24px 0 8px' }}>
      <button style={currentPage === 1 ? btnDisabled : btnBase} disabled={currentPage === 1} onClick={() => onPage(currentPage - 1)}>←</button>
      {start > 1 && (<><button style={btnBase} onClick={() => onPage(1)}>1</button>{start > 2 && <span style={{ color: 'var(--text-muted)', fontSize: '13px' }}>…</span>}</>)}
      {pages.map(p => (
        <button key={p} style={p === currentPage ? btnActive : btnBase} onClick={() => onPage(p)}
          onMouseEnter={e => { if (p !== currentPage) Object.assign(e.currentTarget.style, { borderColor: 'var(--border-focus)', color: 'var(--accent-text)' }); }}
          onMouseLeave={e => { if (p !== currentPage) Object.assign(e.currentTarget.style, { borderColor: 'var(--border)', color: 'var(--text-secondary)' }); }}
        >{p}</button>
      ))}
      {end < totalPages && (<>{end < totalPages - 1 && <span style={{ color: 'var(--text-muted)', fontSize: '13px' }}>…</span>}<button style={btnBase} onClick={() => onPage(totalPages)}>{totalPages}</button></>)}
      <button style={currentPage === totalPages ? btnDisabled : btnBase} disabled={currentPage === totalPages} onClick={() => onPage(currentPage + 1)}>→</button>
    </div>
  );
};

/* ═══════════════════════════════
   Routine Card
═══════════════════════════════ */
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
          ? <img src={product.image_url} alt={product.name} className="routine-img" onError={e => e.target.style.display = 'none'} />
          : <span className="routine-img-placeholder"></span>}
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

/* ═══════════════════════════════
   Brand Dropdown Filter
═══════════════════════════════ */
const POPULAR_BRANDS = [
  'CeraVe','The Ordinary','La Roche-Posay','Neutrogena','Cetaphil',
  "Paula's Choice",'COSRX','Some By Mi','Innisfree','Skinfood',
  'Acnevon','Kesh','Nivea','Eucerin','Bioderma',
  'Vichy','Garnier','Olay','Clinique','Estee Lauder',
];

const BrandDropdown = ({ brandList, brandFilter, allPool, dismissedIdxs, onToggle, onClear }) => {
  const [open, setOpen] = React.useState(false);
  const selectedCount = brandFilter.length;

  return (
    <div style={{ position: 'relative', marginBottom: '14px' }}>
      <button onClick={() => setOpen(v => !v)} style={{
        display: 'flex', alignItems: 'center', gap: '8px',
        padding: '9px 16px', borderRadius: '12px', cursor: 'pointer',
        fontFamily: "'Kanit', sans-serif", fontSize: '13px', fontWeight: '700',
        border: selectedCount > 0 ? '1.5px solid #6366F1' : '1.5px solid var(--border)',
        background: selectedCount > 0 ? 'var(--accent-light)' : 'var(--bg-card)',
        color: selectedCount > 0 ? 'var(--accent-text)' : 'var(--text-secondary)',
        transition: 'all 0.15s', width: '100%', justifyContent: 'space-between',
      }}>
        <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          กรองตามแบรนด์
          {selectedCount > 0 && (
            <span style={{ background: '#6366F1', color: 'white', borderRadius: '20px', padding: '1px 8px', fontSize: '11px', fontWeight: '800' }}>{selectedCount}</span>
          )}
        </span>
        <span style={{ fontSize: '11px', opacity: 0.6, transform: open ? 'rotate(180deg)' : 'none', transition: 'transform 0.2s', display: 'inline-block' }}>▼</span>
      </button>

      {selectedCount > 0 && !open && (
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '5px', marginTop: '8px' }}>
          {brandFilter.map(b => (
            <span key={b} style={{
              display: 'inline-flex', alignItems: 'center', gap: '4px',
              background: 'linear-gradient(135deg,#6366F1,#8B5CF6)', color: 'white',
              padding: '3px 10px', borderRadius: '20px', fontSize: '11px', fontWeight: '700',
            }}>
              {b}
              <button onClick={(e) => { e.stopPropagation(); onToggle(b); }} style={{ background: 'none', border: 'none', color: 'white', cursor: 'pointer', padding: '0', fontSize: '13px', lineHeight: 1, opacity: 0.8 }}>×</button>
            </span>
          ))}
          <button onClick={onClear} style={{ background: 'none', border: '1px solid #FCA5A5', color: '#EF4444', borderRadius: '20px', padding: '3px 10px', fontSize: '11px', fontWeight: '700', cursor: 'pointer', fontFamily: "'Kanit', sans-serif" }}>ล้างทั้งหมด</button>
        </div>
      )}

      {open && (
        <div style={{
          position: 'absolute', top: 'calc(100% + 6px)', left: 0, right: 0,
          background: 'var(--bg-card)', border: '1px solid var(--border)',
          borderRadius: '14px', padding: '14px 16px',
          boxShadow: 'var(--shadow-md)', zIndex: 100,
          maxHeight: '320px', overflowY: 'auto',
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
            <span style={{ fontSize: '11px', fontWeight: '800', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.5px' }}>เลือกได้หลายแบรนด์</span>
            <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
              {selectedCount > 0 && (<button onClick={onClear} style={{ background: 'none', border: 'none', color: '#EF4444', fontSize: '11px', fontWeight: '700', cursor: 'pointer', fontFamily: "'Kanit', sans-serif" }}>✕ ล้างทั้งหมด</button>)}
              <button onClick={() => setOpen(false)} style={{ background: 'none', border: 'none', color: 'var(--text-muted)', fontSize: '16px', cursor: 'pointer', lineHeight: 1, padding: '0' }}>×</button>
            </div>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
            {brandList.map(brand => {
              const active    = brandFilter.includes(brand);
              const isPopular = POPULAR_BRANDS.some(p => brand.toLowerCase().includes(p.toLowerCase()));
              const count     = allPool.filter(p => !dismissedIdxs.includes(p._poolIdx) && p.brand === brand).length;
              return (
                <button key={brand} onClick={() => onToggle(brand)} style={{
                  display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                  padding: '8px 12px', borderRadius: '10px', cursor: 'pointer',
                  fontFamily: "'Kanit', sans-serif", fontSize: '13px',
                  fontWeight: active ? '700' : isPopular ? '600' : '500',
                  border: 'none', textAlign: 'left',
                  background: active ? 'linear-gradient(135deg,rgba(99,102,241,0.15),rgba(139,92,246,0.15))' : 'transparent',
                  color: active ? 'var(--accent-text)' : 'var(--text-primary)',
                  transition: 'background 0.12s',
                }}
                  onMouseEnter={e => { if (!active) e.currentTarget.style.background = 'var(--bg-subtle)'; }}
                  onMouseLeave={e => { if (!active) e.currentTarget.style.background = 'transparent'; }}
                >
                  <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <span style={{ width: '16px', height: '16px', borderRadius: '4px', border: active ? '2px solid #6366F1' : '2px solid var(--border)', background: active ? '#6366F1' : 'transparent', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0, transition: 'all 0.12s' }}>
                      {active && <span style={{ color: 'white', fontSize: '10px', fontWeight: '900' }}>✓</span>}
                    </span>
                    {brand}
                  </span>
                  <span style={{ fontSize: '11px', color: 'var(--text-muted)', background: 'var(--bg-subtle)', padding: '1px 7px', borderRadius: '20px', fontWeight: '600' }}>{count}</span>
                </button>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
};

/* ═══════════════════════════════
   MAIN StepResults
═══════════════════════════════ */
const StepResults = ({ recommend, routine, user, onRestart, summary }) => {
  const email    = user?.email || null;
  const userName = user?.name  || '';
  const routineList = Array.isArray(routine) ? routine : [];

  const allPool = useMemo(() => {
    const raw = Array.isArray(recommend) ? recommend : [];
    return raw.map((p, i) => ({ ...p, _poolIdx: i }));
  }, [recommend]);

  const [dismissedIdxs, setDismissedIdxs] = useState([]);
  const [currentPage,   setCurrentPage]   = useState(1);
  const [brandFilter,   setBrandFilter]   = useState([]);

  const brandList = useMemo(() => {
    const brands  = [...new Set(allPool.map(p => p.brand).filter(Boolean))];
    const popular = brands.filter(b => POPULAR_BRANDS.some(p => b.toLowerCase().includes(p.toLowerCase()))).sort();
    const others  = brands.filter(b => !POPULAR_BRANDS.some(p => b.toLowerCase().includes(p.toLowerCase()))).sort();
    return [...popular, ...others];
  }, [allPool]);

  const visiblePool = useMemo(() => {
    let pool = allPool.filter(p => !dismissedIdxs.includes(p._poolIdx));
    if (brandFilter.length > 0) pool = pool.filter(p => brandFilter.includes(p.brand));
    return pool;
  }, [allPool, dismissedIdxs, brandFilter]);

  const totalPages = Math.max(1, Math.ceil(visiblePool.length / PAGE_SIZE));
  const safePage   = Math.min(currentPage, totalPages);
  const pageStart  = (safePage - 1) * PAGE_SIZE;
  const pageItems  = visiblePool.slice(pageStart, pageStart + PAGE_SIZE);

  const handleDismiss = (poolIdx) => {
    setDismissedIdxs(prev => {
      const next         = [...prev, poolIdx];
      const newVisible   = allPool.filter(p => !next.includes(p._poolIdx));
      const newTotal     = Math.max(1, Math.ceil(newVisible.length / PAGE_SIZE));
      if (currentPage > newTotal) setCurrentPage(newTotal);
      return next;
    });
  };

  const handlePage = (p) => { setCurrentPage(p); window.scrollTo({ top: 0, behavior: 'smooth' }); };
  const toggleBrand = (brand) => { setCurrentPage(1); setBrandFilter(prev => prev.includes(brand) ? prev.filter(b => b !== brand) : [...prev, brand]); };
  const clearBrands = () => { setBrandFilter([]); setCurrentPage(1); };

  const totalDismissed = dismissedIdxs.length;

  return (
    <div className="step-content fadeIn">

      <SummaryBar summary={summary} />

      <SectionHeader
        icon=""
        title="สินค้าที่เหมาะกับคุณ"
        subtitle={
          brandFilter.length > 0
            ? `กรองแบรนด์: ${brandFilter.join(', ')} • ${visiblePool.length} รายการ`
            : totalDismissed > 0
              ? `เหลือ ${visiblePool.length} / ${allPool.length} รายการ • ลบออกแล้ว ${totalDismissed} • กด × ถ้าไม่ชอบ`
              : `${allPool.length} รายการที่ match กับสภาพผิวของคุณ เรียงจาก match มากไปน้อย • กด × เพื่อเอาออก`
        }
      />

      {brandList.length > 1 && (
        <BrandDropdown
          brandList={brandList}
          brandFilter={brandFilter}
          allPool={allPool}
          dismissedIdxs={dismissedIdxs}
          onToggle={toggleBrand}
          onClear={clearBrands}
        />
      )}

      {allPool.length > 0 && (
        <div style={{
          display: 'flex', alignItems: 'center', gap: '10px',
          marginBottom: '16px', padding: '10px 16px',
          background: 'var(--bg-card)', borderRadius: '12px',
          border: '1px solid var(--border)', fontSize: '13px',
          color: 'var(--text-secondary)', flexWrap: 'wrap',
        }}>
          <span style={{ fontWeight: '700', color: 'var(--text-primary)', whiteSpace: 'nowrap' }}>หน้า {safePage} / {totalPages}</span>
          <span style={{ whiteSpace: 'nowrap' }}>(แสดง {visiblePool.length > 0 ? pageStart + 1 : 0}–{Math.min(pageStart + PAGE_SIZE, visiblePool.length)} จาก {visiblePool.length} รายการ)</span>
          <div style={{ flex: 1, minWidth: '80px', height: '6px', background: 'var(--bg-subtle)', borderRadius: '10px', overflow: 'hidden' }}>
            <div style={{ height: '100%', width: allPool.length > 0 ? `${(totalDismissed / allPool.length) * 100}%` : '0%', background: 'linear-gradient(90deg, #EF4444, #F97316)', borderRadius: '10px', transition: 'width 0.4s ease' }} />
          </div>
          {totalDismissed > 0 && (
            <span style={{ background: '#FEF2F2', color: '#EF4444', padding: '2px 9px', borderRadius: '20px', fontSize: '11px', fontWeight: '700', whiteSpace: 'nowrap' }}>ลบออก {totalDismissed}</span>
          )}
        </div>
      )}

      {visiblePool.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '48px 24px', background: 'var(--bg-card)', borderRadius: '20px', border: '2px dashed var(--border)', marginBottom: '40px' }}>
          <div style={{ fontSize: '52px', marginBottom: '14px' }}>{'🔍'}</div>
          <h3 style={{ color: 'var(--text-primary)', margin: '0 0 8px', fontSize: '18px' }}>{brandFilter.length > 0 ? 'ไม่พบสินค้าของแบรนด์นี้' : 'ดูครบทุกตัวแล้ว!'}</h3>
          <p style={{ color: 'var(--text-secondary)', margin: '0 0 22px', fontSize: '14px' }}>{brandFilter.length > 0 ? 'ลองเลือกแบรนด์อื่น หรือล้าง filter' : 'ลองปรับเงื่อนไขแล้ววิเคราะห์ใหม่'}</p>
          <div style={{ display: 'flex', gap: '10px', justifyContent: 'center' }}>
            {brandFilter.length > 0 && (
              <button onClick={clearBrands} style={{ padding: '11px 28px', borderRadius: '12px', border: '2px solid var(--border-focus)', background: 'var(--bg-card)', color: 'var(--accent-text)', fontSize: '14px', fontWeight: '700', cursor: 'pointer', fontFamily: "'Kanit', sans-serif" }}>✕ ล้าง filter</button>
            )}
            <button onClick={onRestart} style={{ padding: '11px 28px', borderRadius: '12px', border: 'none', background: 'linear-gradient(135deg, #4F46E5, #8B5CF6)', color: 'white', fontSize: '14px', fontWeight: '700', cursor: 'pointer', fontFamily: "'Kanit', sans-serif" }}>🔄 วิเคราะห์ใหม่</button>
          </div>
        </div>
      ) : (
        <>
          <div className="results-grid results-grid-mb">
            {pageItems.map((product) => (
              <ProductCard
                key={product._poolIdx}
                product={product}
                email={email}
                userName={userName}
                rank={product._poolIdx + 1}
                matchPercent={Math.min(
                  Math.round((parseFloat(product.final_score) || 0) * 100),
                  99
                )}
                onDismiss={() => handleDismiss(product._poolIdx)}
                userSkinType={summary?.skinType || ''}
              />
            ))}
          </div>

          <PaginationBar currentPage={safePage} totalPages={totalPages} onPage={handlePage} />

          <p style={{ textAlign: 'center', fontSize: '12px', color: 'var(--text-muted)', margin: '8px 0 32px' }}>
            หน้า {safePage} จาก {totalPages} • {visiblePool.length} รายการ
            {brandFilter.length > 0 && ` (กรองแบรนด์: ${brandFilter.join(', ')})`}
          </p>
        </>
      )}

      <div className="results-divider" />

      <SectionHeader icon="" title="Skincare Routine ของคุณ" subtitle="เรียงตามลำดับการใช้งาน step 1 → 5" />

      {routineList.length > 0 ? (
        <div className="routine-list">
          {routineList.map((product, i) => <RoutineCard key={i} product={product} email={email} />)}
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