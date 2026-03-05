-- ================================================================
-- schema.sql
-- ================================================================

CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    name VARCHAR(255),
    role VARCHAR(20) DEFAULT 'user',
    birthdate DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS history (
    id SERIAL PRIMARY KEY,
    user_email VARCHAR(255),
    skin_type VARCHAR(50),
    concerns JSONB,
    recommended_products JSONB,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    product_url VARCHAR(500),
    name VARCHAR(255) NOT NULL,
    brand VARCHAR(100),
    major_category VARCHAR(100),
    subtype VARCHAR(100),
    price DECIMAL(10,2),
    rating DECIMAL(3,2),
    rating_count INTEGER,
    active_tags TEXT,
    function_tags TEXT,
    ingredients_raw TEXT,
    ingredients_list TEXT,
    image_url VARCHAR(500),
    image_local VARCHAR(500),
    skintype VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);