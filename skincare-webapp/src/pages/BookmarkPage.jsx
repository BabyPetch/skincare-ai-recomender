import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import BookmarkButton from '../components/Reviews/BookmarkButton';
import ReviewButton   from '../components/Reviews/ReviewButton';
import ProductReviews from '../components/Reviews/ProductReviews';
import './BookmarkPage.css';

const API = 'http://127.0.0.1:5000/api';

const getCategoryLabel = (cat) => ({
  moisturizer: '🔒 มอยส์เจอไรเซอร์', serum: '✨ เซรั่ม',
  sunscreen: '☀️ กันแดด', toner: '💦 โทนเนอร์',
  cleanser: '🧼 คลีนเซอร์', mask: '🎭 มาส์ก',
  exfoliator: '🌀 เอ็กซ์โฟเลียเตอร์', eye_care: '👁️ ครีมตา',
}[cat] || cat || '-');

const BookmarkPage = ({ user }) => {
  const navigate              = useNavigate();
  const [items, setItems]     = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter]   = useState('all');

  const fetchBookmarks = useCallback(async () => {
    if (!user?.email) return;
    setLoading(true);
    try {
      const res  = await fetch(`${API}/bookmarks/${user.email}`);
      const data = await res.json();
      setItems(Array.isArray(data) ? data : []);
    } catch (err) { console.error(err); }
    finally { setLoading(false); }
  }, [user]);

  useEffect(() => { fetchBookmarks(); }, [fetchBookmarks]);

  const handleRemove = (name, isSaved) => {
    if (!isSaved) setItems(prev => prev.filter(p => p.name !== name));
  };

  const categories = ['all', ...new Set(items.map(p => p.major_category).filter(Boolean))];
  const filtered   = filter === 'all' ? items : items.filter(p => p.major_category === filter);

  if (!user) { navigate('/login'); return null; }

  return (
    <div className="bookmark-page">
      <div className="bookmark-inner">

        <div className="bookmark-header">
          <div>
            <h1>🔖 สินค้าที่บันทึกไว้</h1>
            <p>{items.length} รายการ</p>
          </div>
          <button className="bookmark-back-btn" onClick={() => navigate(-1)}>← กลับ</button>
        </div>

        {items.length > 0 && (
          <div className="bookmark-filter-row">
            {categories.map(cat => (
              <button key={cat}
                className={`bookmark-filter-btn ${filter === cat ? 'active' : ''}`}
                onClick={() => setFilter(cat)}>
                {cat === 'all' ? `ทั้งหมด (${items.length})` : getCategoryLabel(cat)}
              </button>
            ))}
          </div>
        )}

        {loading && (
          <div className="bookmark-loading">
            <div style={{ fontSize: '32px', marginBottom: '10px' }}>⏳</div>
            <p>กำลังโหลด...</p>
          </div>
        )}

        {!loading && items.length === 0 && (
          <div className="bookmark-empty">
            <div style={{ fontSize: '56px', marginBottom: '16px' }}>🔖</div>
            <h3>ยังไม่มีสินค้าที่บันทึก</h3>
            <p>กดปุ่ม 🔖 ที่สินค้าในหน้าแนะนำหรือค้นหาเพื่อบันทึกไว้</p>
            <div className="bookmark-empty-actions">
              <button className="btn-primary-gradient" onClick={() => navigate('/advisor')}>วิเคราะห์ผิว</button>
              <button className="btn-outline-accent" onClick={() => navigate('/search')}>ค้นหาสินค้า</button>
            </div>
          </div>
        )}

        {!loading && filtered.length > 0 && (
          <div className="bookmark-list">
            {filtered.map((product, index) => (
              <div key={index} className="bookmark-card">
                <div className="bookmark-img-box">
                  {product.image_url
                    ? <img src={product.image_url} alt={product.name} onError={e => e.target.style.display = 'none'} />
                    : <span style={{ fontSize: '26px' }}>🧴</span>}
                </div>
                <div className="bookmark-product-info">
                  <div className="bookmark-brand">{product.brand}</div>
                  <div className="bookmark-name">{product.name}</div>
                  <div className="bookmark-tags">
                    <span className="bookmark-tag-cat">{getCategoryLabel(product.major_category)}</span>
                    <span className="bookmark-tag-skin">{product.skintype || 'all skin'}</span>
                  </div>
                </div>
                <div className="bookmark-price-col">
                  <div className="bookmark-price">฿{product.price ? parseInt(product.price).toLocaleString() : '-'}</div>
                  <BookmarkButton product={product} email={user.email} initialSaved={true} onToggle={handleRemove} />
                  <ReviewButton product={product} email={user.email} userName={user?.name} />
                </div>
                <ProductReviews productName={product.name} />
              </div>
            ))}
          </div>
        )}

      </div>
    </div>
  );
};

export default BookmarkPage;