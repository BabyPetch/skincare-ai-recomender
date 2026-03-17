import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useTheme } from '../../context/ThemeContext';
import './Navbar.css';

const Navbar = ({ user, onLogout }) => {
  const navigate   = useNavigate();
  const location   = useLocation();
  const { dark, toggle } = useTheme();

  const isActive    = (path) => location.pathname === path;
  const getBtnClass = (path) => `nav-btn ${isActive(path) ? 'active' : ''}`;

  return (
    <nav className="navbar">
      <div className="navbar-left">
        <h3 className="navbar-title"
          onClick={() => navigate(user?.role === 'admin' ? '/admin' : '/advisor')}>
          SkinCare AI ✨
        </h3>
        <span className="navbar-user">
          สวัสดี, {user?.name || 'Guest'}
          {user?.role === 'admin' && <span className="admin-badge"> (Admin)</span>}
        </span>
      </div>

      <div className="navbar-right">
        {user?.role !== 'admin' && (
          <button onClick={() => navigate('/advisor')} className={getBtnClass('/advisor')}>
            วิเคราะห์ผิว
          </button>
        )}
              
        {user?.role !== 'guest' && (
          <button onClick={() => navigate('/dashboard')} className={getBtnClass('/dashboard')}>
            📊 Dashboard
          </button>
        )}

        <button onClick={() => navigate('/search')} className={getBtnClass('/search')}>
          🔍 ค้นหาสินค้า
        </button>
        {user?.role !== 'admin' && user?.role !== 'guest' && (
          <button onClick={() => navigate('/bookmarks')} className={getBtnClass('/bookmarks')}>
            🔖 บันทึกไว้
          </button>
        )}
        {user?.role === 'admin' && (
          <button onClick={() => navigate('/admin')} className={getBtnClass('/admin')}>
            👑 ระบบหลังบ้าน
          </button>
        )}
        {user?.role !== 'guest' && user?.role !== 'admin' && (
          <button onClick={() => navigate('/profile')} className={getBtnClass('/profile')}>
            👤 โปรไฟล์
          </button>
        )}

        {/* Dark Mode Toggle */}
        <button onClick={toggle} className="theme-toggle" title={dark ? 'เปลี่ยนเป็น Light Mode' : 'เปลี่ยนเป็น Dark Mode'}>
          <span className="theme-toggle-track">
            <span className="theme-toggle-thumb">{dark ? '🌙' : '☀️'}</span>
          </span>
        </button>

        <button onClick={onLogout} className="logout-btn">ออกจากระบบ</button>
      </div>
    </nav>
  );
};

export default Navbar;