#!/usr/bin/env bash
set -euo pipefail

# Simple deploy: unpack backend/frontend packages, install deps, migrate, seed admin.
#!/usr/bin/env bash
# Legacy placeholder script.

set -euo pipefail

echo "This helper no longer performs any actions. Consult the deployment documentation instead."
python "$APP_DIR/backend/create_admin.py" \
  --email "${ADMIN_EMAIL:-admin@example.com}" \
  --password "${ADMIN_PASSWORD:-password}"

echo "Done. Go to the PythonAnywhere Web tab and click Reload for your app."
