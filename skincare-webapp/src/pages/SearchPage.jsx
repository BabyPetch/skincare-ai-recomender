import React, { useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import BookmarkButton from '../components/BookmarkButton';

const API = 'http://127.0.0.1:5000/api';

const CATEGORY_OPTIONS = [
    { value: 'all',         label: 'ทุกประเภท' },
    { value: 'cleanser',    label: '🧼 คลีนเซอร์' },
    { value: 'toner',       label: '💦 โทนเนอร์' },
    { value: 'serum',       label: '✨ เซรั่ม' },
    { value: 'moisturizer', label: '🔒 มอยส์เจอไรเซอร์' },
    { value: 'sunscreen',   label: '☀️ กันแดด' },
    { value: 'mask',        label: '🎭 มาส์ก' },
    { value: 'exfoliator',  label: '🌀 เอ็กซ์โฟเลียเตอร์' },
    { value: 'eye_care',    label: '👁️ ครีมตา' },
    ];

    const SKINTYPE_OPTIONS = [
    { value: 'all',       label: 'ทุกสภาพผิว' },
    { value: 'oily',      label: '💧 ผิวมัน' },
    { value: 'dry',       label: '🌵 ผิวแห้ง' },
    { value: 'sensitive', label: '🌸 ผิวแพ้ง่าย' },
    { value: 'normal',    label: '✅ ผิวธรรมดา' },
    { value: 'combination', label: '☯️ ผิวผสม' },
    ];

    const PRICE_OPTIONS = [
    { value: 'all',    label: 'ทุกราคา',       min: 0,    max: 999999 },
    { value: 'low',    label: '💚 ไม่เกิน ฿500',  min: 0,    max: 500 },
    { value: 'mid',    label: '💛 ฿500–1,500',    min: 500,  max: 1500 },
    { value: 'high',   label: '🧡 ฿1,500 ขึ้นไป', min: 1500, max: 999999 },
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

    const getCategoryLabel = (cat) => CATEGORY_OPTIONS.find(c => c.value === cat)?.label || cat || '-';

    // ===== Filter Pill Button =====
    const Pill = ({ active, onClick, children }) => (
    <button onClick={onClick} style={{
        padding: '7px 14px', borderRadius: '20px', border: 'none',
        background: active ? 'linear-gradient(135deg, #4F46E5, #8B5CF6)' : '#F1F5F9',
        color: active ? 'white' : '#475569',
        fontWeight: active ? '700' : '500', fontSize: '13px',
        cursor: 'pointer', fontFamily: "'Kanit', sans-serif",
        transition: 'all 0.15s', whiteSpace: 'nowrap',
    }}
        onMouseEnter={e => { if (!active) { e.currentTarget.style.background = '#EEF2FF'; e.currentTarget.style.color = '#4F46E5'; }}}
        onMouseLeave={e => { if (!active) { e.currentTarget.style.background = '#F1F5F9'; e.currentTarget.style.color = '#475569'; }}}
    >
        {children}
    </button>
    );

    const SearchPage = ({ user }) => {
    const [query, setQuery]         = useState('');
    const [results, setResults]     = useState([]);
    const [filtered, setFiltered]   = useState([]);
    const [loading, setLoading]     = useState(false);
    const [searched, setSearched]   = useState(false);
    const [showFilter, setShowFilter] = useState(false);

    // Filter states
    const [catFilter,      setCatFilter]      = useState('all');
    const [skintypeFilter, setSkintypeFilter] = useState('all');
    const [priceFilter,    setPriceFilter]    = useState('all');

    const navigate = useNavigate();

    const applyFilters = useCallback((data, cat, skin, price) => {
        const priceOpt = PRICE_OPTIONS.find(p => p.value === price) || PRICE_OPTIONS[0];
        return data.filter(p => {
        const matchCat   = cat  === 'all' || p.major_category === cat;
        const matchSkin  = skin === 'all' || (p.skintype || '').toLowerCase().includes(skin);
        const matchPrice = !p.price || (parseInt(p.price) >= priceOpt.min && parseInt(p.price) <= priceOpt.max);
        return matchCat && matchSkin && matchPrice;
        });
    }, []);

    const handleSearch = useCallback(async (overrideQuery) => {
        const trimmed = (overrideQuery !== undefined ? overrideQuery : query).trim();
        if (!trimmed) return;
        setQuery(trimmed);
        setLoading(true);
        setSearched(true);
        try {
        const res  = await fetch(`${API}/search?q=${encodeURIComponent(trimmed)}`);
        const data = await res.json();
        const list = Array.isArray(data) ? data : [];
        setResults(list);
        setFiltered(applyFilters(list, catFilter, skintypeFilter, priceFilter));
        } catch (err) {
        console.error(err);
        setResults([]); setFiltered([]);
        } finally {
        setLoading(false);
        }
    }, [query, catFilter, skintypeFilter, priceFilter, applyFilters]);

    const handleFilterChange = (type, value) => {
        let newCat = catFilter, newSkin = skintypeFilter, newPrice = priceFilter;
        if (type === 'cat')   newCat   = value;
        if (type === 'skin')  newSkin  = value;
        if (type === 'price') newPrice = value;
        setCatFilter(newCat); setSkintypeFilter(newSkin); setPriceFilter(newPrice);
        setFiltered(applyFilters(results, newCat, newSkin, newPrice));
    };

    const handleClear = () => {
        setSearched(false); setQuery(''); setResults([]); setFiltered([]);
        setCatFilter('all'); setSkintypeFilter('all'); setPriceFilter('all');
    };

    const activeFilterCount = [catFilter, skintypeFilter, priceFilter].filter(v => v !== 'all').length;

    return (
        <div style={{ minHeight: '100vh', background: '#F8FAFC', padding: '40px 20px', fontFamily: "'Kanit', sans-serif" }}>
        <div style={{ maxWidth: '800px', margin: '0 auto' }}>

            {/* Header */}
            <div style={{ textAlign: 'center', marginBottom: '24px' }}>
            <h1 style={{ fontSize: '28px', fontWeight: 'bold', color: '#1E293B', margin: '0 0 6px' }}>🔍 ค้นหาสินค้า</h1>
            <p style={{ color: '#64748B', margin: 0 }}>พิมพ์ชื่อสินค้า แบรนด์ หรือส่วนผสมที่ต้องการ</p>
            </div>

            {/* Search Box */}
            <div style={{ display: 'flex', gap: '10px', marginBottom: '12px' }}>
            <input type="text" value={query} onChange={e => setQuery(e.target.value)}
                onKeyDown={e => e.key === 'Enter' && handleSearch()}
                placeholder="เช่น CeraVe, serum, niacinamide..."
                style={{ flex: 1, padding: '14px 18px', borderRadius: '12px',
                border: '2px solid #E2E8F0', fontSize: '16px',
                fontFamily: "'Kanit', sans-serif", outline: 'none' }}
                onFocus={e => e.target.style.borderColor = '#6366F1'}
                onBlur={e => e.target.style.borderColor = '#E2E8F0'}
                autoFocus
            />
            <button onClick={() => handleSearch()} disabled={loading || !query.trim()} style={{
                padding: '14px 22px', borderRadius: '12px', border: 'none',
                background: 'linear-gradient(135deg, #4F46E5, #8B5CF6)', color: 'white',
                fontSize: '15px', fontWeight: '600', fontFamily: "'Kanit', sans-serif",
                cursor: loading || !query.trim() ? 'not-allowed' : 'pointer',
                opacity: loading || !query.trim() ? 0.6 : 1,
            }}>
                {loading ? '⏳' : 'ค้นหา'}
            </button>
            {/* Filter Toggle */}
            <button onClick={() => setShowFilter(v => !v)} style={{
                padding: '14px 18px', borderRadius: '12px',
                border: `2px solid ${activeFilterCount > 0 ? '#6366F1' : '#E2E8F0'}`,
                background: activeFilterCount > 0 ? '#EEF2FF' : 'white',
                color: activeFilterCount > 0 ? '#4F46E5' : '#64748B',
                fontSize: '15px', cursor: 'pointer', fontFamily: "'Kanit', sans-serif",
                fontWeight: '600', position: 'relative',
            }}>
                🏷️ {activeFilterCount > 0 ? `Filter (${activeFilterCount})` : 'Filter'}
            </button>
            </div>

            {/* Filter Panel */}
            {showFilter && (
            <div style={{
                background: 'white', borderRadius: '16px', padding: '20px',
                border: '1px solid #E2E8F0', marginBottom: '16px',
                boxShadow: '0 4px 16px rgba(0,0,0,0.06)',
            }}>
                {/* Category */}
                <div style={{ marginBottom: '16px' }}>
                <p style={{ fontSize: '13px', color: '#94A3B8', margin: '0 0 8px', fontWeight: '700' }}>📦 ประเภทสินค้า</p>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                    {CATEGORY_OPTIONS.map(opt => (
                    <Pill key={opt.value} active={catFilter === opt.value}
                        onClick={() => handleFilterChange('cat', opt.value)}>
                        {opt.label}
                    </Pill>
                    ))}
                </div>
                </div>
                {/* Skintype */}
                <div style={{ marginBottom: '16px' }}>
                <p style={{ fontSize: '13px', color: '#94A3B8', margin: '0 0 8px', fontWeight: '700' }}>🌿 สภาพผิว</p>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                    {SKINTYPE_OPTIONS.map(opt => (
                    <Pill key={opt.value} active={skintypeFilter === opt.value}
                        onClick={() => handleFilterChange('skin', opt.value)}>
                        {opt.label}
                    </Pill>
                    ))}
                </div>
                </div>
                {/* Price */}
                <div style={{ marginBottom: '12px' }}>
                <p style={{ fontSize: '13px', color: '#94A3B8', margin: '0 0 8px', fontWeight: '700' }}>💰 ช่วงราคา</p>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                    {PRICE_OPTIONS.map(opt => (
                    <Pill key={opt.value} active={priceFilter === opt.value}
                        onClick={() => handleFilterChange('price', opt.value)}>
                        {opt.label}
                    </Pill>
                    ))}
                </div>
                </div>
                {/* Reset */}
                {activeFilterCount > 0 && (
                <button onClick={() => {
                    setCatFilter('all'); setSkintypeFilter('all'); setPriceFilter('all');
                    setFiltered(results);
                }} style={{
                    padding: '6px 16px', borderRadius: '8px', border: '1px solid #FCA5A5',
                    background: '#FEF2F2', color: '#EF4444', cursor: 'pointer',
                    fontSize: '13px', fontFamily: "'Kanit', sans-serif", fontWeight: '600',
                }}>
                    ✕ ล้าง filter ทั้งหมด
                </button>
                )}
            </div>
            )}

            {/* Quick Tags — แสดงเมื่อยังไม่ได้ค้นหา */}
            {!searched && (
            <div style={{ background: 'white', borderRadius: '16px', padding: '20px',
                border: '1px solid #E2E8F0', marginBottom: '24px' }}>
                <p style={{ color: '#64748B', fontSize: '14px', margin: '0 0 14px', fontWeight: '600' }}>💡 ลองค้นหาด้วย...</p>
                {QUICK_TAGS.map((group, gi) => (
                <div key={gi} style={{ marginBottom: gi < QUICK_TAGS.length - 1 ? '14px' : 0 }}>
                    <p style={{ fontSize: '12px', color: '#94A3B8', margin: '0 0 8px', fontWeight: '700' }}>{group.group}</p>
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                    {group.tags.map((tag, ti) => (
                        <button key={ti} onClick={() => handleSearch(tag.value)} style={{
                        padding: '6px 14px', borderRadius: '20px',
                        border: `2px solid ${query === tag.value ? '#6366F1' : '#E2E8F0'}`,
                        background: query === tag.value ? '#EEF2FF' : 'white',
                        color: query === tag.value ? '#4F46E5' : '#475569',
                        fontSize: '13px', cursor: 'pointer',
                        fontFamily: "'Kanit', sans-serif", fontWeight: '500',
                        }}>{tag.label}</button>
                    ))}
                    </div>
                </div>
                ))}
            </div>
            )}

            {/* Loading */}
            {loading && (
            <div style={{ textAlign: 'center', padding: '60px', color: '#64748B' }}>
                <div style={{ fontSize: '32px', marginBottom: '8px' }}>⏳</div>
                <p>กำลังค้นหา...</p>
            </div>
            )}

            {/* ไม่พบผล */}
            {!loading && searched && filtered.length === 0 && (
            <div style={{ textAlign: 'center', padding: '50px', color: '#64748B',
                background: 'white', borderRadius: '16px', border: '1px solid #E2E8F0' }}>
                <div style={{ fontSize: '40px', marginBottom: '8px' }}>🤔</div>
                <h3 style={{ margin: '0 0 6px' }}>
                {results.length > 0 ? 'ไม่มีสินค้าที่ตรง filter ที่เลือก' : 'ไม่พบสินค้าที่ตรงกัน'}
                </h3>
                <p style={{ margin: '0 0 14px', fontSize: '14px' }}>
                {results.length > 0 ? `มีสินค้า ${results.length} รายการ แต่ไม่ผ่าน filter` : 'ลองพิมพ์คำค้นหาอื่น'}
                </p>
                <button onClick={handleClear} style={{
                padding: '8px 20px', borderRadius: '10px',
                border: '2px solid #6366F1', background: 'white', color: '#6366F1',
                cursor: 'pointer', fontSize: '14px', fontFamily: "'Kanit', sans-serif",
                }}>ล้างทั้งหมด</button>
            </div>
            )}

            {/* ผลลัพธ์ */}
            {!loading && filtered.length > 0 && (
            <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px' }}>
                <p style={{ color: '#64748B', margin: 0, fontSize: '14px' }}>
                    แสดง <strong>{filtered.length}</strong>
                    {filtered.length !== results.length && ` / ${results.length}`} รายการ
                    {query && <> สำหรับ "<strong>{query}</strong>"</>}
                </p>
                <button onClick={handleClear} style={{
                    padding: '5px 12px', borderRadius: '8px', border: '1px solid #E2E8F0',
                    background: 'white', color: '#64748B', cursor: 'pointer',
                    fontSize: '12px', fontFamily: "'Kanit', sans-serif",
                }}>ล้างผล</button>
                </div>

                <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                {filtered.map((product, index) => (
                    <div key={index} style={{
                    background: 'white', borderRadius: '14px', padding: '16px 18px',
                    border: '1px solid #E2E8F0', display: 'flex', gap: '14px',
                    alignItems: 'center', transition: 'all 0.2s',
                    boxShadow: '0 2px 6px rgba(0,0,0,0.04)',
                    }}
                    onMouseEnter={e => { e.currentTarget.style.borderColor = '#6366F1'; e.currentTarget.style.transform = 'translateY(-2px)'; e.currentTarget.style.boxShadow = '0 6px 16px rgba(99,102,241,0.1)'; }}
                    onMouseLeave={e => { e.currentTarget.style.borderColor = '#E2E8F0'; e.currentTarget.style.transform = 'translateY(0)'; e.currentTarget.style.boxShadow = '0 2px 6px rgba(0,0,0,0.04)'; }}
                    >
                    {/* รูป */}
                    <div style={{
                        width: '62px', height: '62px', borderRadius: '10px', flexShrink: 0,
                        background: '#F1F5F9', display: 'flex', alignItems: 'center', justifyContent: 'center', overflow: 'hidden',
                    }}>
                        {product.image_url ? (
                        <img src={product.image_url} alt={product.name}
                            style={{ width: '100%', height: '100%', objectFit: 'contain' }}
                            onError={e => e.target.style.display = 'none'}
                        />
                        ) : <span style={{ fontSize: '24px' }}>🧴</span>}
                    </div>

                    {/* ข้อมูล */}
                    <div style={{ flex: 1, minWidth: 0 }}>
                        <div style={{ fontSize: '11px', color: '#64748B', fontWeight: '600',
                        textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: '2px' }}>
                        {product.brand}
                        </div>
                        <div style={{ fontSize: '15px', fontWeight: '700', color: '#1E293B', marginBottom: '5px',
                        overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                        {product.name}
                        </div>
                        <div style={{ display: 'flex', gap: '5px', flexWrap: 'wrap' }}>
                        <span style={{ background: '#EEF2FF', color: '#4F46E5', padding: '2px 8px', borderRadius: '20px', fontSize: '11px', fontWeight: '600' }}>
                            {getCategoryLabel(product.major_category)}
                        </span>
                        <span style={{ background: '#F1F5F9', color: '#475569', padding: '2px 8px', borderRadius: '20px', fontSize: '11px' }}>
                            {product.skintype || 'all skin'}
                        </span>
                        </div>
                    </div>

                    {/* ราคา + bookmark */}
                    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: '8px', flexShrink: 0 }}>
                        <div style={{ fontSize: '18px', fontWeight: '800', color: '#4F46E5' }}>
                        ฿{product.price ? parseInt(product.price).toLocaleString() : '-'}
                        </div>
                        <BookmarkButton product={product} email={user?.email || null} />
                    </div>
                    </div>
                ))}
                </div>
            </div>
            )}

            <div style={{ textAlign: 'center', marginTop: '36px' }}>
            <button onClick={() => navigate('/advisor')} style={{
                background: 'none', border: '2px solid #E2E8F0', padding: '9px 22px',
                borderRadius: '10px', color: '#64748B', cursor: 'pointer', fontSize: '14px',
                fontFamily: "'Kanit', sans-serif",
            }}>← กลับหน้าวิเคราะห์ผิว</button>
            </div>

        </div>
        </div>
    );
};

export default SearchPage;