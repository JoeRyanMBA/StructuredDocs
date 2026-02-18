-- Cleanup missing import image records for document_id = 76
-- Based on 404 log evidence from /images/imports/76/* requests.
--
-- Usage (preview + optional delete):
--   docker compose exec -T postgres psql -U postgres -d structureddocs -f cleanup_missing_import_images_doc76.sql
--
-- Safety:
-- - Runs in a transaction
-- - Shows preview first
-- - Delete is gated by exact (document_id, filename) matches
-- - Script ends with ROLLBACK by default; change to COMMIT after review

BEGIN;

-- 1) Targets from logs (missing on disk)
WITH targets AS (
  SELECT 76::int AS document_id, 'image22_5a818dc3.png'::text AS filename
  UNION ALL SELECT 76, 'image17_d5dd521a.png'
  UNION ALL SELECT 76, 'image13_f0053a91.png'
  UNION ALL SELECT 76, 'image12_04d3a744.jpeg'
)
SELECT
  ii.id,
  ii.document_id,
  ii.filename,
  ii.public_url,
  ii.backend_path,
  ii.frontend_path,
  ii.created_at
FROM import_images ii
JOIN targets t
  ON ii.document_id = t.document_id
 AND ii.filename = t.filename
ORDER BY ii.filename;

-- 2) Count how many rows would be deleted
WITH targets AS (
  SELECT 76::int AS document_id, 'image22_5a818dc3.png'::text AS filename
  UNION ALL SELECT 76, 'image17_d5dd521a.png'
  UNION ALL SELECT 76, 'image13_f0053a91.png'
  UNION ALL SELECT 76, 'image12_04d3a744.jpeg'
)
SELECT COUNT(*) AS rows_to_delete
FROM import_images ii
JOIN targets t
  ON ii.document_id = t.document_id
 AND ii.filename = t.filename;

-- 3) Delete exact matches and return deleted rows
WITH targets AS (
  SELECT 76::int AS document_id, 'image22_5a818dc3.png'::text AS filename
  UNION ALL SELECT 76, 'image17_d5dd521a.png'
  UNION ALL SELECT 76, 'image13_f0053a91.png'
  UNION ALL SELECT 76, 'image12_04d3a744.jpeg'
), deleted AS (
  DELETE FROM import_images ii
  USING targets t
  WHERE ii.document_id = t.document_id
    AND ii.filename = t.filename
  RETURNING ii.id, ii.document_id, ii.filename, ii.public_url
)
SELECT * FROM deleted ORDER BY filename;

-- 4) Verify remaining rows for this document
SELECT
  document_id,
  COUNT(*) AS remaining_rows
FROM import_images
WHERE document_id = 76
GROUP BY document_id;

-- Default safety behavior:
ROLLBACK;

-- After reviewing output and if it looks correct:
-- replace ROLLBACK with COMMIT and rerun.
