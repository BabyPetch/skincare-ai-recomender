import React, { useState, useRef } from 'react';
import { calculateAge } from '../utils/helpers'; // <--- Import Helper ที่แยกไว้
import './UserProfile.css'; // <--- อย่าลืมบรรทัดนี้!

const UserProfile = ({ user, onStartAnalyze, onLogout, onUpdateUser }) => {
  const [isEditing, setIsEditing] = useState(false);
  
  const [editName, setEditName] = useState(user.name || '');
  const [editBirthdate, setEditBirthdate] = useState(user.birthdate || '2000-01-01');
  const [previewImage, setPreviewImage] = useState(user.avatar || null);

  const fileInputRef = useRef(null);

  // คำนวณอายุจาก State ปัจจุบัน (Real-time update)
  const currentAge = calculateAge(editBirthdate);

  const handleImageChange = (e) => {
    const file = e.target.files[0];
    if (file) setPreviewImage(URL.createObjectURL(file));
  };

  const handleSave = () => {
    onUpdateUser({
      name: editName,
      birthdate: editBirthdate,
      age: currentAge, // ส่งอายุที่คำนวณแล้วกลับไปเก็บที่ App.js
      avatar: previewImage
    });
    setIsEditing(false);
  };

  return (
    <div className="profile-container">
      <div className="profile-header">
        <div className="avatar-wrapper">
          {previewImage ? (
            <img src={previewImage} alt="Profile" className="avatar-img" />
          ) : (
            <div className="avatar-circle">{user.name ? user.name.charAt(0).toUpperCase() : 'U'}</div>
          )}
          {isEditing && (
            <div className="avatar-overlay" onClick={() => fileInputRef.current.click()}>📷</div>
          )}
          <input type="file" ref={fileInputRef} style={{ display: 'none' }} accept="image/*" onChange={handleImageChange} />
        </div>

        {isEditing ? (
          <div className="edit-form">
            <input type="text" className="edit-input" value={editName} onChange={(e) => setEditName(e.target.value)} placeholder="ชื่อของคุณ" />
            <p className="user-email">{user.email}</p>
          </div>
        ) : (
          <>
            <h1 className="user-name">สวัสดี, {user.name} 👋</h1>
            <p className="user-email">{user.email}</p>
          </>
        )}

        <button className={`edit-btn ${isEditing ? 'save-mode' : ''}`} onClick={isEditing ? handleSave : () => setIsEditing(true)}>
          {isEditing ? '💾 บันทึกข้อมูล' : '✏️ แก้ไขโปรไฟล์'}
        </button>
      </div>

      <div className="info-section">
        <h3>📝 ข้อมูลสำหรับการวิเคราะห์ผิว</h3>
        <div className="info-card">
          <label>วันเกิดของคุณ:</label>
          
          {isEditing ? (
            <input 
              type="date" 
              className="edit-select"
              value={editBirthdate}
              onChange={(e) => setEditBirthdate(e.target.value)}
            />
          ) : (
            <div style={{ textAlign: 'right' }}>
              <div className="display-value" style={{ fontSize: '1.2rem', color: '#4f46e5', fontWeight: 'bold' }}>
                อายุ {currentAge} ปี
              </div>
              <small style={{ color: '#94a3b8' }}>
                (เกิดวันที่ {new Date(editBirthdate).toLocaleDateString('th-TH')})
              </small>
            </div>
          )}
        </div>
        <p style={{ fontSize: '12px', color: '#94a3b8', marginTop: '10px' }}>
          *ระบบจะใช้อายุนี้ในการเลือกสกินแคร์ที่เหมาะกับวัย
        </p>
      </div>

      <div className="action-area">
        <button className="logout-btn" onClick={onLogout}>ออกจากระบบ</button>
        <button className="start-btn" onClick={onStartAnalyze}>✨ ไปหน้าวิเคราะห์ผิว</button>
      </div>
    </div>
  );
};

export default UserProfile;