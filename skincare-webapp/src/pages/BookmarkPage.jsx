import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import BookmarkButton from '../components/BookmarkButton';

const API = 'http://127.0.0.1:5000/api';

const getCategoryLabel = (cat) => ({
    moisturizer: '🔒 มอยส์เจอไรเซอร์', serum: '✨ เซรั่ม',
    sunscreen: '☀️ กันแดด', toner: '💦 โทนเนอร์',
    cleanser: '🧼 คลีนเซอร์', mask: '🎭 มาส์ก',
    exfoliator: '🌀 เอ็กซ์โฟเลียเตอร์', eye_care: '👁️ ครีมตา',
    }[cat] || cat || '-');

    const BookmarkPage = ({ user }) => {
    const navigate             = useNavigate();
    const [items, setItems]    = useState([]);
    const [loading, setLoading] = useState(true);
    const [filter, setFilter]  = useState('all');

    const fetchBookmarks = useCallback(async () => {
        if (!user?.email) return;
        setLoading(true);
        try {
        const res  = await fetch(`${API}/bookmarks/${user.email}`);
        const data = await res.json();
        setItems(Array.isArray(data) ? data : []);
        } catch (err) {
        console.error(err);
        } finally {
        setLoading(false);
        }
    }, [user]);

    useEffect(() => { fetchBookmarks(); }, [fetchBookmarks]);

    const handleRemove = (name, isSaved) => {
        if (!isSaved) setItems(prev => prev.filter(p => p.name !== name));
    };

    // categories ที่มีอยู่จริง
    const categories = ['all', ...new Set(items.map(p => p.major_category).filter(Boolean))];
    const filtered   = filter === 'all' ? items : items.filter(p => p.major_category === filter);

    if (!user) { navigate('/login'); return null; }

    return (
        <div style={{ minHeight: '100vh', background: '#F8FAFC', padding: '40px 20px', fontFamily: "'Kanit', sans-serif" }}>
        <div style={{ maxWidth: '800px', margin: '0 auto' }}>

            {/* Header */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '30px' }}>
            <div>
                <h1 style={{ fontSize: '26px', fontWeight: 'bold', color: '#1E293B', margin: '0 0 4px' }}>
                🔖 สินค้าที่บันทึกไว้
                </h1>
                <p style={{ color: '#64748B', margin: 0, fontSize: '14px' }}>
                {items.length} รายการ
                </p>
            </div>
            <button onClick={() => navigate(-1)} style={{
                background: 'none', border: '2px solid #E2E8F0', padding: '8px 16px',
                borderRadius: '10px', color: '#64748B', cursor: 'pointer', fontSize: '14px',
                fontFamily: "'Kanit', sans-serif",
            }}>← กลับ</button>
            </div>

            {/* Filter tabs */}
            {items.length > 0 && (
            <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap', marginBottom: '24px' }}>
                {categories.map(cat => (
                <button key={cat} onClick={() => setFilter(cat)} style={{
                    padding: '7px 16px', borderRadius: '20px', border: 'none',
                    background: filter === cat ? 'linear-gradient(135deg, #4F46E5, #8B5CF6)' : '#F1F5F9',
                    color: filter === cat ? 'white' : '#64748B',
                    fontWeight: '600', cursor: 'pointer', fontSize: '13px',
                    fontFamily: "'Kanit', sans-serif", transition: 'all 0.2s',
                }}>
                    {cat === 'all' ? `ทั้งหมด (${items.length})` : getCategoryLabel(cat)}
                </button>
                ))}
            </div>
            )}

            {/* Loading */}
            {loading && (
            <div style={{ textAlign: 'center', padding: '80px', color: '#64748B' }}>
                <div style={{ fontSize: '32px', marginBottom: '10px' }}>⏳</div>
                <p>กำลังโหลด...</p>
            </div>
            )}

            {/* Empty */}
            {!loading && items.length === 0 && (
            <div style={{ textAlign: 'center', padding: '80px 30px', background: 'white',
                borderRadius: '20px', border: '2px dashed #E2E8F0' }}>
                <div style={{ fontSize: '56px', marginBottom: '16px' }}>🔖</div>
                <h3 style={{ color: '#1E293B', margin: '0 0 8px' }}>ยังไม่มีสินค้าที่บันทึก</h3>
                <p style={{ color: '#64748B', margin: '0 0 24px' }}>
                กดปุ่ม 🔖 ที่สินค้าในหน้าแนะนำหรือค้นหาเพื่อบันทึกไว้
                </p>
                <div style={{ display: 'flex', gap: '10px', justifyContent: 'center' }}>
                <button onClick={() => navigate('/advisor')} style={{
                    padding: '10px 24px', borderRadius: '10px', border: 'none',
                    background: 'linear-gradient(135deg, #4F46E5, #8B5CF6)',
                    color: 'white', cursor: 'pointer', fontSize: '14px',
                    fontFamily: "'Kanit', sans-serif", fontWeight: '600',
                }}>วิเคราะห์ผิว</button>
                <button onClick={() => navigate('/search')} style={{
                    padding: '10px 24px', borderRadius: '10px',
                    border: '2px solid #6366F1', background: 'white',
                    color: '#6366F1', cursor: 'pointer', fontSize: '14px',
                    fontFamily: "'Kanit', sans-serif", fontWeight: '600',
                }}>ค้นหาสินค้า</button>
                </div>
            </div>
            )}

            {/* List */}
            {!loading && filtered.length > 0 && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                {filtered.map((product, index) => (
                <div key={index} style={{
                    background: 'white', borderRadius: '16px', padding: '18px 20px',
                    border: '1px solid #E2E8F0', display: 'flex', gap: '14px',
                    alignItems: 'center', boxShadow: '0 2px 8px rgba(0,0,0,0.04)',
                    transition: 'all 0.2s',
                }}
                    onMouseEnter={e => {
                    e.currentTarget.style.borderColor = '#6366F1';
                    e.currentTarget.style.boxShadow = '0 6px 20px rgba(99,102,241,0.1)';
                    }}
                    onMouseLeave={e => {
                    e.currentTarget.style.borderColor = '#E2E8F0';
                    e.currentTarget.style.boxShadow = '0 2px 8px rgba(0,0,0,0.04)';
                    }}
                >
                    {/* รูป */}
                    <div style={{
                    width: '65px', height: '65px', borderRadius: '12px', flexShrink: 0,
                    background: '#F1F5F9', display: 'flex', alignItems: 'center', justifyContent: 'center',
                    overflow: 'hidden',
                    }}>
                    {product.image_url ? (
                        <img src={product.image_url} alt={product.name}
                        style={{ width: '100%', height: '100%', objectFit: 'contain' }}
                        onError={e => e.target.style.display = 'none'}
                        />
                    ) : <span style={{ fontSize: '26px' }}>🧴</span>}
                    </div>

                    {/* ข้อมูล */}
                    <div style={{ flex: 1, minWidth: 0 }}>
                    <div style={{ fontSize: '11px', color: '#64748B', fontWeight: '600',
                        textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: '2px' }}>
                        {product.brand}
                    </div>
                    <div style={{ fontSize: '15px', fontWeight: '700', color: '#1E293B', marginBottom: '6px',
                        overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                        {product.name}
                    </div>
                    <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
                        <span style={{
                        background: '#EEF2FF', color: '#4F46E5', padding: '2px 10px',
                        borderRadius: '20px', fontSize: '12px', fontWeight: '600'
                        }}>
                        {getCategoryLabel(product.major_category)}
                        </span>
                        <span style={{
                        background: '#F1F5F9', color: '#475569', padding: '2px 10px',
                        borderRadius: '20px', fontSize: '12px'
                        }}>
                        {product.skintype || 'all skin'}
                        </span>
                    </div>
                    </div>

                    {/* ราคา + ปุ่ม */}
                    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: '8px', flexShrink: 0 }}>
                    <div style={{ fontSize: '18px', fontWeight: '800', color: '#4F46E5' }}>
                        ฿{product.price ? parseInt(product.price).toLocaleString() : '-'}
                    </div>
                    <BookmarkButton
                        product={product}
                        email={user.email}
                        initialSaved={true}
                        onToggle={handleRemove}
                    />
                    </div>
                </div>
                ))}
            </div>
            )}

        </div>
        </div>
    );
};

export default BookmarkPage;