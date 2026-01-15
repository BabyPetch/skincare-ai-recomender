// src/App.js
import React, { useState } from 'react';
import AdvisorPage from './pages/SkinCareAdvisor'; 
import AdminPage from './pages/AdminPage';     

function App() {
  const [currentPage, setCurrentPage] = useState('user');

  return (
    <div>
      {/* แถบเมนูสำหรับสลับหน้า */}
      <nav style={{ padding: '15px', background: '#333', color: 'white', textAlign: 'center' }}>
        <button onClick={() => setCurrentPage('user')} style={{ marginRight: '10px' }}>🔍 วิเคราะห์ผิว</button>
        <button onClick={() => setCurrentPage('admin')}>⚙️ จัดการสินค้า</button>
      </nav>

      {/* เลือกแสดงผลหน้าตามที่กด */}
      {currentPage === 'user' ? <AdvisorPage /> : <AdminPage />}
    </div>
  );
}

export default App;