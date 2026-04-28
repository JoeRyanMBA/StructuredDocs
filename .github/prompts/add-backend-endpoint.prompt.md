---
description: "Add or extend a StructuredDocs Flask backend endpoint. Use when creating a new backend route, changing request or response payloads, updating serializers, wiring blueprint registration, or adding a focused backend test."
name: "Add Backend Endpoint"
argument-hint: "Describe the endpoint, auth, payload, response, and any model changes"
agent: "backend-specialist"
---
Implement the StructuredDocs backend endpoint described in this chat input.

Requirements:
- Start from the most direct owning code path in `backend/routes/`, `backend/models.py`, or `backend/app.py`.
- Follow the existing Flask Blueprint conventions and register a new blueprint in `backend/app.py` if the task introduces a new resource.
- Preserve JSON response patterns, rollback behavior, and logging conventions used by nearby routes.
- If the contract changes, update the relevant serializer path such as `to_dict()` instead of reshaping responses inconsistently at the call site.
- If the schema changes, add the required Alembic migration and keep existing rows valid.
- Add or update the narrowest practical backend test when the repo already has a nearby test pattern for the touched slice.
- Validate the change with the cheapest focused command available.

Use these repo anchors when relevant:
- [backend/app.py](../../backend/app.py)
- [backend/models.py](../../backend/models.py)
- [backend/routes](../../backend/routes)
- [README.md](../../README.md)
