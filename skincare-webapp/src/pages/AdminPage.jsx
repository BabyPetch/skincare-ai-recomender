import React, { useState, useEffect } from 'react';
import { styles } from '../styles'; // ดึง Styles ที่เราแยกไว้มาใช้
import { PRODUCT_TYPE_OPTIONS } from '../constants/options';

export default function AdminPage() {
    const [products, setProducts] = useState([]);
    const [loading, setLoading] = useState(false);
    const [formData, setFormData] = useState({
        name: '',
        brand: '',
        price: '',
        type_of_product: 'Serum (เซรั่ม)',
        skintype: '',
        'คุณสมบัติ(จากactive ingredients)': ''
    });

    // 1. ฟังก์ชันดึงรายการสินค้าทั้งหมดมาโชว์
    const fetchProducts = async () => {
        try {
            const response = await fetch('http://localhost:5000/api/products');
            const data = await response.json();
            if (data.success) setProducts(data.products);
        } catch (error) {
            console.error("Fetch error:", error);
        }
    };

    useEffect(() => {
        fetchProducts();
    }, []);

    // 2. ฟังก์ชันส่งข้อมูลไปบันทึก (POST)
    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        try {
            const response = await fetch('http://localhost:5000/api/products', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    ...formData, 
                    'price (bath)': Number(formData.price) 
                })
            });
            const data = await response.json();
            if (data.success) {
                alert('บันทึกสำเร็จ!');
                setFormData({ name: '', brand: '', price: '', type_of_product: 'Serum (เซรั่ม)', skintype: '', 'คุณสมบัติ(จากactive ingredients)': '' });
                fetchProducts(); // อัปเดตตารางทันที
            }
        } catch (error) {
            alert('เกิดข้อผิดพลาดในการบันทึก');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div style={{ padding: '20px', maxWidth: '1000px', margin: '0 auto' }}>
            <h1 style={styles.header}>⚙️ ระบบจัดการข้อมูล (Admin)</h1>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
                
                {/* --- ฝั่งซ้าย: ฟอร์มเพิ่มสินค้า --- */}
                <div style={styles.card}>
                    <h3>➕ เพิ่มสินค้าใหม่</h3>
                    <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                        <label>ชื่อสินค้า:</label>
                        <input style={styles.btnOption} value={formData.name} onChange={e => setFormData({...formData, name: e.target.value})} required />
                        
                        <label>แบรนด์:</label>
                        <input style={styles.btnOption} value={formData.brand} onChange={e => setFormData({...formData, brand: e.target.value})} required />
                        
                        <label>ราคา (บาท):</label>
                        <input style={styles.btnOption} type="number" value={formData.price} onChange={e => setFormData({...formData, price: e.target.value})} required />
                        
                        <label>ประเภท:</label>
                        <select style={styles.btnOption} value={formData.type_of_product} onChange={e => setFormData({...formData, type_of_product: e.target.value})}>
                            {PRODUCT_TYPE_OPTIONS.map(opt => <option key={opt} value={opt}>{opt}</option>)}
                        </select>

                        <label>เหมาะกับผิวประเภท (แยกด้วยคอมม่า):</label>
                        <input style={styles.btnOption} placeholder="เช่น ผิวมัน, ผิวผสม" value={formData.skintype} onChange={e => setFormData({...formData, skintype: e.target.value})} />

                        <label>คุณสมบัติเด่น:</label>
                        <textarea style={{...styles.btnOption, height: '80px'}} value={formData['คุณสมบัติ(จากactive ingredients)']} onChange={e => setFormData({...formData, 'คุณสมบัติ(จากactive ingredients)': e.target.value})} />

                        <button type="submit" disabled={loading} style={styles.btnPrimary}>
                            {loading ? 'กำลังบันทึก...' : '🚀 บันทึกลงฐานข้อมูล'}
                        </button>
                    </form>
                </div>

                {/* --- ฝั่งขวา: รายการสินค้าปัจจุบัน --- */}
                <div style={{ ...styles.card, overflowY: 'auto', maxHeight: '600px' }}>
                    <h3>📦 สินค้าในระบบทั้งหมด ({products.length})</h3>
                    <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '14px' }}>
                        <thead>
                            <tr style={{ borderBottom: '2px solid #eee', textAlign: 'left' }}>
                                <th style={{ padding: '8px' }}>ชื่อ/แบรนด์</th>
                                <th style={{ padding: '8px' }}>ราคา</th>
                                <th style={{ padding: '8px' }}>จัดการ</th>
                            </tr>
                        </thead>
                        <tbody>
                            {products.map(p => (
                                <tr key={p.id} style={{ borderBottom: '1px solid #f9f9f9' }}>
                                    <td style={{ padding: '8px' }}>
                                        <b>{p.name}</b> <br/>
                                        <small style={{ color: '#666' }}>{p.brand}</small>
                                    </td>
                                    <td style={{ padding: '8px' }}>{p['price (bath)']} ฿</td>
                                    <td style={{ padding: '8px' }}>
                                        <button style={{ color: 'red', border: 'none', background: 'none', cursor: 'pointer' }}>ลบ</button>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>

            </div>
        </div>
    );
}   