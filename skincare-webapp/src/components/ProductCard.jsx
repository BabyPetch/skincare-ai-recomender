// src/components/ProductCard.jsx
export const ProductCard = ({ product, rank, styles }) => {
    const rankIcons = { 1: '🥇', 2: '🥈', 3: '🥉' };
    return (
        <div style={styles.productCard}>
        <span style={styles.rank}>{rankIcons[rank] || ` ${rank}. `}</span>
        <div style={styles.productInfo}>
            <div style={styles.productName}>{product.name}</div>
            <div style={styles.productDetail}>💼 {product.brand}</div>
            <div style={styles.productDetail}>📦 {product.type}</div>
        </div>
        <div style={styles.productPriceContainer}>
            <div style={styles.productPrice}>{product.price.toLocaleString()} ฿</div>
            <div style={styles.productScore}>คะแนน: {product.score}</div>
        </div>
        </div>
    );
    };