# Archive System Overview

This document summarizes the implemented archive / restore functionality across core entities (Projects, Collections, Feedback, Bugs) and outlines recommended enhancements.

## 1. Goals

Provide a consistent, discoverable lifecycle for retiring and restoring entities without permanent deletion. Key objectives achieved:

- Unified visual affordance (ArchiveToggleButton)

- Dedicated admin archived lists per entity

- Backend toggle endpoint for Projects (new)

- Service + composable layering for reuse

## 2. Entities & Mechanisms

| Entity       | Archive Field / Status            | Backend Toggle Path                          | Archived View Component                |
|--------------|-----------------------------------|----------------------------------------------|----------------------------------------|
| Project      | `project.archived` (bool)         | `POST /api/projects/<id>/archive`            | `ArchivedProjectsView.vue`             |
| Collection   | `collection.archived` (bool)      | `POST /api/collections/<id>/archive` (exists)| `ArchivedCollectionsView.vue`          |
| Feedback     | `feedback.status === 'archived'`  | `POST /api/feedback/<id>/archive` (existing or mapped)| `ArchivedFeedbackView.vue`     |
| Bug Report   | `feedback.status === 'archived'`  | Same as Feedback                            | `ArchivedBugsView.vue`                 |

## 3. Frontend Layers

- **Component:** `ArchiveToggleButton.vue` – Icon button that reflects archived vs active state.

- **Service:** `frontend/src/services/archiveService.js` – Centralized fetch & toggle logic (entity → endpoint mapping).

- **Composable:** `frontend/src/composables/useArchive.js` – Reactive helper for archived list pages (load, restore, archive, toasts).

- **Pages:** Four archived views now use the composable + component for consistent UX.

## 4. Backend Changes

- Added `archived` boolean column to `Project` model (migration included).

- Implemented admin-protected endpoint `POST /api/projects/<id>/archive` accepting `{ "archived": true|false }`.

- Structured log line emitted on each toggle: `[PROJECT_ARCHIVE] user_id=... project_id=... previous_archived=... new_archived=... timestamp=...`.

## 5. Tests & Logging

- Added `test_project_archive.py` covering: archive, restore, auth requirement.

- Structured print logging for operations to ease later ingestion into centralized logs.

## 6. UX Behavior Summary

- Active list views show toggle icon (archive → restore) only for admins.

- Archived list views show only archived items; toggling restores and removes them from the view.

- Optimistic updates with fallback error handling in most lists; toasts for success/failure (add missing toasts for any remaining console-only handlers if noticed).

## 7. Current Constraints

- Server-side filtering for archived vs active is not yet standardized via query params (client fetches full lists for some cases).

- No `archived_at` metadata – unable to report archive aging.

- No bulk archive/unarchive endpoints – UI must toggle items individually.

- Potential duplication or legacy model definitions still present (review `project_models_extension.py`).

## 8. Recommended Enhancements (Roadmap)

### 8.1 API Improvements

- Support `GET /api/projects?archived=true|false` and equivalent for collections.

- Add bulk toggle endpoint: `POST /api/projects/bulk-archive` `{ ids: [...], archived: true }`.

- Introduce `archived_at` (UTC) column (nullable) for Projects & Collections; set/clear automatically.

### 8.2 Data & Auditing

- Add `audit_log` table (id, entity_type, entity_id, user_id, action, previous_state, new_state, timestamp JSON snapshot).

- Optional soft-delete / purge workflow (archived first → purge after retention window).

### 8.3 Frontend UX

- Inline toggle in main dashboards: add a “Show Archived” pill/filter rather than separate page navigation (optional).

- Add counts in dashboard section headers: e.g., `Projects (24 total · 3 archived)` linking to archived view.

- Tooltip unification (use a directive or centralized small component for all icon buttons).

### 8.4 Performance & Scale

- Pagination for archived feedback / bug lists.

- Debounced search + server-side filtering when counts grow.

- Preload metrics endpoint summarizing counts (reduces list fetches for overview cards).

### 8.5 Developer Experience

- Add type definitions or JSDoc for `archiveService` + `useArchive`.

- Expand test coverage: add collection archive test; negative tests (non-admin forbidden).

- CI step: enforce lint & type check before build to catch template structural issues earlier.

### 8.6 Resilience

- Wrap toggle requests with idempotency key (optional) if UI may send duplicate clicks.

- Provide standardized error object shape from backend (code, message) for better toast messaging.

## 9. Suggested Implementation Order (Incremental)

1. Query param filtering (fast win; reduces client data mass).

2. `archived_at` + migration + endpoint exposure.

3. Bulk archive endpoints + UI multi-select.

4. Audit log table + integration in toggle endpoints.

5. Pagination + server-side search for feedback/bugs.

6. Inline archived filter toggle on dashboards.

7. Dashboard aggregate counts API.

## 10. Quick Reference (Endpoints)

```

POST /api/projects/<id>/archive    { archived: boolean }
POST /api/collections/<id>/archive  { archived: boolean }
POST /api/feedback/<id>/archive     { archived: boolean }  (status-based)

```

## 11. Known Follow-Up Cleanup

- Confirm removal or refactor of any legacy duplicate project model definitions.

- Normalize toast messages ("Archived" vs "Moved to archive").

- Add missing success toasts for project archive toggle if not yet surfaced in UI.

---
**Status:** Archive foundation complete & consistent.
**Ready For:** Incremental enhancements (filtering, bulk ops, metadata, auditing).

Let me know if you want implementation to begin on any roadmap item immediately.
