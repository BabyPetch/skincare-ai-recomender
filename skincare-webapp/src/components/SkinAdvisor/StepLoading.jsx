import React from 'react';

const StepLoading = ({ userAge }) => {
  return (
    <div className="loading-screen">
      <div className="loading-spinner"></div>
      <h3>AI กำลังประมวลผล...</h3>
      <p>กำลังค้นหาสกินแคร์รูทีนที่เหมาะกับวัย {userAge || 25} ปี ของคุณ</p>
    </div>
  );
};

export default StepLoading;