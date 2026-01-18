import React, { useState } from 'react';

// Import Pages
import AdvisorPage from './pages/SkinCareAdvisor';
import AdminPage from './pages/AdminPage';
import LoginPage from './pages/LoginPage';
import UserProfile from './pages/UserProfile';

function App() {
  const [user, setUser] = useState(null);
  
  // page state: 'profile' | 'advisor' | 'admin'
  const [currentPage, setCurrentPage] = useState('profile'); 

  // --- 1. จัดการ Login (แก้ตรงนี้!) ---
  const handleLoginSuccess = (userData) => {
    setUser(userData);

    // เช็คเงื่อนไข: ถ้าเป็น Guest หรือชื่อ Test ให้ข้ามไปหน้า Advisor เลย
    if (userData.role === 'guest' || userData.email === 'test@gmail.com') {
      setCurrentPage('advisor'); 
    } else {
      // ถ้าเป็นคนอื่น ให้ไปหน้า Profile ก่อน
      setCurrentPage('profile'); 
    }
  };

  // --- 2. ฟังก์ชันอัปเดตข้อมูล User ---
  const handleUpdateUser = (updatedData) => {
    setUser((prevUser) => ({
      ...prevUser,
      ...updatedData
    }));
  };

  // --- 3. จัดการ Logout ---
  const handleLogout = () => {
    setUser(null);
    setCurrentPage('profile'); 
  };

  // --- ถ้ายังไม่ Login ให้โชว์หน้า Login ---
  if (!user) {
    return <LoginPage onLoginSuccess={handleLoginSuccess} />;
  }

  // --- 4. ถ้าอยู่ในโหมด Profile (และไม่ใช่ Test/Guest ที่ข้ามมา) ---
  if (currentPage === 'profile') {
    return (
      <UserProfile 
        user={user} 
        onStartAnalyze={() => setCurrentPage('advisor')}
        onLogout={handleLogout}
        onUpdateUser={handleUpdateUser}
      />
    );
  }

  // --- 5. หน้าใช้งานจริง (Advisor / Admin) ---
  return (
    <div style={{ fontFamily: "'Kanit', sans-serif" }}>
      
      {/* Navbar */}
      <nav style={{ 
        padding: '15px 30px', 
        background: '#1e293b', 
        color: 'white', 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center',
        boxShadow: '0 4px 6px -1px rgba(0,0,0,0.1)'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '15px' }}>
          <h3 style={{ margin: 0, color: '#818cf8' }}>SkinCare AI</h3>
          <span style={{ fontSize: '14px', opacity: 0.8 }}>
             | ผู้ใช้งาน: {user.name} {user.role === 'guest' && '(Guest)'}
          </span>
        </div>
        
        <div style={{ display: 'flex', gap: '10px' }}>
          <button 
            onClick={() => setCurrentPage('advisor')}
            style={{
              padding: '8px 16px', borderRadius: '6px', border: 'none', cursor: 'pointer',
              background: currentPage === 'advisor' ? '#4f46e5' : 'transparent',
              color: currentPage === 'advisor' ? 'white' : '#94a3b8'
            }}
          >
            🔍 วิเคราะห์ผิว
          </button>
          
          {user.role === 'admin' && (
            <button 
              onClick={() => setCurrentPage('admin')}
              style={{
                padding: '8px 16px', borderRadius: '6px', border: 'none', cursor: 'pointer',
                background: currentPage === 'admin' ? '#4f46e5' : 'transparent',
                color: currentPage === 'admin' ? 'white' : '#94a3b8'
              }}
            >
              ⚙️ จัดการสินค้า
            </button>
          )}

          {/* ปุ่มกลับหน้า Profile (ซ่อนถ้าเป็น Guest ก็ได้ ถ้าต้องการ) */}
          <button 
             onClick={() => setCurrentPage('profile')}
             style={{ padding: '8px 16px', background: 'transparent', color: '#cbd5e1', border: 'none', cursor: 'pointer' }}
          >
            👤 โปรไฟล์
          </button>
          
          <button 
            onClick={handleLogout} 
            style={{ 
              padding: '8px 16px', background: '#ef4444', color: 'white', 
              border: 'none', borderRadius: '6px', cursor: 'pointer', marginLeft: '10px' 
            }}
          >
            ออก
          </button>
        </div>
      </nav>

      <main style={{ padding: '20px' }}>
        {currentPage === 'advisor' ? <AdvisorPage user={user} /> : <AdminPage />}
      </main>

    </div>
  );
}

export default App;