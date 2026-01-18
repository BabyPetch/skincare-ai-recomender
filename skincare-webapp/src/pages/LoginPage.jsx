import React, { useState } from 'react';

const LoginPage = ({ onLoginSuccess }) => {
  const [isLogin, setIsLogin] = useState(true);
  
  // State สำหรับ Form
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [name, setName] = useState('');
  const [birthdate, setBirthdate] = useState(''); // <--- เพิ่ม state วันเกิด
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    const endpoint = isLogin ? '/api/login' : '/api/register';
    const body = isLogin 
      ? { email, password }
      : { name, email, password, birthdate }; // <--- ส่งวันเกิดไปด้วยตอนสมัคร

    try {
      const res = await fetch(`http://127.0.0.1:5000${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
      });
      const data = await res.json();

      if (data.success) {
        if (isLogin) {
          onLoginSuccess(data.user);
        } else {
          alert('สมัครสมาชิกสำเร็จ! กรุณาล็อกอิน');
          setIsLogin(true);
          // เคลียร์ฟอร์ม
          setBirthdate(''); setName(''); setPassword('');
        }
      } else {
        setError(data.message);
      }
    } catch (err) {
      setError('เชื่อมต่อ Server ไม่ได้');
    }
  };

  // Guest Login
  const handleGuestLogin = () => {
    onLoginSuccess({ name: 'Guest', role: 'guest', age: 25 });
  };

  return (
    <div style={{ 
      height: '100vh', display: 'flex', justifyContent: 'center', alignItems: 'center', 
      background: 'linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)', fontFamily: "'Kanit', sans-serif" 
    }}>
      <div style={{ 
        background: 'white', padding: '40px', borderRadius: '20px', 
        boxShadow: '0 10px 25px rgba(0,0,0,0.1)', width: '100%', maxWidth: '400px' 
      }}>
        <h2 style={{ textAlign: 'center', color: '#1e293b', marginBottom: '20px' }}>
          {isLogin ? 'ยินดีต้อนรับ 👋' : 'สมัครสมาชิกใหม่ ✨'}
        </h2>

        {error && <p style={{ color: 'red', textAlign: 'center', fontSize: '14px' }}>{error}</p>}

        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>
          
          {/* ช่องชื่อ (แสดงเฉพาะตอนสมัคร) */}
          {!isLogin && (
            <input 
              type="text" placeholder="ชื่อของคุณ" required
              value={name} onChange={e => setName(e.target.value)}
              style={styles.input}
            />
          )}

          <input 
            type="email" placeholder="อีเมล" required
            value={email} onChange={e => setEmail(e.target.value)}
            style={styles.input}
          />

          <input 
            type="password" placeholder="รหัสผ่าน" required
            value={password} onChange={e => setPassword(e.target.value)}
            style={styles.input}
          />

          {/* ช่องวันเกิด (แสดงเฉพาะตอนสมัคร) */}
          {!isLogin && (
            <div>
              <label style={{ fontSize: '12px', color: '#64748b', marginLeft: '5px' }}>วันเดือนปีเกิด:</label>
              <input 
                type="date" required
                value={birthdate} onChange={e => setBirthdate(e.target.value)}
                style={styles.input}
              />
            </div>
          )}

          <button type="submit" style={styles.primaryBtn}>
            {isLogin ? 'เข้าสู่ระบบ' : 'สมัครสมาชิก'}
          </button>
        </form>

        <div style={{ marginTop: '20px', textAlign: 'center', fontSize: '14px' }}>
          {isLogin ? "ยังไม่มีบัญชี? " : "มีบัญชีแล้ว? "}
          <span 
            onClick={() => { setIsLogin(!isLogin); setError(''); }}
            style={{ color: '#4f46e5', cursor: 'pointer', fontWeight: 'bold' }}
          >
            {isLogin ? 'สมัครเลย' : 'เข้าสู่ระบบ'}
          </span>
        </div>

        {isLogin && (
          <div style={{ marginTop: '20px', borderTop: '1px solid #eee', paddingTop: '20px' }}>
             <button onClick={handleGuestLogin} style={styles.guestBtn}>
               เข้าใช้งานแบบ Guest (ไม่ต้องสมัคร)
             </button>
          </div>
        )}
      </div>
    </div>
  );
};

const styles = {
  input: {
    padding: '12px', borderRadius: '8px', border: '1px solid #e2e8f0', fontSize: '16px', outline: 'none', width: '100%', boxSizing: 'border-box'
  },
  primaryBtn: {
    padding: '12px', borderRadius: '8px', border: 'none', background: '#4f46e5', color: 'white', fontSize: '16px', fontWeight: 'bold', cursor: 'pointer', marginTop: '10px'
  },
  guestBtn: {
    width: '100%', padding: '10px', borderRadius: '8px', border: '1px solid #cbd5e1', background: 'transparent', color: '#64748b', cursor: 'pointer'
  }
};

export default LoginPage;