-- เพิ่ม column ใหม่ใน history table
ALTER TABLE history ADD COLUMN IF NOT EXISTS history_type VARCHAR(20) DEFAULT 'recommend';
ALTER TABLE history ADD COLUMN IF NOT EXISTS routine_products JSONB;