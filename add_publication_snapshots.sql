-- Add missing columns to publication_nodes table for PostgreSQL production database
-- Run this on your production PostgreSQL database

-- Check if columns already exist before adding them
DO $$
BEGIN
    -- Add title_snapshot column if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name='publication_nodes' AND column_name='title_snapshot'
    ) THEN
        ALTER TABLE publication_nodes ADD COLUMN title_snapshot VARCHAR(200);
        RAISE NOTICE 'Added title_snapshot column to publication_nodes';
    ELSE
        RAISE NOTICE 'title_snapshot column already exists in publication_nodes';
    END IF;

    -- Add content_snapshot column if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name='publication_nodes' AND column_name='content_snapshot'
    ) THEN
        ALTER TABLE publication_nodes ADD COLUMN content_snapshot TEXT;
        RAISE NOTICE 'Added content_snapshot column to publication_nodes';
    ELSE
        RAISE NOTICE 'content_snapshot column already exists in publication_nodes';
    END IF;
END $$;

-- Verify the columns were added
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'publication_nodes' 
AND column_name IN ('title_snapshot', 'content_snapshot')
ORDER BY column_name;