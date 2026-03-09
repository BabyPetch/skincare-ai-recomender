CREATE TABLE IF NOT EXISTS reviews (
    id           SERIAL PRIMARY KEY,
    user_email   VARCHAR(255) NOT NULL,
    user_name    VARCHAR(255),
    product_name VARCHAR(255) NOT NULL,
    brand        VARCHAR(255),
    rating       INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    title        VARCHAR(255),
    body         TEXT,
    created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_email, product_name)
);

-- index เพื่อ query เร็วตาม product
CREATE INDEX IF NOT EXISTS idx_reviews_product ON reviews(product_name);