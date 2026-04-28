#!/bin/bash
# Initialise databases on the shared Managed PostgreSQL cluster.
# Run this ONCE after provisioning the cluster — before the first deployment.
#
# Prerequisites:
#   - psql installed locally (brew install postgresql or apt install postgresql-client)
#   - Managed Postgres admin connection string available
#
# Usage:
#   export PG_ADMIN_URL="postgresql://doadmin:PASSWORD@DB_HOST:25060/defaultdb?sslmode=require"
#   ./scripts/init_databases.sh

set -euo pipefail

if [[ -z "${PG_ADMIN_URL:-}" ]]; then
  echo "❌ PG_ADMIN_URL is not set."
  echo "   Export your DO Managed Postgres admin connection string:"
  echo '   export PG_ADMIN_URL="postgresql://doadmin:PASSWORD@DB_HOST:25060/defaultdb?sslmode=require"'
  exit 1
fi

echo "🗄️  Initialising StructuredDocs databases on shared Postgres cluster"
echo "   Connection: $PG_ADMIN_URL"
echo ""

# Prompt for passwords
read -rsp "Enter password for structureddocs_test user:     " TEST_PASS;     echo
read -rsp "Enter password for structureddocs_training user: " TRAINING_PASS; echo
read -rsp "Enter password for structureddocs_prod user:     " PROD_PASS;     echo
echo ""

psql "$PG_ADMIN_URL" <<SQL
-- -----------------------------------------------------------------------
-- Databases
-- -----------------------------------------------------------------------
SELECT 'Creating databases...' AS status;

CREATE DATABASE structureddocs_test     WITH ENCODING 'UTF8';
CREATE DATABASE structureddocs_training WITH ENCODING 'UTF8';
CREATE DATABASE structureddocs_prod     WITH ENCODING 'UTF8';

-- -----------------------------------------------------------------------
-- Per-environment users (principle of least privilege)
-- -----------------------------------------------------------------------
SELECT 'Creating users...' AS status;

CREATE USER structureddocs_test     WITH PASSWORD '$TEST_PASS';
CREATE USER structureddocs_training WITH PASSWORD '$TRAINING_PASS';
CREATE USER structureddocs_prod     WITH PASSWORD '$PROD_PASS';

-- Grant ownership of each database to the corresponding user
ALTER DATABASE structureddocs_test     OWNER TO structureddocs_test;
ALTER DATABASE structureddocs_training OWNER TO structureddocs_training;
ALTER DATABASE structureddocs_prod     OWNER TO structureddocs_prod;

SELECT 'Done. Databases and users created.' AS status;
SQL

echo ""
echo "✅ Databases initialised:"
echo "   structureddocs_test     → user: structureddocs_test"
echo "   structureddocs_training → user: structureddocs_training"
echo "   structureddocs_prod     → user: structureddocs_prod"
echo ""
echo "📋 Next steps:"
echo "   1. Copy the matching envs/*.env.example to each VPS as /opt/structureddocs/backend.env"
echo "   2. Set DATABASE_URL in each env file using the user/password above"
echo "   3. Run ./scripts/deploy.sh <environment> <server-ip> for each VPS"
