CREATE TABLE IF NOT EXISTS bookmarks (
    id           SERIAL PRIMARY KEY,
    user_email   VARCHAR(255) NOT NULL,
    product_name VARCHAR(255) NOT NULL,
    brand        VARCHAR(255),
    major_category VARCHAR(255),
    skintype     VARCHAR(255),
    function_tags TEXT,
    image_url    TEXT,
    price        NUMERIC,
    created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_email, product_name)
);