import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import './UserProfile.css';

const UserProfile = ({ user }) => {
  const navigate = useNavigate();
  
  // สร้างตัวแปรเก็บข้อมูลผู้ใช้ล่าสุด
  const [currentUser, setCurrentUser] = useState(user);

  // --- ฟังก์ชันดึงข้อมูลใหม่ล่าสุด ---
  useEffect(() => {
    if (user?.email) {
      console.log("🔄 Fetching fresh user data...");
      fetch(`http://127.0.0.1:5000/api/user/${user.email}`)
        .then(res => res.json())
        .then(data => {
          if (!data.error) {
            console.log("✅ Got fresh data:", data);
            setCurrentUser(data); // อัปเดตหน้าจอด้วยข้อมูลใหม่
          }
        })
        .catch(err => console.error("Error fetching user:", err));
    }
  }, [user]);

  // ถ้าไม่มี User ให้เด้งไปหน้า Login
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
      
      {/* ส่วนปุ่ม Back กลับหน้าหลัก (เผื่ออยากกลับ) */}
      <div style={{ width: '100%', maxWidth: '500px', marginBottom: '10px', textAlign: 'left' }}>
        <button 
          onClick={() => navigate('/')}
          style={{ border: 'none', background: 'none', color: '#64748b', cursor: 'pointer', fontSize: '14px' }}
        >
          ← กลับหน้าหลัก
        </button>
      </div>

      {/* การ์ดข้อมูลส่วนตัว */}
      <div className="profile-card">
        <div className="profile-header-bg"></div>
        <div className="profile-info">
          <div className="profile-avatar">
            {currentUser.name ? currentUser.name.charAt(0).toUpperCase() : 'U'}
          </div>
          <h2 className="profile-name">{currentUser.name}</h2>
          <p className="profile-email">{currentUser.email}</p>
          {currentUser.role === 'guest' && (
            <span className="guest-badge">บัญชีผู้เยี่ยมชม</span>
          )}
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
          <button className="btn-action btn-logout" onClick={handleLogout}>
            ออกจากระบบ
          </button>
          <button className="btn-action btn-analyze" onClick={() => navigate('/advisor')}>
            วิเคราะห์ผิวอีกครั้ง
          </button>
        </div>
      </div>

      {/* ส่วนประวัติการวิเคราะห์ */}
      <div className="history-section">
        <h3 className="history-title">🕒 ประวัติการวิเคราะห์ผิว ({history.length})</h3>
        
        <div className="history-list">
          {history.length > 0 ? (
            history.map((item, index) => (
              <div key={index} className="history-card">
                <div className="history-header">
                  <span className="history-date">{item.date}</span>
                  <span className="skin-badge">{item.skin_type}</span>
                </div>
                <div className="history-concerns">
                  ปัญหา: {item.concerns.join(', ') || 'ไม่มี'}
                </div>
                
                {/* แสดงสินค้าที่แนะนำแบบย่อ */}
                <div className="history-products">
                  {item.results && item.results.map((prod, idx) => (
                    <div key={idx} className="mini-product">
                      <div className="step-tag">{prod.step}</div>
                      <div className="prod-name" title={prod.name}>
                        {prod.name}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ))
          ) : (
            <div className="empty-history">
              <p>ยังไม่มีประวัติการวิเคราะห์</p>
              <button onClick={() => navigate('/advisor')}>
                เริ่มวิเคราะห์ผิวครั้งแรก
              </button>
            </div>
          )}
        </div>
      </div>

    </div>
  );
};

export default UserProfile;