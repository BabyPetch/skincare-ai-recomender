import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useNavigate, useLocation } from 'react-router-dom';

// Import Pages
import SkinCareAdvisor from './pages/SkinCareAdvisor';
import AdminPage from './pages/AdminPage';
import LoginPage from './pages/LoginPage';
import UserProfile from './pages/UserProfile';

// --- ส่วนประกอบ: Navbar ---
const Navbar = ({ user, onLogout }) => {
  const navigate = useNavigate();
  const location = useLocation();

  const isActive = (path) => location.pathname === path;

  // สไตล์ปุ่มทั่วไป
  const btnStyle = (path) => ({
    padding: '8px 16px',
    borderRadius: '6px',
    border: 'none',
    cursor: 'pointer',
    background: isActive(path) ? '#4f46e5' : 'transparent',
    color: isActive(path) ? 'white' : '#94a3b8',
    transition: '0.2s'
  });

  return (
    <nav style={{ 
      padding: '15px 30px', 
      background: '#1e293b', 
      color: 'white', 
      display: 'flex', 
      justifyContent: 'space-between', 
      alignItems: 'center',
      boxShadow: '0 4px 6px -1px rgba(0,0,0,0.1)',
      position: 'sticky',
      top: 0,
      zIndex: 1000
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '15px' }}>
        <h3 style={{ margin: 0, color: '#818cf8', cursor:'pointer' }} onClick={() => navigate('/skincare-advisor')}>
            SkinCare AI ✨
        </h3>
        <span style={{ fontSize: '14px', opacity: 0.8, borderLeft: '1px solid #475569', paddingLeft: '15px' }}>
            สวัสดี, {user?.name || 'Guest'} 
            {user?.role === 'admin' && <span style={{color: '#facc15', marginLeft: '5px'}}> (Admin)</span>}
        </span>
      </div>
      
      <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
        
        {/* 1. ปุ่มไปหน้า AI Advisor */}
        <button 
          onClick={() => navigate('/skincare-advisor')}
          style={btnStyle('/skincare-advisor')}
        >
          🔍 วิเคราะห์ผิว
        </button>
        
        {/* 2. ปุ่ม Admin (โชว์เฉพาะแอดมิน) */}
        {user?.role === 'admin' && (
          <button 
            onClick={() => navigate('/admin')}
            style={btnStyle('/admin')}
          >
            👑 ระบบหลังบ้าน
          </button>
        )}

        {/* 3. ปุ่ม Profile (โชว์ทุกคนที่ไม่ใช่ Guest) */}
        {user?.role !== 'guest' && (
             <button 
             onClick={() => navigate('/profile')}
             style={btnStyle('/profile')}
          >
            👤 โปรไฟล์
          </button>
        )}
        
        {/* 4. ปุ่ม Logout */}
        <button 
          onClick={onLogout} 
          style={{ 
            padding: '8px 16px', background: '#ef4444', color: 'white', 
            border: 'none', borderRadius: '6px', cursor: 'pointer', marginLeft: '10px' 
          }}
        >
          ออกจากระบบ
        </button>
      </div>
    </nav>
  );
};

// --- Main App Component ---
function App() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // 1. ตรวจสอบ localStorage ตอนเริ่มแอป (เพื่อให้ Refresh แล้วไม่หลุด)
  useEffect(() => {
    const savedUser = localStorage.getItem('user');
    if (savedUser) {
      setUser(JSON.parse(savedUser));
    }
    setLoading(false);
  }, []);

  // 2. ฟังก์ชัน Logout
  const handleLogout = () => {
    localStorage.removeItem('user');
    setUser(null);
    window.location.href = '/login'; 
  };

  // 3. ฟังก์ชัน Login
  const handleLogin = (userData) => {
    setUser(userData);
    localStorage.setItem('user', JSON.stringify(userData));
  };

  if (loading) return <div style={{padding:'20px'}}>⏳ Loading...</div>;

  return (
    <Router>
      <div style={{ fontFamily: "'Kanit', sans-serif", minHeight: '100vh', background: '#F8FAFC' }}>
        
        {/* แสดง Navbar เฉพาะตอน Login แล้ว */}
        {user && <Navbar user={user} onLogout={handleLogout} />}

        <Routes>
          {/* ✅ Route 1: หน้า Login */}
          <Route 
            path="/login" 
            element={!user ? <LoginPage onLoginSuccess={handleLogin} /> : <Navigate to="/skincare-advisor" />} 
          />

          {/* ✅ Route 2: หน้า AI Advisor (สำคัญ: ส่ง user props ไปด้วย) */}
          <Route 
            path="/skincare-advisor" 
            element={user ? <SkinCareAdvisor user={user} /> : <Navigate to="/login" />} 
          />

          {/* ✅ Route 3: หน้า Profile */}
          <Route 
            path="/profile" 
            element={user ? <UserProfile user={user} /> : <Navigate to="/login" />} 
          />

          {/* ✅ Route 4: หน้า Admin (เช็ค Role ก่อนเข้า) */}
          <Route 
            path="/admin" 
            element={
              user && user.role === 'admin' 
                ? <AdminPage user={user} /> 
                : <Navigate to="/skincare-advisor" />
            } 
          />
          
          {/* ✅ Route 5: ถ้าพิมพ์มั่ว ให้ดีดกลับหน้าหลัก */}
          <Route path="*" element={<Navigate to={user ? "/skincare-advisor" : "/login"} />} />
        </Routes>

      </div>
    </Router>
  );
}

export default App;