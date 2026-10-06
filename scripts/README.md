manage_feedback.py
==================

Purpose
-------

Small management helper to list recent feedback reports and safely remove test/smoke rows.

Usage
-----

- List 10 most recent feedback rows:

  ```bash

  python3 scripts/manage_feedback.py --list --count 10
  ```

- Delete smoke-test rows (only those matching page '/smoke-test' and component 'smoke'):

  ```bash

  python3 scripts/manage_feedback.py --delete-smoke --yes
  ```

Safety
------

- The delete action requires --yes to run. Without it, the script will refuse to delete.

- This script imports your app factory and runs with your app's configuration.

## Diagnostics

Standalone repository diagnostics live in `scripts/diagnostics/`. Run them from
the repository root as Python modules, for example:

```bash
python -m scripts.diagnostics.diagnose_import_issues
```

Database utilities and import repair tools are indexed in
[`database/README.md`](database/README.md) and
[`maintenance/imports/README.md`](maintenance/imports/README.md).
