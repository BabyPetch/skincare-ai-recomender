import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
// Import Pages
import SkinCareAdvisor from './pages/SkinCareAdvisor';
import AdminPage from './pages/AdminPage';
import LoginPage from './pages/LoginPage';
import UserProfile from './pages/UserProfile';
import SkinGuide from './pages/SkinGuide';
import SearchPage from './pages/SearchPage';
import BookmarkPage from './pages/BookmarkPage';
import DashboardPage from './pages/DashboardPage';
import ComparePage from './pages/ComparePage';

// Import Navbar
import Navbar from './components/์Navbar/Navbar';

function App() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // ⭐ state สำหรับ Compare
  const [compareList, setCompareList] = useState([]);

  // โหลดข้อมูล user จาก LocalStorage
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

  if (loading) return <div style={{ padding: '20px' }}>⏳ Loading...</div>;

  return (
    <Router>
      <div
        style={{
          fontFamily: "'Kanit', sans-serif",
          minHeight: '100vh',
          background: '#F8FAFC'
        }}
      >
        {/* Navbar */}
        {user && (
          <Navbar
            user={user}
            onLogout={handleLogout}
            compareCount={compareList.length}
          />
        )}

        <Routes>
          {/* Login */}
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

          {/* Dashboard */}
          <Route
            path="/dashboard"
            element={
              user ? (
                <DashboardPage
                  user={user}
                  compareList={compareList}
                  setCompareList={setCompareList}
                />
              ) : (
                <Navigate to="/login" />
              )
            }
          />

          {/* Bookmark */}
          <Route
            path="/bookmarks"
            element={
              user ? (
                <BookmarkPage user={user} />
              ) : (
                <Navigate to="/login" />
              )
            }
          />

          {/* Search */}
          <Route
            path="/search"
            element={
              user ? (
                <SearchPage
                  user={user}
                  compareList={compareList}
                  setCompareList={setCompareList}
                />
              ) : (
                <Navigate to="/login" />
              )
            }
          />

          {/* Guide */}
          <Route
            path="/guide"
            element={
              user && user.role !== 'admin' ? (
                <SkinGuide />
              ) : (
                <Navigate to={user ? "/admin" : "/login"} />
              )
            }
          />

          {/* Compare */}
          <Route
            path="/compare"
            element={
              user ? (
                <ComparePage
                  user={user}
                  compareList={compareList}
                  setCompareList={setCompareList}
                />
              ) : (
                <Navigate to="/login" />
              )
            }
          />

          {/* Advisor */}
          <Route
            path="/advisor"
            element={
              user && user.role !== 'admin' ? (
                <SkinCareAdvisor
                  user={user}
                  compareList={compareList}
                  setCompareList={setCompareList}
                />
              ) : (
                <Navigate to={user ? "/admin" : "/login"} />
              )
            }
          />

          <Route path="/skincare-advisor" element={<Navigate to="/advisor" />} />

          {/* Profile */}
          <Route
            path="/profile"
            element={
              user && user.role !== 'admin' ? (
                <UserProfile user={user} />
              ) : (
                <Navigate to={user ? "/admin" : "/login"} />
              )
            }
          />

          {/* Admin */}
          <Route
            path="/admin"
            element={
              user && user.role === 'admin' ? (
                <AdminPage user={user} />
              ) : (
                <Navigate to="/advisor" />
              )
            }
          />

          {/* Default route */}
          <Route
            path="*"
            element={
              <Navigate
                to={!user ? "/login" : user.role === 'admin' ? "/admin" : "/advisor"}
              />
            }
          />
        </Routes>
      </div>
    </Router>
  );
}

export default App;

