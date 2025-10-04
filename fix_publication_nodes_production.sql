-- SQL script to fix publication_nodes schema in production
-- Add missing columns for publication node snapshots

-- PostgreSQL version
ALTER TABLE publication_nodes 
ADD COLUMN IF NOT EXISTS title_snapshot VARCHAR(200);

ALTER TABLE publication_nodes 
ADD COLUMN IF NOT EXISTS content_snapshot TEXT;