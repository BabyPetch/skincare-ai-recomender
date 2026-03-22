import React from 'react';
import { useNavigate } from 'react-router-dom';
import './SkinGuide.css';

const SkinGuide = () => {
    const navigate = useNavigate();

    return (
        <div className="guide-page">
        <div className="guide-header">
            <h1>เช็คสภาพผิวเบื้องต้น</h1>
            <p>เลือกวิธีทดสอบที่สะดวก แล้วจำผลลัพธ์ไว้ใช้วิเคราะห์นะครับ</p>
        </div>

        <div className="cards-container">
            
            {/* --- Card 1: วิธีล้างหน้า (ใส่กล่องสีตามแบบ) --- */}
            <div className="guide-card">
            <div className="card-top">
                <h3 className="card-title">1. วิธีล้างหน้าแล้วรอดูผล <br/><span>(Bare Face Test)</span></h3>
                <p className="card-steps">
                1. ล้างหน้าด้วยคลีนเซอร์ที่อ่อนโยน <br/>
                2. ซับหน้าให้แห้ง <b>งดทาครีมทุกชนิด</b> <br/>
                3. รอ 30–60 นาที แล้วสังเกตผิว
                </p>
            </div>
            
            {/* Grid กล่องสีพาสเทล (เหมือนรูปตัวอย่าง) */}
            <div className="skin-type-grid">
                <div className="type-box box-oily">
                <div>
                    <strong>ผิวมัน</strong>
                    <span>มันวาวทั่วใบหน้า</span>
                </div>
                </div>
                <div className="type-box box-dry">
                <div>
                    <strong>ผิวแห้ง</strong>
                    <span>แห้ง ตึง ลอกเป็นขุย</span>
                </div>
                </div>
                <div className="type-box box-combi">
                <div>
                    <strong>ผิวผสม</strong>
                    <span>มันแค่ T-zone แก้มแห้ง</span>
                </div>
                </div>
                <div className="type-box box-normal">
                <div>
                    <strong>ผิวธรรมดา</strong>
                    <span>ไม่มัน ไม่ตึง</span>
                </div>
                </div>
                <div className="type-box box-sensitive">
                <div>
                    <strong>แพ้ง่าย</strong>
                    <span>แสบ คัน แดงง่าย</span>
                </div>
                </div>
            </div>
            </div>

            {/* --- Card 2: กระดาษซับมัน (ปรับสไตล์ให้เข้ากัน) --- */}
            <div className="guide-card">
            <div className="card-top">
                <h3 className="card-title">2. ใช้กระดาษซับมัน <br/><span>(Blotting Paper)</span></h3>
                <p className="card-steps">
                แปะกระดาษที่ หน้าผาก, จมูก, แก้ม, คาง ทิ้งไว้สักพักแล้วส่องกับไฟ
                </p>
            </div>
            <div className="skin-type-grid">
                <div className="type-box box-oily">
                    <div><strong>มันทุกแผ่น</strong> = ผิวมัน</div>
                </div>
                <div className="type-box box-combi">
                    <div><strong>มันบางจุด</strong> = ผิวผสม</div>
                </div>
                <div className="type-box box-dry">
                    <div><strong>ไม่มันเลย</strong> = ผิวแห้ง</div>
                </div>
            </div>
            </div>

            {/* --- Card 3: ผิวขาดน้ำ --- */}
            <div className="guide-card">
            <div className="card-top">
                <h3 className="card-title">3. เช็คผิวขาดน้ำ <br/><span>(Dehydrated Skin)</span></h3>
                <p className="card-steps" style={{color:'#d97706'}}>
                ⚠️ เกิดได้กับทุกคน (แม้แต่คนผิวมัน) อาการคือ "หน้ามันแต่ผิวลอก"
                </p>
            </div>
            <div className="type-box box-warning" >
                <div className="box-icon">👉</div>
                <div>
                <strong>วิธีทดสอบ:</strong> ใช้นิ้วดันแก้มขึ้นเบาๆ<br/>
                <span style={{color:'#c2410c'}}>*ถ้าย่นเป็นริ้วเล็กๆ = ขาดน้ำ</span>
                </div>
            </div>
            </div>

        </div>

        <div className="guide-footer">
            <button className="btn-start" onClick={() => navigate('/advisor')}>
            <span>พร้อมแล้ว! ไปเริ่มวิเคราะห์ผิว</span> ➜
            </button>
        </div>
        </div>
    );
};

export default SkinGuide;