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
    -- ✅ แก้: TIMESTAMP WITH TIME ZONE + DEFAULT NOW() สำหรับ is_new 7 วัน
    created_at       TIMESTAMP WITH TIME ZONE DEFAULT NOW()
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
ALTER TABLE products ADD COLUMN IF NOT EXISTS free_from        TEXT;
ALTER TABLE products ADD COLUMN IF NOT EXISTS key_ingredients  TEXT;
ALTER TABLE products ADD COLUMN IF NOT EXISTS key_functions    TEXT;
ALTER TABLE products ADD COLUMN IF NOT EXISTS active_acne      TEXT;
ALTER TABLE products ADD COLUMN IF NOT EXISTS active_whitening TEXT;
ALTER TABLE products ADD COLUMN IF NOT EXISTS active_wrinkle   TEXT;
ALTER TABLE products ADD COLUMN IF NOT EXISTS active_exfoliation TEXT;
ALTER TABLE products ADD COLUMN IF NOT EXISTS active_hydration TEXT;
ALTER TABLE products ADD COLUMN IF NOT EXISTS active_barrier   TEXT;
ALTER TABLE products ADD COLUMN IF NOT EXISTS active_soothing  TEXT;
ALTER TABLE products ADD COLUMN IF NOT EXISTS active_oilct     TEXT;
ALTER TABLE products ADD COLUMN IF NOT EXISTS active_antioxidant TEXT;
-- ✅ แก้: migrate created_at เป็น TIMESTAMP WITH TIME ZONE (ถ้า DB เก่าใช้ TIMESTAMP ธรรมดา)
ALTER TABLE products ALTER COLUMN created_at TYPE TIMESTAMP WITH TIME ZONE USING created_at AT TIME ZONE 'Asia/Bangkok';
ALTER TABLE products ALTER COLUMN created_at SET DEFAULT NOW();

-- เพิ่ม table active_ingredients
CREATE TABLE IF NOT EXISTS active_ingredients (
    id         SERIAL PRIMARY KEY,
    ingredient TEXT NOT NULL UNIQUE,
    acne       BOOLEAN DEFAULT FALSE,
    whitening  BOOLEAN DEFAULT FALSE,
    wrinkle    BOOLEAN DEFAULT FALSE,
    exfoliation BOOLEAN DEFAULT FALSE,
    hydration  BOOLEAN DEFAULT FALSE,
    barrierrepair BOOLEAN DEFAULT FALSE,
    soothing   BOOLEAN DEFAULT FALSE,
    oilcontrol BOOLEAN DEFAULT FALSE,
    antioxidant BOOLEAN DEFAULT FALSE
);

INSERT INTO active_ingredients (ingredient, acne, whitening, wrinkle, exfoliation, hydration, barrierrepair, soothing, oilcontrol, antioxidant) VALUES
('Adapalene', TRUE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE),
('Allantoin', TRUE, FALSE, FALSE, FALSE, TRUE, TRUE, TRUE, FALSE, FALSE),
('Alpha Arbutin', TRUE, TRUE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE),
('Ammonium Lactate', TRUE, FALSE, FALSE, TRUE, FALSE, FALSE, FALSE, FALSE, FALSE),
('Asiatic Acid', TRUE, FALSE, FALSE, FALSE, FALSE, FALSE, TRUE, FALSE, FALSE),
('Asiaticoside', TRUE, FALSE, FALSE, FALSE, TRUE, TRUE, TRUE, FALSE, FALSE),
('Azadirachta Indica (Neem) Extract', TRUE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE),
('Azadirachta Indica Extract', TRUE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE),
('Azelaic Acid', TRUE, TRUE, FALSE, FALSE, FALSE, FALSE, FALSE, TRUE, FALSE),
('Benzoyl Peroxide', TRUE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE),
('Betaine Salicylate', TRUE, FALSE, FALSE, TRUE, FALSE, FALSE, FALSE, TRUE, FALSE),
('Bisabolol', TRUE, FALSE, FALSE, FALSE, FALSE, TRUE, TRUE, FALSE, FALSE),
('Bromelain', TRUE, FALSE, FALSE, TRUE, FALSE, FALSE, FALSE, FALSE, FALSE),
('Camellia Sinensis Leaf Extract', TRUE, FALSE, TRUE, FALSE, FALSE, TRUE, TRUE, TRUE, TRUE),
('Capryloyl Salicylic Acid', TRUE, FALSE, FALSE, TRUE, FALSE, FALSE, FALSE, TRUE, FALSE),
('Centella Asiatica Extract', TRUE, FALSE, TRUE, FALSE, TRUE, TRUE, TRUE, FALSE, TRUE),
('Citric Acid', TRUE, TRUE, TRUE, TRUE, FALSE, FALSE, FALSE, FALSE, FALSE),
('Dipotassium Glycyrrhizate', TRUE, TRUE, FALSE, FALSE, FALSE, FALSE, TRUE, FALSE, FALSE),
('Epigallocatechin Gallate', TRUE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, TRUE),
('Galactose', TRUE, FALSE, FALSE, TRUE, FALSE, FALSE, FALSE, FALSE, FALSE),
('Gluconolactone', TRUE, FALSE, FALSE, TRUE, FALSE, FALSE, FALSE, FALSE, FALSE),
('Glycolic Acid', TRUE, TRUE, TRUE, TRUE, FALSE, FALSE, FALSE, TRUE, FALSE),
('Glycyrrhiza Glabra Root Extract', TRUE, TRUE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE),
('Hamamelis Virginiana Extract', TRUE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, TRUE, FALSE),
('Hamamelis Virginiana Extract (Witch Hazel)', TRUE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, TRUE, FALSE),
('Honey Extract', TRUE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE),
('Hydroxypinacolone Retinoate', TRUE, FALSE, TRUE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE),
('Hydroxypinacolone Retinoate (HPR)', TRUE, FALSE, TRUE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE),
('Kojic Acid', TRUE, TRUE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE),
('L-Carnitine', TRUE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, TRUE, FALSE),
('Lactic Acid', TRUE, TRUE, TRUE, TRUE, FALSE, FALSE, FALSE, TRUE, FALSE),
('Lactobionic Acid', TRUE, FALSE, FALSE, TRUE, FALSE, FALSE, FALSE, FALSE, FALSE),
('Madecassoside', TRUE, FALSE, TRUE, FALSE, TRUE, TRUE, TRUE, FALSE, FALSE),
('Malic Acid', TRUE, FALSE, FALSE, TRUE, FALSE, FALSE, FALSE, FALSE, FALSE),
('Mandelic Acid', TRUE, TRUE, TRUE, TRUE, FALSE, FALSE, FALSE, FALSE, FALSE),
('Melaleuca Alternifolia (Tea Tree) Leaf Oil', TRUE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, TRUE, FALSE),
('Niacinamide', TRUE, TRUE, TRUE, FALSE, FALSE, FALSE, FALSE, TRUE, FALSE),
('Panthenol', TRUE, FALSE, TRUE, FALSE, TRUE, TRUE, TRUE, FALSE, FALSE),
('Papain', TRUE, FALSE, FALSE, TRUE, FALSE, FALSE, FALSE, FALSE, FALSE),
('Potassium Azeloyl Diglycinate', TRUE, TRUE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE),
('Propolis Extract', TRUE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE),
('Resorcinol', TRUE, FALSE, FALSE, TRUE, FALSE, FALSE, FALSE, FALSE, FALSE),
('Retinal', TRUE, FALSE, TRUE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE),
('Retinaldehyde', TRUE, FALSE, TRUE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE),
('Retinol', TRUE, FALSE, TRUE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE),
('Retinyl Palmitate', TRUE, FALSE, TRUE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE),
('Retinyl Propionate', TRUE, FALSE, TRUE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE),
('Salicylic Acid', TRUE, FALSE, FALSE, TRUE, FALSE, FALSE, FALSE, TRUE, FALSE),
('Salix Alba (Willow) Bark Extract', TRUE, FALSE, FALSE, TRUE, FALSE, FALSE, FALSE, FALSE, FALSE),
('Salix Alba Bark Extract', TRUE, FALSE, FALSE, TRUE, FALSE, FALSE, FALSE, FALSE, FALSE),
('Sarcosine', TRUE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, TRUE, FALSE),
('Sodium Lactate', TRUE, FALSE, FALSE, TRUE, TRUE, FALSE, FALSE, FALSE, FALSE),
('Sodium Salicylate', TRUE, FALSE, FALSE, TRUE, FALSE, FALSE, FALSE, FALSE, FALSE),
('Subtilisin', TRUE, FALSE, FALSE, TRUE, FALSE, FALSE, FALSE, FALSE, FALSE),
('Sulfur', TRUE, FALSE, FALSE, TRUE, FALSE, FALSE, FALSE, TRUE, FALSE),
('Tartaric Acid', TRUE, FALSE, FALSE, TRUE, FALSE, FALSE, FALSE, FALSE, FALSE),
('Tea Tree Oil', TRUE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE),
('Tranexamic Acid', TRUE, TRUE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE),
('Willow Bark Extract', TRUE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE),
('Willow Bark Extract (Salix Alba Bark Extract)', TRUE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE),
('Zinc Gluconate', TRUE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, TRUE, FALSE),
('Zinc Oxide', TRUE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE),
('Zinc PCA', TRUE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, TRUE, FALSE),
('Zinc Sulfate', TRUE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, TRUE, FALSE),
('3-O-Ethyl Ascorbic Acid', FALSE, TRUE, TRUE, FALSE, FALSE, FALSE, FALSE, FALSE, TRUE),
('4-Butylresorcinol', FALSE, TRUE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE),
('Arbutin', FALSE, TRUE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE),
('Arctostaphylos Uva-Ursi Leaf Extract', FALSE, TRUE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE),
('Arctostaphylos Uva-Ursi Leaf Extract (Bearberry)', FALSE, TRUE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE),
('Ascorbic Acid', FALSE, TRUE, TRUE, FALSE, FALSE, FALSE, FALSE, FALSE, TRUE),
('Ascorbyl Glucoside', FALSE, TRUE, TRUE, FALSE, FALSE, FALSE, FALSE, FALSE, TRUE),
('Ascorbyl Tetraisopalmitate', FALSE, TRUE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE),
('Camellia Sinensis Extract', FALSE, TRUE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE),
('Cetyl Tranexamate Mesylate', FALSE, TRUE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE),
('Decapeptide-12', FALSE, TRUE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE),
('Glabridin', FALSE, TRUE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE),
('Hexylresorcinol', FALSE, TRUE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE),
('Hydroquinone', FALSE, TRUE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE),
('Kojic Dipalmitate', FALSE, TRUE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE),
('Licorice Extract', FALSE, TRUE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE),
('Magnesium Ascorbyl Phosphate', FALSE, TRUE, TRUE, FALSE, FALSE, FALSE, FALSE, FALSE, TRUE),
('Mequinol', FALSE, TRUE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE),
('Morus Alba Root Extract', FALSE, TRUE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE),
('Morus Alba Root Extract (Mulberry)', FALSE, TRUE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE),
('Nonapeptide-1', FALSE, TRUE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE),
('Oligopeptide-68', FALSE, TRUE, TRUE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE),
('Papaya Extract', FALSE, TRUE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE),
('Phenylethyl Resorcinol', FALSE, TRUE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE),
('Phenylethyl Resorcinol (SymWhite 377)', FALSE, TRUE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE),
('Punica Granatum Extract', FALSE, TRUE, TRUE, FALSE, FALSE, FALSE, FALSE, FALSE, TRUE),
('Scutellaria Baicalensis Root Extract', FALSE, TRUE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE),
('Sodium Ascorbyl Phosphate', FALSE, TRUE, TRUE, FALSE, FALSE, FALSE, FALSE, FALSE, TRUE),
('Sodium Ascorbyl Tetraisopalmitate', FALSE, TRUE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE),
('Tetrahexyldecyl Ascorbate', FALSE, TRUE, TRUE, FALSE, FALSE, FALSE, FALSE, FALSE, TRUE),
('Vitamin C derivatives', FALSE, TRUE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE),
('Acetyl Hexapeptide-8', FALSE, FALSE, TRUE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE),
('Adenosine', FALSE, FALSE, TRUE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE),
('Bakuchiol', FALSE, FALSE, TRUE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE),
('Ceramides', FALSE, FALSE, TRUE, FALSE, TRUE, TRUE, FALSE, FALSE, FALSE),
('Coenzyme Q10', FALSE, FALSE, TRUE, FALSE, FALSE, FALSE, FALSE, FALSE, TRUE),
('Coenzyme Q10 (Ubiquinone)', FALSE, FALSE, TRUE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE),
('Copper Tripeptide-1', FALSE, FALSE, TRUE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE),
('Elastin', FALSE, FALSE, TRUE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE),
('Ferulic Acid', FALSE, FALSE, TRUE, FALSE, FALSE, FALSE, FALSE, FALSE, TRUE),
('Ginseng Root Extract', FALSE, FALSE, TRUE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE),
('Glycerin', FALSE, FALSE, TRUE, FALSE, TRUE, TRUE, TRUE, FALSE, FALSE),
('Hyaluronic Acid', FALSE, FALSE, TRUE, FALSE, TRUE, FALSE, FALSE, FALSE, FALSE),
('Hydrolyzed Collagen', FALSE, FALSE, TRUE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE),
('Hydrolyzed Hyaluronic Acid', FALSE, FALSE, TRUE, FALSE, TRUE, FALSE, FALSE, FALSE, FALSE),
('Idebenone', FALSE, FALSE, TRUE, FALSE, FALSE, FALSE, FALSE, FALSE, TRUE),
('Oligopeptide-1', FALSE, FALSE, TRUE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE),
('Palmitoyl Pentapeptide-4', FALSE, FALSE, TRUE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE),
('Palmitoyl Tetrapeptide-7', FALSE, FALSE, TRUE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE),
('Palmitoyl Tripeptide-1', FALSE, FALSE, TRUE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE),
('Peptides', FALSE, FALSE, TRUE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE),
('Resveratrol', FALSE, FALSE, TRUE, FALSE, FALSE, FALSE, FALSE, FALSE, TRUE),
('Retinyl Acetate', FALSE, FALSE, TRUE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE),
('Sodium Acetylated Hyaluronate', FALSE, FALSE, TRUE, FALSE, TRUE, FALSE, FALSE, FALSE, FALSE),
('Sodium Hyaluronate', FALSE, FALSE, TRUE, FALSE, TRUE, FALSE, TRUE, FALSE, FALSE),
('Soluble Collagen', FALSE, FALSE, TRUE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE),
('Tocopherol', FALSE, FALSE, TRUE, FALSE, FALSE, FALSE, FALSE, FALSE, TRUE),
('Tocopherol (Vitamin E)', FALSE, FALSE, TRUE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE),
('Tocopheryl Acetate', FALSE, FALSE, TRUE, FALSE, FALSE, FALSE, FALSE, FALSE, TRUE),
('Vitamin C', FALSE, FALSE, TRUE, FALSE, FALSE, FALSE, FALSE, FALSE, TRUE),
('Apricot Seed Powder', FALSE, FALSE, FALSE, TRUE, FALSE, FALSE, FALSE, FALSE, FALSE),
('Capryloyl Salicylic Acid (LHA)', FALSE, FALSE, FALSE, TRUE, FALSE, FALSE, FALSE, FALSE, FALSE),
('Cellulose', FALSE, FALSE, FALSE, TRUE, FALSE, FALSE, FALSE, FALSE, FALSE),
('Hydrated Silica', FALSE, FALSE, FALSE, TRUE, FALSE, FALSE, FALSE, TRUE, FALSE),
('Jojoba Esters', FALSE, FALSE, FALSE, TRUE, FALSE, FALSE, FALSE, FALSE, FALSE),
('Urea', FALSE, FALSE, FALSE, TRUE, TRUE, TRUE, FALSE, FALSE, FALSE),
('Walnut Shell Powder', FALSE, FALSE, FALSE, TRUE, FALSE, FALSE, FALSE, FALSE, FALSE),
('Alanine', FALSE, FALSE, FALSE, FALSE, TRUE, FALSE, FALSE, FALSE, FALSE),
('Aloe Barbadensis Leaf Extract', FALSE, FALSE, FALSE, FALSE, TRUE, FALSE, TRUE, FALSE, FALSE),
('Arginine', FALSE, FALSE, FALSE, FALSE, TRUE, FALSE, FALSE, FALSE, FALSE),
('Beeswax', FALSE, FALSE, FALSE, FALSE, TRUE, FALSE, FALSE, FALSE, FALSE),
('Betaine', FALSE, FALSE, FALSE, FALSE, TRUE, TRUE, TRUE, FALSE, FALSE),
('Butylene Glycol', FALSE, FALSE, FALSE, FALSE, TRUE, FALSE, FALSE, FALSE, FALSE),
('Ceramide AP', FALSE, FALSE, FALSE, FALSE, TRUE, TRUE, FALSE, FALSE, FALSE),
('Ceramide AS', FALSE, FALSE, FALSE, FALSE, TRUE, TRUE, FALSE, FALSE, FALSE),
('Ceramide EOP', FALSE, FALSE, FALSE, FALSE, TRUE, TRUE, FALSE, FALSE, FALSE),
('Ceramide NP', FALSE, FALSE, FALSE, FALSE, TRUE, TRUE, TRUE, FALSE, FALSE),
('Ceramide NS', FALSE, FALSE, FALSE, FALSE, TRUE, TRUE, FALSE, FALSE, FALSE),
('Cholesterol', FALSE, FALSE, FALSE, FALSE, TRUE, TRUE, TRUE, FALSE, FALSE),
('Cyclopentasiloxane', FALSE, FALSE, FALSE, FALSE, TRUE, FALSE, FALSE, FALSE, FALSE),
('Dimethicone', FALSE, FALSE, FALSE, FALSE, TRUE, TRUE, FALSE, FALSE, FALSE),
('Glycine', FALSE, FALSE, FALSE, FALSE, TRUE, FALSE, FALSE, FALSE, FALSE),
('Hydroxypropyltrimonium Hyaluronate', FALSE, FALSE, FALSE, FALSE, TRUE, FALSE, FALSE, FALSE, FALSE),
('Hydroxypropyltrimonium HyaluronateHyaluronic Acid', FALSE, FALSE, FALSE, FALSE, TRUE, FALSE, FALSE, FALSE, FALSE),
('Lanolin', FALSE, FALSE, FALSE, FALSE, TRUE, TRUE, FALSE, FALSE, FALSE),
('Mineral Oil', FALSE, FALSE, FALSE, FALSE, TRUE, TRUE, FALSE, FALSE, FALSE),
('PCA', FALSE, FALSE, FALSE, FALSE, TRUE, FALSE, FALSE, FALSE, FALSE),
('Pentylene Glycol', FALSE, FALSE, FALSE, FALSE, TRUE, FALSE, FALSE, FALSE, FALSE),
('Petrolatum', FALSE, FALSE, FALSE, FALSE, TRUE, TRUE, FALSE, FALSE, FALSE),
('Phytosphingosine', FALSE, FALSE, FALSE, FALSE, TRUE, TRUE, TRUE, FALSE, FALSE),
('Potassium Hyaluronate', FALSE, FALSE, FALSE, FALSE, TRUE, FALSE, FALSE, FALSE, FALSE),
('Proline', FALSE, FALSE, FALSE, FALSE, TRUE, FALSE, FALSE, FALSE, FALSE),
('Propylene Glycol', FALSE, FALSE, FALSE, FALSE, TRUE, FALSE, FALSE, FALSE, FALSE),
('Serine', FALSE, FALSE, FALSE, FALSE, TRUE, FALSE, FALSE, FALSE, FALSE),
('Shea Butter', FALSE, FALSE, FALSE, FALSE, TRUE, FALSE, FALSE, FALSE, FALSE),
('Shea Butter (Butyrospermum Parkii Butter)', FALSE, FALSE, FALSE, FALSE, TRUE, FALSE, FALSE, FALSE, FALSE),
('Sodium PCA', FALSE, FALSE, FALSE, FALSE, TRUE, TRUE, FALSE, FALSE, FALSE),
('Sorbitol', FALSE, FALSE, FALSE, FALSE, TRUE, FALSE, FALSE, FALSE, FALSE),
('Sphingolipids', FALSE, FALSE, FALSE, FALSE, TRUE, TRUE, FALSE, FALSE, FALSE),
('Threonine', FALSE, FALSE, FALSE, FALSE, TRUE, FALSE, FALSE, FALSE, FALSE),
('Trehalose', FALSE, FALSE, FALSE, FALSE, TRUE, FALSE, TRUE, FALSE, FALSE),
('Avena Sativa (Oat) Kernel Extract', FALSE, FALSE, FALSE, FALSE, FALSE, TRUE, TRUE, FALSE, FALSE),
('Avena Sativa Kernel Extract', FALSE, FALSE, FALSE, FALSE, FALSE, TRUE, TRUE, FALSE, FALSE),
('Calendula Officinalis Extract', FALSE, FALSE, FALSE, FALSE, FALSE, TRUE, FALSE, FALSE, FALSE),
('Ceramide EOS', FALSE, FALSE, FALSE, FALSE, FALSE, TRUE, FALSE, FALSE, FALSE),
('Fatty acids', FALSE, FALSE, FALSE, FALSE, FALSE, TRUE, FALSE, FALSE, FALSE),
('Hydrogenated Lecithin', FALSE, FALSE, FALSE, FALSE, FALSE, TRUE, FALSE, FALSE, FALSE),
('Lecithin', FALSE, FALSE, FALSE, FALSE, FALSE, TRUE, FALSE, FALSE, FALSE),
('Linoleic Acid', FALSE, FALSE, FALSE, FALSE, FALSE, TRUE, FALSE, FALSE, FALSE),
('Linolenic Acid', FALSE, FALSE, FALSE, FALSE, FALSE, TRUE, FALSE, FALSE, FALSE),
('Oleic Acid', FALSE, FALSE, FALSE, FALSE, FALSE, TRUE, FALSE, FALSE, FALSE),
('Palmitic Acid', FALSE, FALSE, FALSE, FALSE, FALSE, TRUE, FALSE, FALSE, FALSE),
('Stearic Acid', FALSE, FALSE, FALSE, FALSE, FALSE, TRUE, FALSE, FALSE, FALSE),
('Aloe Barbadensis Leaf Juice', FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, TRUE, FALSE, FALSE),
('Aloe Vera Extract', FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, TRUE, FALSE, FALSE),
('Calendula Officinalis Flower Extract', FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, TRUE, FALSE, FALSE),
('Chamomilla Recutita Flower Extract', FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, TRUE, FALSE, FALSE),
('Colloidal Oatmeal', FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, TRUE, FALSE, FALSE),
('Houttuynia Cordata Extract', FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, TRUE, TRUE, FALSE),
('Madecassic Acid', FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, TRUE, FALSE, FALSE),
('Portulaca Oleracea Extract', FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, TRUE, FALSE, FALSE),
('Bentonite', FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, TRUE, FALSE),
('Camellia Sinensis Leaf Extract (Green Tea)', FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, TRUE, TRUE),
('Green Tea Extract', FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, TRUE, TRUE),
('Kaolin', FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, TRUE, FALSE),
('Magnesium Aluminum Silicate', FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, TRUE, FALSE),
('Melaleuca Alternifolia Leaf Oil', FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, TRUE, FALSE),
('Silica', FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, TRUE, FALSE),
('Talc', FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, TRUE, FALSE),
('Witch Hazel Extract', FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, TRUE, FALSE),
('Alpha Lipoic Acid', FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, TRUE),
('Astaxanthin', FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, TRUE),
('Beta-Carotene', FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, TRUE),
('Catalase', FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, TRUE),
('Curcuma Longa Root Extract', FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, TRUE),
('Curcuma Longa Root Extract (Turmeric)', FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, TRUE),
('Epigallocatechin Gallate (EGCG)', FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, TRUE),
('Glutathione', FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, TRUE),
('Lycopene', FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, TRUE),
('Punica Granatum Extract (Pomegranate)', FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, TRUE),
('Superoxide Dismutase', FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, TRUE),
('Ubiquinone', FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, TRUE),
('Ubiquinone (Coenzyme Q10)', FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, TRUE),
('Vitamin E', FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, TRUE),
('Vitis Vinifera Seed Extract', FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, TRUE),
('Vitis Vinifera Seed Extract (Grape Seed)', FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, TRUE)

ON CONFLICT (ingredient) DO UPDATE SET
    acne = EXCLUDED.acne,
    whitening = EXCLUDED.whitening,
    wrinkle = EXCLUDED.wrinkle,
    exfoliation = EXCLUDED.exfoliation,
    hydration = EXCLUDED.hydration,
    barrierrepair = EXCLUDED.barrierrepair,
    soothing = EXCLUDED.soothing,
    oilcontrol = EXCLUDED.oilcontrol,
    antioxidant = EXCLUDED.antioxidant;


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

ALTER TABLE users ADD COLUMN IF NOT EXISTS gender VARCHAR(10) DEFAULT 'other';

-- ✅ ตั้ง timezone DB เป็นไทย
ALTER DATABASE "skincareCollectionDB" SET timezone = 'Asia/Bangkok';

-- Default admin account
INSERT INTO users (name, email, password, role)
VALUES ('Admin', 'admin@admin.com', 'admin1234', 'admin')
ON CONFLICT (email) DO NOTHING;