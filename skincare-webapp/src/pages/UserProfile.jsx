import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import './UserProfile.css';

const UserProfile = ({ user }) => {
  const navigate = useNavigate();
  const [currentUser, setCurrentUser] = useState(user);
  
  // ✅ 1. เพิ่ม State สำหรับเก็บข้อมูลประวัติที่ถูกเลือก
  const [selectedItem, setSelectedItem] = useState(null);

  useEffect(() => {
    if (user?.email) {
      fetch(`http://127.0.0.1:5000/api/user/${user.email}`)
        .then(res => res.json())
        .then(data => {
          if (!data.error) setCurrentUser(data);
        })
        .catch(err => console.error("Error fetching user:", err));
    }
  }, [user]);

  if (!currentUser) {
    navigate('/login');
    return null;
  }

  const handleLogout = () => {
    navigate('/login');
    window.location.reload(); 
  };

  const history = currentUser.history || [];

  return (
    <div className="profile-container">
      {/* ส่วนปุ่ม Back และการ์ดโปรไฟล์ (คงเดิมตามแบบที่คุณชอบ) */}
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
            <span className="detail-label">🎂 วันเกิด</span>
            <span className="detail-value">{currentUser.birthdate || '-'}</span>
          </div>
          <div className="detail-row">
            <span className="detail-label">📅 อายุ</span>
            <span className="detail-value">{currentUser.age || 0} ปี</span>
          </div>
        </div>
        <div className="profile-actions">
          <button className="btn-action btn-logout" onClick={handleLogout}>ออกจากระบบ</button>
          <button className="btn-action btn-analyze" onClick={() => navigate('/advisor')}>วิเคราะห์ผิวอีกครั้ง</button>
        </div>
      </div>

      {/* --- ส่วนประวัติการวิเคราะห์ --- */}
      <div className="history-section">
        <h3 className="history-title">🕒 ประวัติการวิเคราะห์ผิว ({history.length})</h3>
        <div className="history-list">
          {history.length > 0 ? (
            history.map((item, index) => (
              // ✅ 2. ใส่ onClick ให้กับการ์ด เพื่อเปิด Modal
              <div key={index} className="history-card clickable" onClick={() => setSelectedItem(item)}>
                <div className="history-header">
                  <span className="history-date">{item.date}</span>
                  <span className="skin-badge">{item.skin_type}</span>
                </div>
                <div className="history-concerns">
                  ปัญหา: {item.concerns.join(', ') || 'ไม่มี'}
                </div>
                <div className="click-hint">กดเพื่อดูรายละเอียด...</div>
              </div>
            ))
          ) : (
            <div className="empty-history"><p>ยังไม่มีประวัติการวิเคราะห์</p></div>
          )}
        </div>
      </div>

      {/* ✅ 3. เพิ่ม MODAL (หน้าต่างเด้ง) */}
      {selectedItem && (
        <div className="modal-overlay" onClick={() => setSelectedItem(null)}>
          <div className="modal-content" onClick={e => e.stopPropagation()}>
            <button className="modal-close" onClick={() => setSelectedItem(null)}>×</button>
            <h2 className="modal-title">ผลการวิเคราะห์ผิว</h2>
            <p className="modal-date">วันที่ {selectedItem.date}</p>
            
            <div className="modal-summary">
              <span className="skin-badge-large">{selectedItem.skin_type}</span>
              <p><strong>ปัญหาผิว:</strong> {selectedItem.concerns.join(', ') || 'ไม่มี'}</p>
            </div>

            <div className="modal-results">
              <h3>✨ สินค้าที่แนะนำ</h3>
              {selectedItem.results && selectedItem.results.map((prod, idx) => (
                <div key={idx} className="modal-product-item">
                  <div className="modal-step-tag">
                    {(() => {
                      // 1. ดึงค่าจากตัวแปรที่น่าจะเป็นไปได้ (ลองเช็คทุกชื่อที่คุณอาจจะใช้ใน CSV)
                      const stepValue = prod.step || prod.category || prod.Category || prod.type;

                      // 2. ถ้าเป็นตัวเลข หรือข้อความตัวเลข ให้แปลงเป็นชื่อขั้นตอนไทย
                      if (stepValue === 1 || stepValue === "1" || String(stepValue).toLowerCase().includes('cleansing')) {
                        return "🧼 Step 1: ล้างหน้า";
                      }
                      if (stepValue === 2 || stepValue === "2" || String(stepValue).toLowerCase().includes('essence')) {
                        return "💦 Step 2: เตรียมผิว";
                      }
                      if (stepValue === 3 || stepValue === "3" || String(stepValue).toLowerCase().includes('serum')) {
                        return "✨ Step 3: บำรุงล้ำลึก";
                      }
                      if (stepValue === 4 || stepValue === "4" || String(stepValue).toLowerCase().includes('moisturizer')) {
                        return "🔒 Step 4: ล็อคความชุ่มชื้น";
                      }
                      if (stepValue === 5 || stepValue === "5" || String(stepValue).toLowerCase().includes('sunscreen')) {
                        return "☀️ Step 5: กันแดด";
                      }

                      // 3. ถ้าไม่เข้าเงื่อนไขเลย ให้แสดงค่าที่มีอยู่ ถ้าไม่มีจริงๆ ให้ขึ้นว่า "บำรุงผิว"
                      return stepValue || "✨ ขั้นตอนบำรุง";
                    })()}
                  </div>
                  <div className="modal-prod-details">
                    <div className="modal-prod-brand">{prod.brand}</div>
                    <div className="modal-prod-name">{prod.name}</div>
                    <div className="modal-prod-price">ราคาประมาณ {prod.price} บาท</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default UserProfile;