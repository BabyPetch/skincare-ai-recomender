import React, { useState } from 'react';
import AdvisorPage from './pages/SkinCareAdvisor';
import AdminPage from './pages/AdminPage';
import LoginPage from './pages/LoginPage';

function App() {
  const [user, setUser] = useState(null); // เก็บข้อมูลคนล็อกอิน
  const [currentPage, setCurrentPage] = useState('user');

  // ถ้ายังไม่ล็อกอิน ให้โชว์หน้า Login
  if (!user) {
    return <LoginPage onLoginSuccess={(userData) => setUser(userData)} />;
  }

  return (
    <div>
      <nav style={{ padding: '15px', background: '#1e293b', color: 'white', display: 'flex', justifyContent: 'space-between' }}>
        <div>
           <span>ยินดีต้อนรับคุณ {user.name} </span>
           {user.role === 'guest' && <small>(Guest Mode)</small>}
        </div>
        <div>
          <button onClick={() => setCurrentPage('user')}>🔍 วิเคราะห์ผิว</button>
          
          {/* เฉพาะคนที่ไม่ใช่ Guest และอาจจะเป็น Admin ถึงจะเห็นปุ่มนี้ */}
          {user.role === 'admin' && (
            <button onClick={() => setCurrentPage('admin')}>⚙️ จัดการสินค้า</button>
          )}
          
          <button onClick={() => setUser(null)} style={{marginLeft: '10px', background: '#ef4444'}}>ออกจากระบบ</button>
        </div>
      </nav>

      <main>
        {currentPage === 'user' ? <AdvisorPage user={user} /> : <AdminPage />}
      </main>
    </div>
  );
}

export default App;