import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { loginUser, registerUser } from '../services/api';
import './LoginPage.css';

const LoginPage = ({ onLoginSuccess }) => {
  const navigate = useNavigate();
  const [isLogin, setIsLogin] = useState(true);

  const [email,     setEmail]     = useState('');
  const [password,  setPassword]  = useState('');
  const [name,      setName]      = useState('');
  const [birthdate, setBirthdate] = useState('');
  const [gender,    setGender]    = useState('other');
  const [error,     setError]     = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    try {
      if (isLogin) {
        const data = await loginUser({ email, password });
        onLoginSuccess(data.user);
        navigate(data.user.role === 'admin' ? '/admin' : '/guide');
      } else {
        await registerUser({ name, email, password, birthdate, gender });
        alert('สมัครสมาชิกสำเร็จ! กรุณาล็อกอิน');
        setIsLogin(true);
        setPassword('');
        setBirthdate('');
        setGender('other');
      }
    } catch (err) {
      console.error(err);
      setError('อีเมล/รหัสผ่านไม่ถูกต้อง หรือเชื่อมต่อ Server ไม่ได้');
    }
  };

  const handleGuestLogin = () => {
    onLoginSuccess({ name: 'Guest', role: 'guest', age: 25, gender: 'other' });
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
            <>
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

              <div className="form-group">
                <label>เพศ:</label>
                <select
                  className="form-input"
                  value={gender}
                  onChange={e => setGender(e.target.value)}
                >
                  <option value="other">ไม่ระบุ</option>
                  <option value="female">หญิง</option>
                  <option value="male">ชาย</option>
                </select>
              </div>
            </>
          )}

          <button type="submit" className="btn-primary">
            {isLogin ? 'เข้าสู่ระบบ' : 'สมัครสมาชิก'}
          </button>
        </form>

        <div className="toggle-container">
          {isLogin ? 'ยังไม่มีบัญชี? ' : 'มีบัญชีแล้ว? '}
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