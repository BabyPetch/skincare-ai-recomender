import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js';
import { Pie } from 'react-chartjs-2';
import './AdminPage.css';

// ลงทะเบียน Component สำหรับกราฟวงกลม
ChartJS.register(ArcElement, Tooltip, Legend);

const AdminPage = ({ user }) => {
    const [users, setUsers] = useState([]);
    const [activeTab, setActiveTab] = useState('dashboard'); // ✅ state สำหรับสลับหน้า
    const navigate = useNavigate();

    useEffect(() => {
        // 🛡️ ป้องกันคนที่ไม่ใช่ Admin เข้ามา
        if (!user || user.role !== 'admin') {
        alert("คุณไม่มีสิทธิ์เข้าถึงหน้านี้!");
        navigate('/');
        return;
        }
        fetchUsers();
    }, [user, navigate]);

    const fetchUsers = async () => {
        try {
        const res = await fetch('http://127.0.0.1:5000/api/admin/users');
        const data = await res.json();
        setUsers(data);
        } catch (error) {
        console.error("Error fetching users:", error);
        }
    };

    const handleDelete = async (email) => {
        if (!window.confirm(`คุณแน่ใจหรือไม่ว่าจะลบผู้ใช้ ${email}?`)) return;
        try {
        const res = await fetch(`http://127.0.0.1:5000/api/admin/users/${email}`, {
            method: 'DELETE'
        });
        if (res.ok) {
            alert("ลบเรียบร้อย!");
            fetchUsers();
        } else {
            alert("เกิดข้อผิดพลาดในการลบ");
        }
        } catch (error) {
        console.error("Delete error:", error);
        }
    };

    // --- 📊 ส่วนคำนวณข้อมูล Dashboard ---
    const totalUsers = users.length;
    const adminCount = users.filter(u => u.role === 'admin').length;
    const userCount = users.filter(u => u.role === 'user').length;

    // ข้อมูลกราฟ
    const chartData = {
        labels: ['Admin (ผู้ดูแล)', 'User (สมาชิกทั่วไป)'],
        datasets: [
        {
            data: [adminCount, userCount],
            backgroundColor: ['#4f46e5', '#10b981'],
            borderColor: ['#ffffff', '#ffffff'],
            borderWidth: 2,
        },
        ],
    };

    return (
        <div className="admin-container">
        <div className="admin-header">
            <h1 className="admin-title">👑 Admin Control Panel</h1>
            
            {/* ปุ่มสลับ Tab */}
            <div className="admin-tabs">
            <button 
                className={`tab-btn ${activeTab === 'dashboard' ? 'active' : ''}`}
                onClick={() => setActiveTab('dashboard')}
            >
                📊 ภาพรวม (Dashboard)
            </button>
            <button 
                className={`tab-btn ${activeTab === 'users' ? 'active' : ''}`}
                onClick={() => setActiveTab('users')}
            >
                👥 จัดการสมาชิก
            </button>
            </div>
        </div>

        <div className="admin-content">
            {/* 👉 ส่วนที่ 1: Dashboard View */}
            {activeTab === 'dashboard' && (
            <div className="dashboard-view fadeIn">
                <div className="stats-grid">
                <div className="stat-card blue">
                    <h3>ทั้งหมด</h3>
                    <div className="number">{totalUsers}</div>
                    <p>บัญชีในระบบ</p>
                </div>
                <div className="stat-card green">
                    <h3>สมาชิกทั่วไป</h3>
                    <div className="number">{userCount}</div>
                    <p>Users</p>
                </div>
                <div className="stat-card purple">
                    <h3>ผู้ดูแล</h3>
                    <div className="number">{adminCount}</div>
                    <p>Admins</p>
                </div>
                </div>

                <div className="chart-section">
                <h3>สัดส่วนผู้ใช้งาน</h3>
                <div className="pie-chart-wrapper">
                    <Pie data={chartData} />
                </div>
                </div>
            </div>
            )}

            {/* 👉 ส่วนที่ 2: Users Table View */}
            {activeTab === 'users' && (
            <div className="users-view fadeIn">
                <div className="table-header">
                <h3>รายชื่อสมาชิกทั้งหมด</h3>
                <button className="btn-refresh" onClick={fetchUsers}>🔄 รีเฟรช</button>
                </div>
                <div className="table-responsive">
                <table className="admin-table">
                    <thead>
                    <tr>
                        <th>ชื่อ</th>
                        <th>อีเมล</th>
                        <th>อายุ</th>
                        <th>สถานะ</th>
                        <th>จัดการ</th>
                    </tr>
                    </thead>
                    <tbody>
                    {users.map((u, index) => (
                        <tr key={index}>
                        <td>{u.name}</td>
                        <td>{u.email}</td>
                        <td>{u.age || '-'}</td>
                        <td>
                            <span className={`role-badge ${u.role}`}>
                            {u.role}
                            </span>
                        </td>
                        <td>
                            {u.role !== 'admin' && (
                            <button 
                                className="btn-delete"
                                onClick={() => handleDelete(u.email)}
                            >
                                ลบ
                            </button>
                            )}
                        </td>
                        </tr>
                    ))}
                    </tbody>
                </table>
                </div>
            </div>
            )}
        </div>
        </div>
    );
};

export default AdminPage;