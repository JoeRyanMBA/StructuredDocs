---
description: "Create or update a focused StructuredDocs regression test from a bug report, failing behavior, or route-level defect. Use when converting reproducible bugs into pytest coverage with minimal setup."
name: "Write Regression Test"
argument-hint: "Describe the bug, expected behavior, endpoints/models touched, and preferred test file"
agent: "backend-specialist"
---
Write or update a focused regression test for the bug described in this chat input.

Requirements:
- Reproduce the failure first in test form, then assert the expected fixed behavior.
- Prefer the narrowest test location and setup already used in this repo (root-level `test_*.py` or targeted backend test files).
- Reuse lightweight app fixtures where possible, including selective blueprint loading and temporary SQLite setup when appropriate.
- Keep fixtures local unless there is clear multi-file reuse.
- Avoid broad end-to-end expansion when a route- or model-level regression test is sufficient.
- Run or suggest the narrowest pytest command from repo root.

Useful references:
- [conftest.py](../../conftest.py)
- [test_reviews_api_regression.py](../../test_reviews_api_regression.py)
- [backend/routes](../../backend/routes)
- [README.md](../../README.md)
