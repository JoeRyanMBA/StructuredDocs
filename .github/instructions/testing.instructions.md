---
description: "Use when editing or adding pytest files, conftest fixtures, backend API regression tests, or focused validation for StructuredDocs changes. Covers repo test locations, narrow test selection, and existing lightweight app-fixture patterns."
name: "StructuredDocs Testing"
applyTo: "{test_*.py,conftest.py,backend/**/test*.py}"
---
# StructuredDocs Testing Guidelines

- Prefer the narrowest existing test surface that exercises the changed behavior. This repo has many focused root-level tests like `test_reviews_api_regression.py`, plus some tests under `backend/`.
- Many backend tests create a lightweight Flask app with `create_app()`, set `ENABLE_BLUEPRINTS` narrowly, and use a temporary SQLite database. Reuse that pattern before introducing heavier setup.
- Keep fixtures local when they are specific to a feature; only add to `conftest.py` when the fixture is broadly reused.
- When a behavior change is confined to one route or workflow, add or update a focused regression test rather than expanding broad integration coverage.
- If a test depends on a running backend or a nonstandard port, document that dependency in the test or in the validation summary.
- After editing tests, run the narrowest practical pytest command from repo root.
