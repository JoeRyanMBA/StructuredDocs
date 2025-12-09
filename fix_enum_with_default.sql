-- Fix project_stakeholders.role enum with proper handling of defaults

-- Step 1: Create the new enum type
DO $$
BEGIN
  CREATE TYPE project_stakeholder_role AS ENUM (
    'project_manager',
    'subject_matter_expert',
    'reviewer',
    'stakeholder',
    'sponsor'
  );
EXCEPTION
  WHEN duplicate_object THEN
    RAISE NOTICE 'Type project_stakeholder_role already exists, skipping creation';
END $$;

-- Step 2: Drop the default constraint temporarily
ALTER TABLE project_stakeholders 
  ALTER COLUMN role DROP DEFAULT;

-- Step 3: Convert the column to the new enum type
ALTER TABLE project_stakeholders 
  ALTER COLUMN role TYPE project_stakeholder_role 
  USING CASE role
    WHEN 'author' THEN 'project_manager'::project_stakeholder_role
    WHEN 'admin' THEN 'sponsor'::project_stakeholder_role
    WHEN 'subject_matter_expert' THEN 'subject_matter_expert'::project_stakeholder_role
    WHEN 'reviewer' THEN 'reviewer'::project_stakeholder_role
    ELSE 'stakeholder'::project_stakeholder_role
  END;

-- Step 4: Restore the default value
ALTER TABLE project_stakeholders 
  ALTER COLUMN role SET DEFAULT 'stakeholder'::project_stakeholder_role;

-- Verify the change
SELECT column_name, data_type, column_default
FROM information_schema.columns
WHERE table_name = 'project_stakeholders' AND column_name = 'role';
