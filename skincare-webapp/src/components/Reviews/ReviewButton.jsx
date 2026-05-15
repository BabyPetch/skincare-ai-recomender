import React, { useState, useEffect } from 'react';
import { createPortal } from 'react-dom';
import './ReviewButton.css';

const API = import.meta.env.VITE_API_URL || 'http://127.0.0.1:5000/api';
const STARS = [1, 2, 3, 4, 5];

const ReviewModal = ({ product, email, userName, existing, onClose, onSaved }) => {
  const [rating, setRating] = useState(existing?.rating || 0);
  const [hover,  setHover]  = useState(0);
  const [title,  setTitle]  = useState(existing?.title  || '');
  const [body,   setBody]   = useState(existing?.body   || '');
  const [saving, setSaving] = useState(false);

  const handleSave = async () => {
    if (!rating) return;
    setSaving(true);
    try {
      await fetch(`${API}/review`, {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email, user_name: userName || 'ไม่ระบุชื่อ',
          product_name: product.name,
          brand: product.brand || '',
          rating, title, body,
        }),
      });
      onSaved({ rating, title, body });
      onClose();
    } catch (e) { console.error(e); }
    finally { setSaving(false); }
  };

  const handleDelete = async () => {
    if (!window.confirm('ลบรีวิวนี้?')) return;
    await fetch(`${API}/review`, {
      method:  'DELETE',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, product_name: product.name }),
    });
    onSaved(null);
    onClose();
  };

  // render ออกไปที่ body โดยตรง — หลุดจาก transform ของ card
  return createPortal(
    <div className="rv-overlay" onClick={onClose}>
      <div className="rv-modal" onClick={e => e.stopPropagation()}>
        <button className="rv-close" onClick={onClose}>×</button>

        <h3 className="rv-modal-title">⭐ รีวิวสินค้า</h3>
        <p className="rv-modal-product">{product.brand} — {product.name}</p>

        <div className="rv-stars-row">
          {STARS.map(s => (
            <button key={s}
              className={`rv-star ${s <= (hover || rating) ? 'active' : ''}`}
              onMouseEnter={() => setHover(s)}
              onMouseLeave={() => setHover(0)}
              onClick={() => setRating(s)}>★</button>
          ))}
          <span className="rv-star-label">
            {['', 'แย่มาก', 'พอใช้', 'โอเค', 'ดี', 'ดีมาก'][hover || rating] || 'เลือกดาว'}
          </span>
        </div>

        <input
          className="rv-input"
          placeholder="หัวข้อรีวิว (ไม่บังคับ)"
          value={title}
          onChange={e => setTitle(e.target.value)}
          maxLength={100}
        />

        <textarea
          className="rv-textarea"
          placeholder="รีวิวของคุณ... บอกเล่าประสบการณ์ใช้งาน"
          value={body}
          onChange={e => setBody(e.target.value)}
          rows={4}
          maxLength={500}
        />
        <div className="rv-char-count">{body.length}/500</div>

        <div className="rv-modal-actions">
          {existing && (
            <button className="rv-btn-delete" onClick={handleDelete}>🗑 ลบรีวิว</button>
          )}
          <button className="rv-btn-save" onClick={handleSave}
            disabled={!rating || saving}>
            {saving ? 'กำลังบันทึก...' : existing ? '✏️ แก้ไข' : '💾 บันทึก'}
          </button>
        </div>
      </div>
    </div>,
    document.body
  );
};

const ReviewButton = ({ product, email, userName }) => {
  const [existing, setExisting] = useState(null);
  const [open,     setOpen]     = useState(false);

  useEffect(() => {
    if (!email || !product?.name) return;
    fetch(`${API}/reviews/check`, {
      method:  'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, product_name: product.name }),
    })
      .then(r => r.json())
      .then(data => setExisting(data))
      .catch(() => {});
  }, [email, product?.name]);

  if (!email) return null;

  return (
    <>
      <button
        className={`rv-trigger ${existing ? 'reviewed' : ''}`}
        onClick={() => setOpen(true)}
        title={existing ? `คะแนนของคุณ: ${existing.rating}★` : 'เขียนรีวิว'}
      >
        {existing
          ? <><span className="rv-trigger-stars">{'★'.repeat(existing.rating)}</span><span className="rv-trigger-label">รีวิวแล้ว</span></>
          : <><span>☆</span><span className="rv-trigger-label">รีวิว</span></>
        }
      </button>

      {open && (
        <ReviewModal
          product={product}
          email={email}
          userName={userName}
          existing={existing}
          onClose={() => setOpen(false)}
          onSaved={(data) => setExisting(data)}
        />
      )}
    </>
  );
};

export default ReviewButton;