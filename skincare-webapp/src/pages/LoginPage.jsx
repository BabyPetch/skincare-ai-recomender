import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom'; // 1. ต้องมีตัวนี้
import { loginUser, registerUser } from '../services/api'; 
import './LoginPage.css'; 

const LoginPage = ({ onLoginSuccess }) => {
  const navigate = useNavigate(); // 2. ประกาศตัวแปร
  const [isLogin, setIsLogin] = useState(true);
  
  // State
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [name, setName] = useState('');
  const [birthdate, setBirthdate] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    try {
      if (isLogin) {
        // --- 🟢 ล็อกอิน ---
        const data = await loginUser({ email, password });
        
        onLoginSuccess(data.user); 
        
        // 👑 3. เพิ่มการเช็ค Role ตรงนี้
        if (data.user.role === 'admin') {
          navigate('/admin'); // ถ้าเป็นแอดมิน ให้เด้งไปหน้าแอดมิน
        } else {
          navigate('/guide'); // ถ้าเป็น user ทั่วไป ให้ไปหน้า Guide
        }

      } else {
        // --- 🔵 สมัครสมาชิก ---
        await registerUser({ name, email, password, birthdate });
        alert('สมัครสมาชิกสำเร็จ! กรุณาล็อกอิน');
        setIsLogin(true);
        setPassword('');
        setBirthdate('');
      }
    } catch (err) {
      console.error(err);
      setError('อีเมล/รหัสผ่านไม่ถูกต้อง หรือเชื่อมต่อ Server ไม่ได้');
    }
  };

  // Guest Login
  const handleGuestLogin = () => {
    onLoginSuccess({ name: 'Guest', role: 'guest', age: 25 });

    // 4. Guest ก็สั่งให้ไปหน้า Guide เหมือนกัน
    navigate('/guide');
  };

  return (
    <div className="login-container">
      <div className="login-card">
        <h2 className="login-title">
          {isLogin ? 'ยินดีต้อนรับ' : 'สมัครสมาชิกใหม่ ✨'}
        </h2>

        {error && <div className="error-message">{error}</div>}

        <form onSubmit={handleSubmit} className="login-form">
          {!isLogin && (
            <input 
              className="form-input"
              type="text" 
              placeholder="ชื่อของคุณ" 
              required
              value={name} 
              onChange={e => setName(e.target.value)}
            />
          )}

          <input 
            className="form-input"
            type="email" 
            placeholder="อีเมล" 
            required
            value={email} 
            onChange={e => setEmail(e.target.value)}
          />

          <input 
            className="form-input"
            type="password" 
            placeholder="รหัสผ่าน" 
            required
            value={password} 
            onChange={e => setPassword(e.target.value)}
          />

          {!isLogin && (
            <div className="form-group">
              <label>วันเดือนปีเกิด:</label>
              <input 
                className="form-input"
                type="date" 
                required
                value={birthdate} 
                onChange={e => setBirthdate(e.target.value)}
              />
            </div>
          )}

          <button type="submit" className="btn-primary">
            {isLogin ? 'เข้าสู่ระบบ' : 'สมัครสมาชิก'}
          </button>
        </form>

        <div className="toggle-container">
          {isLogin ? "ยังไม่มีบัญชี? " : "มีบัญชีแล้ว? "}
          <span 
            className="toggle-link"
            onClick={() => { setIsLogin(!isLogin); setError(''); }}
          >
            {isLogin ? 'สมัครเลย' : 'เข้าสู่ระบบ'}
          </span>
        </div>

        {isLogin && (
          <div className="divider">
              <button onClick={handleGuestLogin} className="btn-guest">
                เข้าใช้งานแบบ Guest (ไม่ต้องสมัคร)
              </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default LoginPage;