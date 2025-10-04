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
