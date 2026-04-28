---
description: "Use when editing Vue frontend pages, views, components, composables, or API wrappers in frontend/src/. Covers API-layer boundaries, folder responsibilities, and preserving the existing StructuredDocs Vue application patterns."
name: "StructuredDocs Frontend"
applyTo: "frontend/src/**"
---
# StructuredDocs Frontend Guidelines

- Keep network access in `frontend/src/api/`. When a backend contract changes, update the API wrapper first, then update the consuming page, view, component, or composable.
- Reuse the shared request layer such as `frontend/src/api/base.js` and existing API modules instead of adding ad hoc fetch or Axios setup inside components.
- Put reusable stateful logic in `frontend/src/composables/`, reusable UI in `frontend/src/components/`, and page-level flows in `frontend/src/pages/` or `frontend/src/views/`.
- Use the `@` alias for imports from `frontend/src/`.
- Preserve the current Vue app structure and naming before introducing new patterns or directories.
- Keep field names aligned with backend payloads unless an intentional API translation layer already exists.
- For collection, topic, review, import, and publication screens, trace the matching backend route or API module before changing local state shape.
- The standard local dev flow is the Vite app in `frontend/` talking to the backend on port 8080 through the existing proxy setup.
