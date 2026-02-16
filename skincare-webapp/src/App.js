import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';

// Import Pages
import SkinCareAdvisor from './pages/SkinCareAdvisor';
import AdminPage from './pages/AdminPage';
import LoginPage from './pages/LoginPage';
import UserProfile from './pages/UserProfile';
import SkinGuide from './pages/SkinGuide';

// Import Navbar ที่แยกไฟล์ออกไปแล้ว
import Navbar from './components/์Navbar/Navbar'; 

function App() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // โหลดข้อมูลการล็อกอินจาก LocalStorage
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
        
        {/* เรียกใช้งาน Navbar โดยส่ง user และฟังก์ชัน handleLogout ไปให้ */}
        {user && <Navbar user={user} onLogout={handleLogout} />}

        <Routes>
          {/* ✅ หน้า Login */}
          <Route 
            path="/login" 
            element={
              !user ? (
                <LoginPage onLoginSuccess={handleLogin} />
              ) : user.role === 'admin' ? (
                <Navigate to="/admin" />
              ) : (
                <Navigate to="/guide" />
              )
            } 
          />

          {/* ✅ หน้า Guide สำหรับ User */}
          <Route 
            path="/guide" 
            element={user && user.role !== 'admin' ? <SkinGuide /> : <Navigate to={user ? "/admin" : "/login"} />} 
          />

          {/* ✅ หน้า Advisor สำหรับ User */}
          <Route 
            path="/advisor" 
            element={user && user.role !== 'admin' ? <SkinCareAdvisor user={user} /> : <Navigate to={user ? "/admin" : "/login"} />} 
          />
          <Route path="/skincare-advisor" element={<Navigate to="/advisor" />} />

          {/* ✅ หน้า Profile สำหรับ User */}
          <Route 
            path="/profile" 
            element={user && user.role !== 'admin' ? <UserProfile user={user} /> : <Navigate to={user ? "/admin" : "/login"} />} 
          />

          {/* ✅ หน้า Admin สำหรับ Admin เท่านั้น */}
          <Route 
            path="/admin" 
            element={user && user.role === 'admin' ? <AdminPage user={user} /> : <Navigate to="/advisor" />} 
          />
          
          {/* ✅ จัดการ Route มั่วๆ */}
          <Route 
            path="*" 
            element={<Navigate to={!user ? "/login" : user.role === 'admin' ? "/admin" : "/advisor"} />} 
          />
          
        </Routes>
      </div>
    </Router>
  );
}

export default App;