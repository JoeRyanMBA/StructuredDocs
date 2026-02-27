-- Migration: Add email_delivery_unavailable column to reviews table
-- This column tracks when email delivery is unavailable for a reviewer

-- Check if column exists first (PostgreSQL 9.6+)
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_name='reviews' 
        AND column_name='email_delivery_unavailable'
    ) THEN
        -- Add the column
        ALTER TABLE reviews 
        ADD COLUMN email_delivery_unavailable BOOLEAN NOT NULL DEFAULT FALSE;
        
        RAISE NOTICE 'Column email_delivery_unavailable added successfully';
    ELSE
        RAISE NOTICE 'Column email_delivery_unavailable already exists';
    END IF;
END $$;

-- Verify the column was added
SELECT column_name, data_type, column_default, is_nullable
FROM information_schema.columns
WHERE table_name = 'reviews'
AND column_name = 'email_delivery_unavailable';
