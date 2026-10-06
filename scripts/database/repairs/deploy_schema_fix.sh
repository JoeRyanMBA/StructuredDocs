#!/bin/bash
# Production database schema fix for publication_nodes table
# This script should be run on the production server to fix the missing columns

echo "🔧 Fixing publication_nodes schema in production database..."

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
cd "$REPO_ROOT"

python3 -m scripts.database.repairs.fix_publication_nodes_schema

if [ $? -eq 0 ]; then
    echo "✅ Schema fix completed successfully"
    echo "📝 Publication PDF/HTML export should now work"
else
    echo "❌ Schema fix failed"
    exit 1
fi