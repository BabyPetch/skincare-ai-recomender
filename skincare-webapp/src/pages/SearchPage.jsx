import React, { useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import BookmarkButton from '../components/Reviews/BookmarkButton';
import ReviewButton   from '../components/Reviews/ReviewButton';
import ProductReviews from '../components/Reviews/ProductReviews';
import './SearchPage.css';

const API = 'http://127.0.0.1:5000/api';

const CATEGORY_OPTIONS = [
  { value: 'all',         label: 'ทุกประเภท' },
  { value: 'cleanser',    label: '🧼 คลีนเซอร์' },
  { value: 'cleansing',   label: '🫧 คลีนซิ่ง' },   // ← เพิ่ม
  { value: 'toner',       label: '💦 โทนเนอร์' },
  { value: 'serum',       label: '✨ เซรั่ม' },
  { value: 'moisturizer', label: '🔒 มอยส์เจอไรเซอร์' },
  { value: 'sunscreen',   label: '☀️ กันแดด' },
  { value: 'mask',        label: '🎭 มาส์ก' },
  { value: 'eye_care',    label: '👁️ ครีมตา' },

];

const SKINTYPE_OPTIONS = [
  { value: 'all',         label: 'ทุกสภาพผิว' },
  { value: 'oily',        label: '💧 ผิวมัน' },
  { value: 'dry',         label: '🌵 ผิวแห้ง' },
  { value: 'sensitive',   label: '🌸 ผิวแพ้ง่าย' },
  { value: 'normal',      label: '✅ ผิวธรรมดา' },
  { value: 'combination', label: '☯️ ผิวผสม' },
];

const PRICE_OPTIONS = [
  { value: 'all',  label: 'ทุกราคา',          min: 0,    max: 999999 },
  { value: 'low',  label: '💚 ไม่เกิน ฿500',   min: 0,    max: 500 },
  { value: 'mid',  label: '💛 ฿500–1,500',     min: 500,  max: 1500 },
  { value: 'high', label: '🧡 ฿1,500 ขึ้นไป',  min: 1500, max: 999999 },
];

const QUICK_TAGS = [
  { group: '📦 ประเภทสินค้า', tags: [
    { label: 'มอยส์เจอไรเซอร์', value: 'moisturizer' },
    { label: 'เซรั่ม',           value: 'serum' },
    { label: 'คลีนเซอร์',        value: 'cleanser' },
    { label: 'กันแดด',           value: 'sunscreen' },
    { label: 'โทนเนอร์',         value: 'toner' },
    { label: 'มาส์ก',            value: 'mask' },
  ]},
  { group: '🌿 ส่วนผสมยอดนิยม', tags: [
    { label: 'Niacinamide',     value: 'niacinamide' },
    { label: 'Hyaluronic Acid', value: 'hyaluronic' },
    { label: 'Retinol',         value: 'retinol' },
    { label: 'Ceramide',        value: 'ceramide' },
    { label: 'Salicylic Acid',  value: 'salicylic' },
    { label: 'Vitamin C',       value: 'ascorbic' },
  ]},
  { group: '✨ แบรนด์ยอดนิยม', tags: [
    { label: 'CeraVe',       value: 'CeraVe' },
    { label: 'The Ordinary', value: 'The Ordinary' },
    { label: 'Acnevon',      value: 'Acnevon' },
    { label: 'Kesh',         value: 'Kesh' },
  ]},
];

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

// แก้ handleSearch — ลบ catFilter ออก
  const handleSearch = useCallback(async (overrideQuery) => {
    const trimmed = (overrideQuery !== undefined ? overrideQuery : query).trim();
    if (!trimmed) return;
    setQuery(trimmed); setLoading(true); setSearched(true);
    try {
      const res  = await fetch(`${API}/search?q=${encodeURIComponent(trimmed)}`);
      const data = await res.json();
      const list = Array.isArray(data) ? data : [];
      setResults(list);
      setFiltered(applyFilters(list, skintypeFilter, priceFilter));  // ← ลบ catFilter
    } catch { setResults([]); setFiltered([]); }
    finally { setLoading(false); }
  }, [query, skintypeFilter, priceFilter, applyFilters]);  // ← ลบ catFilter

  const handleFilterChange = (type, value) => {
    const newSkin  = type === 'skin'  ? value : skintypeFilter;
    const newPrice = type === 'price' ? value : priceFilter;

    setSkintypeFilter(newSkin);
    setPriceFilter(newPrice);

    if (results.length > 0) {
      // มี results อยู่แล้ว → filter ทันที
      setFiltered(applyFilters(results, newSkin, newPrice));
    } else if (type === 'cat' && value !== 'all') {
      // ยังไม่ได้ search → auto search ด้วย category ที่กด
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

        {showFilter && (
          <div className="filter-panel">
            <div className="filter-group">
              <p className="filter-group-label">🌿 สภาพผิว</p>
              <div className="filter-pills">
                {SKINTYPE_OPTIONS.map(opt => (
                  <button key={opt.value}
                    className={`filter-pill ${skintypeFilter === opt.value ? 'active' : ''}`}
                    onClick={() => handleFilterChange('skin', opt.value)}>{opt.label}</button>
                ))}
              </div>
            </div>
            <div className="filter-group">
              <p className="filter-group-label">💰 ช่วงราคา</p>
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

        {!searched && (
          <div className="quick-tags-panel">
            <p className="quick-tags-title">💡 ลองค้นหาด้วย...</p>
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
        )}

        {loading && (
          <div className="search-loading">
            <div style={{ fontSize: '32px', marginBottom: '8px' }}>⏳</div>
            <p>กำลังค้นหา...</p>
          </div>
        )}

        {!loading && searched && filtered.length === 0 && (
          <div className="search-empty">
            <div style={{ fontSize: '40px', marginBottom: '8px' }}>🤔</div>
            <h3>{results.length > 0 ? 'ไม่มีสินค้าที่ตรง filter' : 'ไม่พบสินค้าที่ตรงกัน'}</h3>
            <p>{results.length > 0
              ? `มีสินค้า ${results.length} รายการ แต่ไม่ผ่าน filter`
              : 'ลองพิมพ์คำค้นหาอื่น'}</p>
            <button className="back-btn" style={{ marginTop: '12px' }} onClick={handleClear}>
              ล้างทั้งหมด
            </button>
          </div>
        )}

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
                        : <span style={{ fontSize: '24px' }}>🧴</span>}
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
                      {/* ── ปุ่มเปรียบเทียบ ── */}
                      <button
                        className={`compare-btn ${inCompare ? 'active' : ''}`}
                        onClick={() => toggleCompare(product)}
                        disabled={!inCompare && compare.length >= 4}
                        title={inCompare
                          ? 'ยกเลิกเปรียบเทียบ'
                          : compare.length >= 4
                            ? 'เต็มแล้ว (สูงสุด 4 รายการ)'
                            : 'เพิ่มเพื่อเปรียบเทียบ'}>
                        {inCompare ? '✓ เปรียบเทียบ' : '⚖️ เปรียบเทียบ'}
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
                title={p.name}
                onClick={() => toggleCompare(p)}>
                {p.image_url
                  ? <img src={p.image_url} alt={p.name}
                      onError={e => e.target.style.display='none'} />
                  : '🧴'}
              </div>
            ))}
          </div>
          <button className="compare-bar-go" onClick={() => navigate('/compare')}>
            ⚖️ เปรียบเทียบเลย
          </button>
          <button className="compare-bar-clear"
            onClick={() => setCompareList([])}
            title="ล้างทั้งหมด">×</button>
        </div>
      )}

    </div>
  );
};

export default SearchPage;