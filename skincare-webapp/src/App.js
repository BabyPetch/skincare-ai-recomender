import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useNavigate, useLocation } from 'react-router-dom';

// Import Pages
import SkinCareAdvisor from './pages/SkinCareAdvisor';
import AdminPage from './pages/AdminPage';
import LoginPage from './pages/LoginPage';
import UserProfile from './pages/UserProfile';
import SkinGuide from './pages/SkinGuide';

// --- Navbar ---
const Navbar = ({ user, onLogout }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const isActive = (path) => location.pathname === path;

  const btnStyle = (path) => ({
    padding: '8px 16px', borderRadius: '6px', border: 'none', cursor: 'pointer',
    background: isActive(path) ? '#4f46e5' : 'transparent',
    color: isActive(path) ? 'white' : '#94a3b8', transition: '0.2s'
  });

  return (
    <nav style={{ padding: '15px 30px', background: '#1e293b', color: 'white', display: 'flex', justifyContent: 'space-between', alignItems: 'center', position: 'sticky', top: 0, zIndex: 1000 }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '15px' }}>
        <h3 style={{ margin: 0, color: '#818cf8', cursor:'pointer' }} onClick={() => navigate('/advisor')}>
            SkinCare AI ✨
        </h3>
        <span style={{ fontSize: '14px', opacity: 0.8, borderLeft: '1px solid #475569', paddingLeft: '15px' }}>
            สวัสดี, {user?.name || 'Guest'} 
            {user?.role === 'admin' && <span style={{color: '#facc15', marginLeft: '5px'}}> (Admin)</span>}
        </span>
      </div>
      
      <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
        {/* ✅ แก้ Link ให้ตรงกัน */}
        <button onClick={() => navigate('/advisor')} style={btnStyle('/advisor')}>
          🔍 วิเคราะห์ผิว
        </button>
        
        {user?.role === 'admin' && (
          <button onClick={() => navigate('/admin')} style={btnStyle('/admin')}>
            👑 ระบบหลังบ้าน
          </button>
        )}

        {user?.role !== 'guest' && (
             <button onClick={() => navigate('/profile')} style={btnStyle('/profile')}>
            👤 โปรไฟล์
          </button>
        )}
        
        <button onClick={onLogout} style={{ padding: '8px 16px', background: '#ef4444', color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer', marginLeft: '10px' }}>
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

  useEffect(() => {
    const savedUser = localStorage.getItem('user');
    if (savedUser) setUser(JSON.parse(savedUser));
    setLoading(false);
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('user');
    setUser(null);
    window.location.href = '/login'; 
  };

  const handleLogin = (userData) => {
    setUser(userData);
    localStorage.setItem('user', JSON.stringify(userData));
  };

  if (loading) return <div style={{padding:'20px'}}>⏳ Loading...</div>;

  return (
    <Router>
      <div style={{ fontFamily: "'Kanit', sans-serif", minHeight: '100vh', background: '#F8FAFC' }}>
        
        {user && <Navbar user={user} onLogout={handleLogout} />}

        <Routes>
          {/* ✅ 1. แก้ตรงนี้: ถ้า Login แล้ว ให้ไป /guide ก่อนเสมอ */}
          <Route 
            path="/login" 
            element={!user ? <LoginPage onLoginSuccess={handleLogin} /> : <Navigate to="/guide" />} 
          />

          {/* ✅ 2. หน้า Guide (ต้องอยู่ก่อน wildcard *) */}
          <Route path="/guide" element={<SkinGuide />} />

          {/* ✅ 3. หน้า Advisor (ผมเปลี่ยน path เป็น /advisor ให้สั้นลง) */}
          <Route 
            path="/advisor" 
            element={user ? <SkinCareAdvisor user={user} /> : <Navigate to="/login" />} 
          />
          {/* รองรับชื่อเก่าเผื่อหลง */}
          <Route path="/skincare-advisor" element={<Navigate to="/advisor" />} />

          {/* ✅ 4. หน้า Profile */}
          <Route 
            path="/profile" 
            element={user ? <UserProfile user={user} /> : <Navigate to="/login" />} 
          />

          {/* ✅ 5. หน้า Admin */}
          <Route 
            path="/admin" 
            element={user && user.role === 'admin' ? <AdminPage user={user} /> : <Navigate to="/advisor" />} 
          />
          
          {/* ✅ 6. ถ้าพิมพ์มั่ว หรือหาไม่เจอ ให้ไปหน้า advisor */}
          <Route path="*" element={<Navigate to={user ? "/advisor" : "/login"} />} />

          
          
        </Routes>

      </div>
    </Router>
  );
}

export default App;