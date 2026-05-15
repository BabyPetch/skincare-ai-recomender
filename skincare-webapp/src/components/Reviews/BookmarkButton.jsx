import React, { useState } from 'react';

const API = import.meta.env.VITE_API_URL || 'http://127.0.0.1:5000/api';

const BookmarkButton = ({ product, email, initialSaved = false, onToggle }) => {
  const [saved, setSaved]     = useState(initialSaved);
  const [loading, setLoading] = useState(false);

  const handleClick = async (e) => {
    e.stopPropagation();
    if (!email) {
      alert('กรุณาเข้าสู่ระบบก่อนบันทึกสินค้า');
      return;
    }
    setLoading(true);
    try {
      const res  = await fetch(`${API}/bookmark`, {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
        body:    JSON.stringify({ email, product }),
      });
      const data = await res.json();
      const newSaved = data.status === 'added';
      setSaved(newSaved);
      if (onToggle) onToggle(product.name, newSaved);
    } catch (err) {
      console.error('Bookmark error:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <button
      onClick={handleClick}
      disabled={loading}
      title={saved ? 'ลบออกจากที่บันทึก' : 'บันทึกสินค้า'}
      style={{
        background:    saved ? '#FEF3C7' : '#F1F5F9',
        border:        `2px solid ${saved ? '#F59E0B' : '#E2E8F0'}`,
        borderRadius:  '10px',
        padding:       '6px 10px',
        cursor:        loading ? 'not-allowed' : 'pointer',
        fontSize:      '16px',
        transition:    'all 0.2s',
        opacity:       loading ? 0.6 : 1,
        lineHeight:    1,
      }}
      onMouseEnter={e => {
        if (!loading) e.currentTarget.style.transform = 'scale(1.1)';
      }}
      onMouseLeave={e => {
        e.currentTarget.style.transform = 'scale(1)';
      }}
    >
      {loading ? '⏳' : saved ? '🔖' : '🔖'}
      <span style={{
        fontSize: '11px', marginLeft: '4px', fontWeight: '600',
        color: saved ? '#D97706' : '#94A3B8',
        fontFamily: "'Kanit', sans-serif",
      }}>
        {saved ? 'บันทึกแล้ว' : 'บันทึก'}
      </span>
    </button>
  );
};

export default BookmarkButton;