import React, { useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import BookmarkButton from '../components/Reviews/BookmarkButton';
import ReviewButton   from '../components/Reviews/ReviewButton';
import ProductReviews from '../components/Reviews/ProductReviews';
import './SearchPage.css';

const API = import.meta.env.VITE_API_URL || 'http://127.0.0.1:5000/api';

const CATEGORY_OPTIONS = [
  { value: 'all',         label: 'ทุกประเภท' },
  { value: 'cleanser',    label: 'คลีนเซอร์' },
  { value: 'cleansing',   label: 'คลีนซิ่ง' },
  { value: 'toner',       label: 'โทนเนอร์' },
  { value: 'serum',       label: 'เซรั่ม' },
  { value: 'moisturizer', label: 'มอยส์เจอไรเซอร์' },
  { value: 'sunscreen',   label: 'กันแดด' },
  { value: 'mask',        label: 'มาส์ก' },
  { value: 'eye_care',    label: 'ครีมตา' },
];

const SKINTYPE_OPTIONS = [
  { value: 'all',         label: 'ทุกสภาพผิว' },
  { value: 'oily',        label: 'ผิวมัน' },
  { value: 'dry',         label: 'ผิวแห้ง' },
  { value: 'sensitive',   label: 'ผิวแพ้ง่าย' },
  { value: 'normal',      label: 'ผิวธรรมดา' },
  { value: 'combination', label: 'ผิวผสม' },
];

const PRICE_OPTIONS = [
  { value: 'all',  label: 'ทุกราคา',          min: 0,    max: 999999 },
  { value: 'low',  label: 'ไม่เกิน ฿500',   min: 0,    max: 500 },
  { value: 'mid',  label: '฿500–1,500',     min: 500,  max: 1500 },
  { value: 'high', label: '฿1,500 ขึ้นไป',  min: 1500, max: 999999 },
];

// ── แบรนด์ยอดนิยม แบ่งตาม tier ──
const POPULAR_BRANDS = [
  // 🔥 Top tier — เป็นที่รู้จักมากที่สุด
  {
    tier: 'top',
    label: 'แบรนด์ฮิตติดชาร์ต',
    brands: [
      { label: 'CeraVe',         value: 'CeraVe',         desc: 'Ceramide + Hyaluronic' },
      { label: 'The Ordinary',   value: 'The Ordinary',   desc: 'Active ingredients ราคาดี' },
      { label: 'La Roche-Posay', value: 'La Roche-Posay', desc: 'Sensitive skin specialist' },
      { label: 'COSRX',          value: 'COSRX',          desc: 'K-beauty สิวและผิวแพ้' },
      { label: 'Neutrogena',     value: 'Neutrogena',     desc: 'Dermatologist recommended' },
      { label: "Paula's Choice", value: "Paula's Choice",  desc: 'BHA/Retinol expert' },
    ],
  },
  // ⭐ Popular — ได้รับความนิยมสูง
  {
    tier: 'popular',
    label: 'ยอดนิยมในไทย',
    brands: [
      { label: 'Cetaphil',    value: 'Cetaphil',    desc: 'Gentle สำหรับผิวแพ้ง่าย' },
      { label: 'Bioderma',    value: 'Bioderma',    desc: 'Micellar water ชื่อดัง' },
      { label: 'Eucerin',     value: 'Eucerin',     desc: 'Medical skincare' },
      { label: 'Vichy',       value: 'Vichy',       desc: 'Thermal water จากฝรั่งเศส' },
      { label: 'Some By Mi',  value: 'Some By Mi',  desc: 'AHA/BHA/PHA K-beauty' },
      { label: 'Innisfree',   value: 'Innisfree',   desc: 'Natural K-beauty จากเกาะเชจู' },
      { label: 'Acnevon',     value: 'Acnevon',     desc: 'แบรนด์ไทย เน้นสิว' },
      { label: 'Kesh',        value: 'Kesh',        desc: 'แบรนด์ไทย ราคาเข้าถึงได้' },
    ],
  },
  // 💎 Premium
  {
    tier: 'premium',
    label: 'พรีเมียม',
    brands: [
      { label: 'Clinique',      value: 'Clinique',      desc: 'Allergy tested' },
      { label: 'Estee Lauder',  value: 'Estee Lauder',  desc: 'Luxury skincare' },
      { label: 'SK-II',         value: 'SK-II',         desc: 'Pitera essence' },
      { label: 'Sulwhasoo',     value: 'Sulwhasoo',     desc: 'K-beauty high-end' },
    ],
  },
];

const QUICK_TAGS = [
  { group: 'ประเภทสินค้า', tags: [
    { label: 'มอยส์เจอไรเซอร์', value: 'moisturizer' },
    { label: 'เซรั่ม',           value: 'serum' },
    { label: 'คลีนเซอร์',        value: 'cleanser' },
    { label: 'กันแดด',           value: 'sunscreen' },
    { label: 'โทนเนอร์',         value: 'toner' },
    { label: 'มาส์ก',            value: 'mask' },
  ]},
  { group: 'ส่วนผสมยอดนิยม', tags: [
    { label: 'Niacinamide',     value: 'niacinamide' },
    { label: 'Hyaluronic Acid', value: 'hyaluronic' },
    { label: 'Retinol',         value: 'retinol' },
    { label: 'Ceramide',        value: 'ceramide' },
    { label: 'Salicylic Acid',  value: 'salicylic' },
    { label: 'Vitamin C',       value: 'ascorbic' },
  ]},
];

const TIER_STYLE = {
  top: {
    headerBg:   'linear-gradient(135deg, #FF6B6B, #FF8E53)',
    chipBg:     'linear-gradient(135deg, #FF6B6B, #FF8E53)',
    chipBorder: '#FF6B6B',
    chipColor:  'white',
    idleBg:     'rgba(255,107,107,0.08)',
    idleBorder: 'rgba(255,107,107,0.35)',
    idleColor:  '#CC4444',
  },
  popular: {
    headerBg:   'linear-gradient(135deg, #6366F1, #8B5CF6)',
    chipBg:     'linear-gradient(135deg, #6366F1, #8B5CF6)',
    chipBorder: '#6366F1',
    chipColor:  'white',
    idleBg:     'var(--accent-light)',
    idleBorder: 'rgba(99,102,241,0.4)',
    idleColor:  'var(--accent-text)',
  },
  premium: {
    headerBg:   'linear-gradient(135deg, #D4A017, #F5C842)',
    chipBg:     'linear-gradient(135deg, #D4A017, #F5C842)',
    chipBorder: '#D4A017',
    chipColor:  'white',
    idleBg:     'rgba(212,160,23,0.08)',
    idleBorder: 'rgba(212,160,23,0.4)',
    idleColor:  '#9A7000',
  },
};

const getCategoryLabel = (cat) =>
  CATEGORY_OPTIONS.find(c => c.value === cat)?.label || cat || '-';

const SearchPage = ({ user, compareList, setCompareList }) => {
  const [query, setQuery]           = useState('');
  const [results, setResults]       = useState([]);
  const [filtered, setFiltered]     = useState([]);
  const [loading, setLoading]       = useState(false);
  const [searched, setSearched]     = useState(false);
  const [showFilter, setShowFilter] = useState(false);
  const [skintypeFilter, setSkintypeFilter] = useState('all');
  const [priceFilter,    setPriceFilter]    = useState('all');
  const navigate = useNavigate();

  const compare = compareList || [];

  const toggleCompare = (product) => {
    const isIn = compare.some(p => p.name === product.name);
    if (isIn) {
      setCompareList(compare.filter(p => p.name !== product.name));
    } else {
      if (compare.length >= 4) return;
      setCompareList([...compare, product]);
    }
  };

  const applyFilters = useCallback((data, skin, price) => {
    const priceOpt = PRICE_OPTIONS.find(p => p.value === price) || PRICE_OPTIONS[0];
    return data.filter(p => {
      const matchSkin  = skin === 'all' || (p.skintype || '').toLowerCase().includes(skin);
      const matchPrice = !p.price || (parseInt(p.price) >= priceOpt.min && parseInt(p.price) <= priceOpt.max);
      return matchSkin && matchPrice;
    });
  }, []);

  const handleSearch = useCallback(async (overrideQuery) => {
    const trimmed = (overrideQuery !== undefined ? overrideQuery : query).trim();
    if (!trimmed) return;
    setQuery(trimmed); setLoading(true); setSearched(true);
    try {
      const res  = await fetch(`${API}/search?q=${encodeURIComponent(trimmed)}`);
      const data = await res.json();
      const list = Array.isArray(data) ? data : [];
      setResults(list);
      setFiltered(applyFilters(list, skintypeFilter, priceFilter));
    } catch { setResults([]); setFiltered([]); }
    finally { setLoading(false); }
  }, [query, skintypeFilter, priceFilter, applyFilters]);

  const handleFilterChange = (type, value) => {
    const newSkin  = type === 'skin'  ? value : skintypeFilter;
    const newPrice = type === 'price' ? value : priceFilter;
    setSkintypeFilter(newSkin);
    setPriceFilter(newPrice);
    if (results.length > 0) {
      setFiltered(applyFilters(results, newSkin, newPrice));
    } else if (type === 'cat' && value !== 'all') {
      handleSearch(value);
    }
  };

  const handleClear = () => {
    setSearched(false); setQuery(''); setResults([]); setFiltered([]);
  };

  const activeFilterCount = [skintypeFilter, priceFilter].filter(v => v !== 'all').length;

  return (
    <div className="search-page">
      <div className="search-inner">

        <div className="search-header">
          <h1>🔍 ค้นหาสินค้า</h1>
          <p>พิมพ์ชื่อสินค้า แบรนด์ หรือส่วนผสมที่ต้องการ</p>
        </div>

        {/* ── Search box ── */}
        <div className="search-box-row">
          <input className="search-input" type="text" value={query}
            onChange={e => setQuery(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && handleSearch()}
            placeholder="เช่น CeraVe, serum, niacinamide..."
            autoFocus
          />
          <button className="search-btn"
            onClick={() => handleSearch()}
            disabled={loading || !query.trim()}>
            {loading ? '⏳' : 'ค้นหา'}
          </button>
          <button
            className={`filter-toggle-btn ${activeFilterCount > 0 ? 'active' : ''}`}
            onClick={() => setShowFilter(v => !v)}>
            🏷️ {activeFilterCount > 0 ? `Filter (${activeFilterCount})` : 'Filter'}
          </button>
        </div>

        {/* ── Filter panel ── */}
        {showFilter && (
          <div className="filter-panel">
            <div className="filter-group">
              <p className="filter-group-label">สภาพผิว</p>
              <div className="filter-pills">
                {SKINTYPE_OPTIONS.map(opt => (
                  <button key={opt.value}
                    className={`filter-pill ${skintypeFilter === opt.value ? 'active' : ''}`}
                    onClick={() => handleFilterChange('skin', opt.value)}>{opt.label}</button>
                ))}
              </div>
            </div>
            <div className="filter-group">
              <p className="filter-group-label">ช่วงราคา</p>
              <div className="filter-pills">
                {PRICE_OPTIONS.map(opt => (
                  <button key={opt.value}
                    className={`filter-pill ${priceFilter === opt.value ? 'active' : ''}`}
                    onClick={() => handleFilterChange('price', opt.value)}>{opt.label}</button>
                ))}
              </div>
            </div>
            {activeFilterCount > 0 && (
              <button className="filter-reset-btn" onClick={() => {
                setSkintypeFilter('all'); setPriceFilter('all');
                setFiltered(results);
              }}>✕ ล้าง filter ทั้งหมด</button>
            )}
          </div>
        )}

        {/* ── Quick tags + Popular brands (ก่อน search) ── */}
        {!searched && (
          <>
            {/* Popular brands section */}
            <div style={{
              background: 'var(--bg-card)', borderRadius: '16px',
              padding: '20px', border: '1px solid var(--border)',
              marginBottom: '16px',
            }}>
              <p style={{
                color: 'var(--text-primary)', fontSize: '15px',
                margin: '0 0 16px', fontWeight: '800',
                display: 'flex', alignItems: 'center', gap: '6px',
              }}>
                แบรนด์ยอดนิยม
                <span style={{
                  fontSize: '11px', fontWeight: '500',
                  color: 'var(--text-muted)', marginLeft: '2px',
                }}>กดเพื่อค้นหา</span>
              </p>

              {POPULAR_BRANDS.map((group) => {
                const st = TIER_STYLE[group.tier];
                return (
                  <div key={group.tier} style={{ marginBottom: '16px' }}>
                    {/* tier header */}
                    <div style={{
                      display: 'inline-flex', alignItems: 'center',
                      background: st.headerBg,
                      color: 'white', padding: '3px 12px',
                      borderRadius: '20px', fontSize: '11px', fontWeight: '800',
                      marginBottom: '10px', letterSpacing: '0.3px',
                    }}>
                      {group.label}
                    </div>

                    {/* brand chips */}
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                      {group.brands.map(brand => (
                        <button
                          key={brand.value}
                          onClick={() => handleSearch(brand.value)}
                          title={brand.desc}
                          style={{
                            display: 'flex', flexDirection: 'column',
                            alignItems: 'flex-start',
                            padding: '8px 14px', borderRadius: '12px',
                            border: `1.5px solid ${st.idleBorder}`,
                            background: st.idleBg,
                            color: st.idleColor,
                            cursor: 'pointer',
                            fontFamily: "'Kanit', sans-serif",
                            transition: 'all 0.15s',
                            textAlign: 'left',
                          }}
                          onMouseEnter={e => Object.assign(e.currentTarget.style, {
                            background: st.chipBg,
                            color: st.chipColor,
                            borderColor: st.chipBorder,
                            transform: 'translateY(-2px)',
                            boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
                          })}
                          onMouseLeave={e => Object.assign(e.currentTarget.style, {
                            background: st.idleBg,
                            color: st.idleColor,
                            borderColor: st.idleBorder,
                            transform: 'none',
                            boxShadow: 'none',
                          })}
                        >
                          <span style={{ fontSize: '13px', fontWeight: '700' }}>
                            {brand.label}
                          </span>
                          <span style={{
                            fontSize: '10px', opacity: 0.7,
                            fontWeight: '400', marginTop: '1px',
                          }}>
                            {brand.desc}
                          </span>
                        </button>
                      ))}
                    </div>
                  </div>
                );
              })}
            </div>

            {/* Quick tags */}
            <div className="quick-tags-panel">
              <p className="quick-tags-title">ลองค้นหาด้วย...</p>
              {QUICK_TAGS.map((group, gi) => (
                <div key={gi} className="quick-tag-group">
                  <p className="quick-tag-group-label">{group.group}</p>
                  <div className="quick-tag-pills">
                    {group.tags.map((tag, ti) => (
                      <button key={ti}
                        className={`quick-tag-btn ${query === tag.value ? 'active' : ''}`}
                        onClick={() => handleSearch(tag.value)}>{tag.label}</button>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </>
        )}

        {/* ── Loading ── */}
        {loading && (
          <div className="search-loading">
            <div style={{ fontSize: '32px', marginBottom: '8px' }}></div>
            <p>กำลังค้นหา...</p>
          </div>
        )}

        {/* ── Empty ── */}
        {!loading && searched && filtered.length === 0 && (
          <div className="search-empty">
            <div style={{ fontSize: '40px', marginBottom: '8px' }}></div>
            <h3>{results.length > 0 ? 'ไม่มีสินค้าที่ตรง filter' : 'ไม่พบสินค้าที่ตรงกัน'}</h3>
            <p>{results.length > 0
              ? `มีสินค้า ${results.length} รายการ แต่ไม่ผ่าน filter`
              : 'ลองพิมพ์คำค้นหาอื่น'}</p>
            <button className="back-btn" style={{ marginTop: '12px' }} onClick={handleClear}>
              ล้างทั้งหมด
            </button>
          </div>
        )}

        {/* ── Results ── */}
        {!loading && filtered.length > 0 && (
          <div>
            <div className="result-meta-row">
              <p className="result-meta-text">
                แสดง <strong>{filtered.length}</strong>
                {filtered.length !== results.length && ` / ${results.length}`} รายการ
                {query && <> สำหรับ "<strong>{query}</strong>"</>}
              </p>
              <button className="clear-btn" onClick={handleClear}>ล้างผล</button>
            </div>

            <div className="search-product-list">
              {filtered.map((product, index) => {
                const inCompare = compare.some(p => p.name === product.name);
                return (
                  <div key={index} className="search-product-card">
                    <div className="product-img-box">
                      {product.image_url
                        ? <img src={product.image_url} alt={product.name}
                            onError={e => e.target.style.display = 'none'} />
                        : <span style={{ fontSize: '24px' }}></span>}
                    </div>
                    <div className="product-info">
                      <div className="product-brand-label">{product.brand}</div>
                      <div className="product-name-label">{product.name}</div>
                      <div className="product-tags">
                        <span className="product-tag-cat">
                          {getCategoryLabel(product.major_category)}
                        </span>
                        <span className="product-tag-skin">
                          {product.skintype || 'all skin'}
                        </span>
                      </div>
                    </div>
                    <div className="product-price-col">
                      <div className="product-price">
                        ฿{product.price ? parseInt(product.price).toLocaleString() : '-'}
                      </div>
                      <BookmarkButton product={product} email={user?.email || null} />
                      <ReviewButton   product={product} email={user?.email || null}
                        userName={user?.name} />
                      <button
                        className={`compare-btn ${inCompare ? 'active' : ''}`}
                        onClick={() => toggleCompare(product)}
                        disabled={!inCompare && compare.length >= 4}
                        title={inCompare ? 'ยกเลิกเปรียบเทียบ' : compare.length >= 4 ? 'เต็มแล้ว' : 'เพิ่มเพื่อเปรียบเทียบ'}>
                        {inCompare ? '✓ เปรียบเทียบ' : 'เปรียบเทียบ'}
                      </button>
                    </div>
                    <ProductReviews productName={product.name} />
                  </div>
                );
              })}
            </div>
          </div>
        )}

        <div className="search-back-row">
          <button className="back-btn" onClick={() => navigate('/advisor')}>
            ← กลับหน้าวิเคราะห์ผิว
          </button>
        </div>

      </div>

      {/* ── Floating compare bar ── */}
      {compare.length > 0 && (
        <div className="compare-bar">
          <span className="compare-bar-count">{compare.length}/4</span>
          <span className="compare-bar-text">สินค้าที่เลือก</span>
          <div className="compare-bar-thumbs">
            {compare.map((p, i) => (
              <div key={i} className="compare-bar-thumb"
                title={p.name} onClick={() => toggleCompare(p)}>
                {p.image_url
                  ? <img src={p.image_url} alt={p.name}
                      onError={e => e.target.style.display='none'} />
                  : ''}
              </div>
            ))}
          </div>
          <button className="compare-bar-go" onClick={() => navigate('/compare')}>
            เปรียบเทียบเลย
          </button>
          <button className="compare-bar-clear"
            onClick={() => setCompareList([])} title="ล้างทั้งหมด">×</button>
        </div>
      )}

    </div>
  );
};

export default SearchPage;