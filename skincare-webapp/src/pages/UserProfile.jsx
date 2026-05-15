import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import './UserProfile.css';

const API = import.meta.env.VITE_API_URL || 'http://127.0.0.1:5000/api';

const getCategoryLabel = (cat) => ({
  moisturizer: 'มอยส์เจอไรเซอร์', serum: 'เซรั่ม', sunscreen: 'กันแดด',
  toner: 'โทนเนอร์', cleanser: 'คลีนเซอร์', mask: 'มาส์ก',
  exfoliator: 'เอ็กซ์โฟเลียเตอร์', eye_care: 'ครีมตา',
}[cat] || cat || '-');

// ===== Product Item (recommend) =====
const ProductItem = ({ prod, idx }) => (
  <div className="modal-product-item">
    <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
      {prod.image_url && (
        <img src={prod.image_url} alt={prod.name}
          style={{ width: '50px', height: '50px', objectFit: 'contain', borderRadius: '8px', flexShrink: 0 }}
          onError={e => e.target.style.display = 'none'}
        />
      )}
      <div style={{ flex: 1 }}>
        <div className="modal-prod-brand">{prod.brand}</div>
        <div className="modal-prod-name">{prod.name}</div>
        <div style={{ display: 'flex', gap: '6px', marginTop: '4px' }}>
          <span style={{ background: '#EEF2FF', color: '#4F46E5', padding: '2px 8px', borderRadius: '12px', fontSize: '12px' }}>
            {getCategoryLabel(prod.major_category)}
          </span>
        </div>
      </div>
      <div className="modal-prod-price">
        ฿{prod.price ? parseInt(prod.price).toLocaleString() : '-'}
      </div>
    </div>
  </div>
);

// ===== Routine Item =====
const RoutineItem = ({ prod }) => (
  <div className="modal-product-item">
    <div style={{
      background: 'linear-gradient(135deg, #4F46E5, #8B5CF6)',
      display: 'inline-flex', alignItems: 'center', gap: '6px',
      padding: '4px 12px', borderRadius: '12px', marginBottom: '10px'
    }}>
      <span>{prod.step_icon}</span>
      <span style={{ color: 'white', fontSize: '12px', fontWeight: '600' }}>
        Step {prod.step} — {prod.step_label}
      </span>
    </div>
    <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
      {prod.image_url && (
        <img src={prod.image_url} alt={prod.name}
          style={{ width: '50px', height: '50px', objectFit: 'contain', borderRadius: '8px', flexShrink: 0 }}
          onError={e => e.target.style.display = 'none'}
        />
      )}
      <div style={{ flex: 1 }}>
        <div className="modal-prod-brand">{prod.brand}</div>
        <div className="modal-prod-name">{prod.name}</div>
      </div>
      <div className="modal-prod-price">
        ฿{prod.price ? parseInt(prod.price).toLocaleString() : '-'}
      </div>
    </div>
  </div>
);

// ===== Modal =====
const HistoryModal = ({ item, onClose }) => {
  const [tab, setTab] = useState('recommend');
  const recList     = Array.isArray(item.results) ? item.results : [];
  const routineList = Array.isArray(item.routine) ? item.routine : [];
  const hasRoutine  = routineList.length > 0;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={e => e.stopPropagation()}>
        <button className="modal-close" onClick={onClose}>×</button>
        <h2 className="modal-title">ผลการวิเคราะห์ผิว</h2>
        <p className="modal-date">วันที่ {item.date}</p>

        <div className="modal-summary">
          <span className="skin-badge-large">{item.skin_type}</span>
          <p><strong>ปัญหาผิว:</strong> {
            Array.isArray(item.concerns) ? item.concerns.join(', ') || 'ไม่มี' : 'ไม่มี'
          }</p>
        </div>

        {/* Tabs */}
        {hasRoutine && (
          <div style={{ display: 'flex', gap: '8px', marginBottom: '20px' }}>
            {[
              { key: 'recommend', label: 'สินค้าแนะนำ' },
              { key: 'routine',   label: 'Routine' },
            ].map(t => (
              <button key={t.key} onClick={() => setTab(t.key)} style={{
                flex: 1, padding: '10px', borderRadius: '10px', border: 'none',
                background: tab === t.key ? 'linear-gradient(135deg, #667eea, #764ba2)' : '#F1F5F9',
                color: tab === t.key ? 'white' : '#64748B',
                fontWeight: '600', cursor: 'pointer', fontSize: '14px',
                fontFamily: "'Kanit', sans-serif",
              }}>
                {t.label}
              </button>
            ))}
          </div>
        )}

        {/* Content */}
        <div className="modal-results">
          {tab === 'recommend' && (
            <>
              <h3>สินค้าที่แนะนำ</h3>
              {recList.length > 0
                ? recList.map((prod, i) => <ProductItem key={i} prod={prod} idx={i} />)
                : <p style={{ color: '#94A3B8', textAlign: 'center' }}>ไม่มีข้อมูล</p>
              }
            </>
          )}
          {tab === 'routine' && (
            <>
              <h3>Skincare Routine</h3>
              {routineList.length > 0
                ? routineList.map((prod, i) => <RoutineItem key={i} prod={prod} />)
                : <p style={{ color: '#94A3B8', textAlign: 'center' }}>ไม่มีข้อมูล routine</p>
              }
            </>
          )}
        </div>
      </div>
    </div>
  );
};

// ===== Main Page =====
const UserProfile = ({ user }) => {
  const navigate = useNavigate();
  const [currentUser, setCurrentUser] = useState(user);
  const [selectedItem, setSelectedItem] = useState(null);

  useEffect(() => {
    if (user?.email) {
      fetch(`${API}/user/${user.email}`)
        .then(res => res.json())
        .then(data => { if (!data.error) setCurrentUser(data); })
        .catch(err => console.error("Error fetching user:", err));
    }
  }, [user]);

  if (!currentUser) { navigate('/login'); return null; }

  const handleLogout = () => { navigate('/login'); window.location.reload(); };
  const history = currentUser.history || [];

  return (
    <div className="profile-container">
      <div style={{ width: '100%', maxWidth: '500px', marginBottom: '10px', textAlign: 'left' }}>
        <button onClick={() => navigate('/')} style={{ border: 'none', background: 'none', color: '#64748b', cursor: 'pointer', fontSize: '14px' }}>
          ← กลับหน้าหลัก
        </button>
      </div>

      <div className="profile-card">
        <div className="profile-header-bg"></div>
        <div className="profile-info">
          <div className="profile-avatar">{currentUser.name ? currentUser.name.charAt(0).toUpperCase() : 'U'}</div>
          <h2 className="profile-name">{currentUser.name}</h2>
          <p className="profile-email">{currentUser.email}</p>
        </div>
        <div className="profile-details">
          <div className="detail-row">
            <span className="detail-label">วันเกิด</span>
            <span className="detail-value">{currentUser.birthdate || '-'}</span>
          </div>
          <div className="detail-row">
            <span className="detail-label">อายุ</span>
            <span className="detail-value">{currentUser.age || 0} ปี</span>
          </div>
        </div>
        <div className="profile-actions">
          <button className="btn-action btn-logout" onClick={handleLogout}>ออกจากระบบ</button>
          <button className="btn-action btn-analyze" onClick={() => navigate('/advisor')}>วิเคราะห์ผิวอีกครั้ง</button>
        </div>
      </div>

      <div className="history-section">
        <h3 className="history-title">ประวัติการวิเคราะห์ผิว ({history.length})</h3>
        <div className="history-list">
          {history.length > 0 ? history.map((item, index) => (
            <div key={index} className="history-card clickable" onClick={() => setSelectedItem(item)}>
              <div className="history-header">
                <span className="history-date">{item.date}</span>
                <div style={{ display: 'flex', gap: '6px', alignItems: 'center' }}>
                  {item.routine && item.routine.length > 0 && (
                    <span style={{
                      background: '#EEF2FF', color: '#4F46E5', padding: '3px 8px',
                      borderRadius: '12px', fontSize: '11px', fontWeight: '600'
                    }}>Routine</span>
                  )}
                  <span className="skin-badge">{item.skin_type}</span>
                </div>
              </div>
              <div className="history-concerns">
                ปัญหา: {Array.isArray(item.concerns) ? item.concerns.join(', ') || 'ไม่มี' : 'ไม่มี'}
              </div>
              <div className="click-hint">กดเพื่อดูรายละเอียด...</div>
            </div>
          )) : (
            <div className="empty-history"><p>ยังไม่มีประวัติการวิเคราะห์</p></div>
          )}
        </div>
      </div>

      {selectedItem && (
        <HistoryModal item={selectedItem} onClose={() => setSelectedItem(null)} />
      )}
    </div>
  );
};

export default UserProfile;