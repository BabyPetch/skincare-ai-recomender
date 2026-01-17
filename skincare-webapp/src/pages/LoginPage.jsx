import React, { useState } from 'react';
import { styles } from '../styles';

export default function LoginPage({ onLoginSuccess }) {
    const [isRegister, setIsRegister] = useState(false);
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [name, setName] = useState('');

    const handleAuth = async (e) => {
        e.preventDefault();
        const endpoint = isRegister ? 'register' : 'login';
        try {
        const res = await fetch(`http://localhost:5000/api/${endpoint}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password, name, role: 'user' })
        });
        const data = await res.json();
        if (data.success) {
            if (isRegister) {
            alert("สมัครสมาชิกสำเร็จ! กรุณาล็อกอิน");
            setIsRegister(false);
            } else {
            onLoginSuccess(data.user); // ส่งข้อมูล user กลับไปที่ App.js
            }
        } else {
            alert(data.message);
        }
        } catch (err) { alert("เชื่อมต่อเซิร์ฟเวอร์ไม่ได้"); }
    };

    return (
        <div style={styles.container}>
        <div style={{...styles.card, maxWidth: '400px'}}>
            <h2 style={styles.header}>{isRegister ? 'สมัครสมาชิก' : 'เข้าสู่ระบบ'}</h2>
            <form onSubmit={handleAuth} style={{display: 'flex', flexDirection: 'column', gap: '1rem'}}>
            {isRegister && (
                <input style={styles.btnOption} placeholder="ชื่อของคุณ" onChange={e => setName(e.target.value)} required />
            )}
            <input style={styles.btnOption} type="email" placeholder="อีเมล" onChange={e => setEmail(e.target.value)} required />
            <input style={styles.btnOption} type="password" placeholder="รหัสผ่าน" onChange={e => setPassword(e.target.value)} required />
            
            <button type="submit" style={styles.btnPrimary}>
                {isRegister ? 'ยืนยันการสมัคร' : 'ล็อกอิน'}
            </button>
            </form>

            <div style={{textAlign: 'center', marginTop: '1.5rem'}}>
            <p onClick={() => setIsRegister(!isRegister)} style={{cursor: 'pointer', color: '#9333ea'}}>
                {isRegister ? 'มีบัญชีอยู่แล้ว? เข้าสู่ระบบ' : 'ยังไม่มีบัญชี? สมัครสมาชิกที่นี่'}
            </p>
            <hr style={{margin: '1rem 0', opacity: 0.2}} />
            <button 
                onClick={() => onLoginSuccess({ name: 'Guest', role: 'guest' })} 
                style={{...styles.btnBack, width: '100%'}}
            >
                เข้าใช้งานแบบ Guest (ไม่บันทึกข้อมูล)
            </button>
            </div>
        </div>
        </div>
    );
}