import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import './Navbar.css';

const Navbar = ({ user, onLogout }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const isActive = (path) => location.pathname === path;

  const getBtnClass = (path) =>
    `nav-btn ${isActive(path) ? 'active' : ''}`;

  return (
    <nav className="navbar">
      <div className="navbar-left">
        <h3
          className="navbar-title"
          onClick={() =>
            navigate(user?.role === 'admin' ? '/admin' : '/advisor')
          }
        >
          SkinCare AI ✨
        </h3>

        <span className="navbar-user">
          สวัสดี, {user?.name || 'Guest'}
          {user?.role === 'admin' && (
            <span className="admin-badge"> (Admin)</span>
          )}
        </span>
      </div>

      <div className="navbar-right">
        {user?.role !== 'admin' && (
          <button
            onClick={() => navigate('/advisor')}
            className={getBtnClass('/advisor')}
          >
            🔍 วิเคราะห์ผิว
          </button>
        )}

        {user?.role === 'admin' && (
          <button
            onClick={() => navigate('/admin')}
            className={getBtnClass('/admin')}
          >
            👑 ระบบหลังบ้าน
          </button>
        )}

        {user?.role !== 'guest' && user?.role !== 'admin' && (
          <button
            onClick={() => navigate('/profile')}
            className={getBtnClass('/profile')}
          >
            👤 โปรไฟล์
          </button>
        )}

        <button onClick={onLogout} className="logout-btn">
          ออกจากระบบ
        </button>
      </div>
    </nav>
  );
};

export default Navbar;
