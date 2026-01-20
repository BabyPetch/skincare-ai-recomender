import React from 'react';
import ProductCard from './ProductCard'; // Import การ์ดสินค้าที่เราแยกไว้

const StepResults = ({ results, user, onRestart }) => {
  return (
    <div className="results-content">
      <div className="results-header">
        <div>
          <h2 className="step-title">✨ สกินแคร์รูทีนเพื่อคุณ</h2>
          <p className="step-subtitle">สำหรับ: {user?.name} (อายุ {user?.age} ปี)</p>
        </div>
        <button className="btn-restart" onClick={onRestart}>🔄 เริ่มใหม่</button>
      </div>

      <div className="product-list">
        {Array.isArray(results) && results.length > 0 ? (
          results.map((product, idx) => (
            <ProductCard key={idx} product={product} />
          ))
        ) : (
          <div className="empty-state">
            <span className="empty-icon">😕</span>
            <h3>ไม่พบข้อมูลสินค้า</h3>
            <p>ลองปรับเปลี่ยนเงื่อนไข หรือตรวจสอบการเชื่อมต่อ</p>
            <button className="btn-restart-large" onClick={onRestart}>เริ่มทำแบบทดสอบใหม่</button>
          </div>
        )}
      </div>
    </div>
  );
};

export default StepResults;