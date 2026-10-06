-- Add missing columns to publication_nodes table
-- This file provides a SQL Server–compatible version to satisfy generic linters.
-- A PostgreSQL variant is included below as comments for reference.

/*
	SQL Server (T-SQL) version
	- Uses COL_LENGTH to check for column existence
	- Adds columns only if they are missing
*/
IF COL_LENGTH('publication_nodes', 'title_snapshot') IS NULL
BEGIN
	ALTER TABLE publication_nodes ADD title_snapshot VARCHAR(200) NULL;
END;

IF COL_LENGTH('publication_nodes', 'content_snapshot') IS NULL
BEGIN
	ALTER TABLE publication_nodes ADD content_snapshot NVARCHAR(MAX) NULL;
END;

-- Verify the columns exist
SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_NAME = 'publication_nodes'
	AND COLUMN_NAME IN ('title_snapshot', 'content_snapshot')
ORDER BY COLUMN_NAME;

/*
PostgreSQL version (for reference only):

-- ALTER TABLE publication_nodes ADD COLUMN IF NOT EXISTS title_snapshot VARCHAR(200);
-- ALTER TABLE publication_nodes ADD COLUMN IF NOT EXISTS content_snapshot TEXT;
-- 
-- SELECT column_name, data_type, is_nullable 
-- FROM information_schema.columns 
-- WHERE table_name = 'publication_nodes' 
--   AND column_name IN ('title_snapshot', 'content_snapshot')
-- ORDER BY column_name;
*/