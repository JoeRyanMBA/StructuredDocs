-- SQL to create feedback_reports table for quick testing
CREATE TABLE IF NOT EXISTS feedback_reports (
  id serial PRIMARY KEY,
  report_type VARCHAR(32) NOT NULL DEFAULT 'other',
  page VARCHAR(256),
  component VARCHAR(256),
  user_contact VARCHAR(256),
  message TEXT NOT NULL,
  metadata TEXT,
  created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now()
);

-- Add enum type if your DB uses it; if using SQLAlchemy/Flask-Migrate prefer generating a proper migration.
-- Example (Postgres):
-- DO $$ BEGIN
--   CREATE TYPE feedback_report_type AS ENUM ('bug', 'suggestion', 'other');
-- EXCEPTION
--   WHEN duplicate_object THEN NULL;
-- END $$;

-- Note: If using Flask-Migrate, generate a migration instead of running this file on production.
