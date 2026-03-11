-- ================================================================
-- schema.sql
-- ================================================================

CREATE TABLE IF NOT EXISTS users (
    id         SERIAL PRIMARY KEY,
    email      VARCHAR(255) UNIQUE NOT NULL,
    password   VARCHAR(255) NOT NULL,
    name       VARCHAR(255),
    role       VARCHAR(20) DEFAULT 'user',
    birthdate  DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS products (
    id               SERIAL PRIMARY KEY,
    product_url      TEXT,
    name             TEXT NOT NULL,
    brand            TEXT,
    major_category   TEXT,
    subtype          TEXT,
    price            DECIMAL(10,2),
    rating           DECIMAL(3,2),
    rating_count     INTEGER,
    active_tags      TEXT,
    function_tags    TEXT,
    ingredients_raw  TEXT,
    ingredients_list TEXT,
    image_url        TEXT,
    image_local      TEXT,
    skintype         TEXT,
    created_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- migrate: ถ้า products มี VARCHAR อยู่ให้แปลงเป็น TEXT อัตโนมัติ
ALTER TABLE products ALTER COLUMN brand          TYPE TEXT;
ALTER TABLE products ALTER COLUMN major_category TYPE TEXT;
ALTER TABLE products ALTER COLUMN subtype        TYPE TEXT;
ALTER TABLE products ALTER COLUMN image_url      TYPE TEXT;
ALTER TABLE products ALTER COLUMN image_local    TYPE TEXT;
ALTER TABLE products ALTER COLUMN skintype       TYPE TEXT;
ALTER TABLE products ALTER COLUMN product_url    TYPE TEXT;
ALTER TABLE products ALTER COLUMN name           TYPE TEXT;

CREATE TABLE IF NOT EXISTS history (
    id                   SERIAL PRIMARY KEY,
    user_email           VARCHAR(255),
    skin_type            VARCHAR(50),
    concerns             JSONB,
    recommended_products JSONB,
    history_type         VARCHAR(20) DEFAULT 'recommend',
    routine_products     JSONB,
    timestamp            TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

ALTER TABLE history ADD COLUMN IF NOT EXISTS history_type     VARCHAR(20) DEFAULT 'recommend';
ALTER TABLE history ADD COLUMN IF NOT EXISTS routine_products JSONB;

CREATE TABLE IF NOT EXISTS bookmarks (
    id             SERIAL PRIMARY KEY,
    user_email     VARCHAR(255) NOT NULL,
    product_name   TEXT NOT NULL,
    brand          TEXT,
    major_category TEXT,
    skintype       TEXT,
    function_tags  TEXT,
    image_url      TEXT,
    price          NUMERIC,
    created_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_email, product_name)
);

CREATE TABLE IF NOT EXISTS reviews (
    id           SERIAL PRIMARY KEY,
    user_email   VARCHAR(255) NOT NULL,
    user_name    VARCHAR(255),
    product_name TEXT NOT NULL,
    brand        TEXT,
    rating       INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    title        TEXT,
    body         TEXT,
    created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_email, product_name)
);

CREATE INDEX IF NOT EXISTS idx_reviews_product ON reviews(product_name);