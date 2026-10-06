# StructuredDocs — Entity Lifecycle Guide

This document explains the lifecycle of the three core entities in StructuredDocs — **Projects**, **Collections**, and **Topics** — from creation through to publication and archival. It is intended for both content authors and developers.

---

## Overview

StructuredDocs organises content in a three-level hierarchy:

```
Project
└── Collection (can be nested)
    └── Topic (the actual content)
```

- A **Project** is the top-level container representing a body of work. It groups collections, tracks milestones, and assigns stakeholders.
- A **Collection** is a named, ordered set of topics. Collections can be nested inside each other and published as a document.
- A **Topic** is a single piece of content — a page of HTML written in the editor. Topics go through a review workflow before they can be published.

---

## Project Lifecycle

### States

Projects have a `status` field with five possible values:

| Status | Meaning |
|---|---|
| `planning` | Initial state. Work hasn't started yet. |
| `active` | Work is underway. |
| `review` | Content is under review. |
| `completed` | The project has been finished. |
| `on_hold` | Work is paused. |

In addition, any project can be **archived** (soft delete) regardless of status. Archiving hides the project from active views but does not delete it.

### Typical Lifecycle

```
Create → planning
           │
           ▼
         active  ──→  review  ──→  completed
           │
           ▼
        (archive when done)
```

1. **Create** a project with a name and optional description and dates. Status defaults to `planning`.
2. **Add stakeholders** to the project, assigning them roles such as `project_manager`, `reviewer`, `subject_matter_expert`, `sponsor`, or `stakeholder`. Stakeholders with `can_review = true` can be assigned as topic reviewers.
3. **Track milestones** by creating `ProjectMilestone` records against the project. Milestone statuses: `planned → in_progress → completed` (or `overdue`).
4. **Attach collections** to the project via `project_id` on the Collection.
5. **Update status** as work progresses through `active → review → completed`.
6. **Archive** the project when it is finished and no longer needs to appear in active views. There is no hard delete for projects.

### What you can do with a Project

| Action | Notes |
|---|---|
| Create | Sets status to `planning` |
| Edit name, description, dates, status | Any time |
| Add / remove stakeholders | With project-specific roles |
| Add / remove milestones | Tracked independently |
| Archive / restore | Soft delete; does not delete collections |
| View all reviews | Aggregated across all topics in the project |

---

## Collection Lifecycle

### States

Collections do not have a status enum. Their state is determined by two things:

| State | How it's set |
|---|---|
| **Active** | Default; `archived = false` |
| **Archived** | `archived = true` (soft delete) |
| **Published** | A `Publication` record exists with the same name |

### Typical Lifecycle

```
Create → (add topics) → publish → (archive when done) → delete
```

1. **Create** a collection with a name, a unique form number, and an optional description.
2. **Nest** collections inside each other using `parent_id` to build a document hierarchy (e.g., chapters and sections).
3. **Assign topics** to the collection. Topics are linked via an ordered pivot table (`collection_topic_tree`) and can be arranged hierarchically within the collection. A topic can belong to more than one collection.
4. **Configure variables** if topics contain `{{variable}}` placeholders. Variable values must be selected before publishing.
5. **Publish** the collection to create a snapshot. Publishing captures the current content of every topic (with variables substituted) into a `Publication` record. Republishing updates the existing publication.
6. **Archive** the collection when it is no longer actively maintained. An archived collection can still have its publication exported.
7. **Delete** the collection when you no longer need it at all.
   - If the collection has a publication, it must be archived first. Deleting an archived collection also deletes the associated publication.
   - Child collections are cascade-deleted.
   - Topics are **not** deleted; they are simply unlinked from the collection.

### What you can do with a Collection

| Action | Notes |
|---|---|
| Create | Requires a unique form number |
| Edit name, form number, description | Any time |
| Nest inside another collection | Set via `parent_id` |
| Add / reorder / remove topics | Topics can appear in multiple collections |
| Check variable readiness | Before publishing |
| Publish | Creates or updates a Publication snapshot |
| Archive / restore | Soft delete; does not delete topics |
| Delete | Must be archived first if a publication exists |

---

## Topic Lifecycle

### States

Topics have a `status` field that drives the review and publication workflow:

| Status | Meaning |
|---|---|
| `draft` | Initial state. Content is being written. |
| `pending_review` | Submitted for review; awaiting a reviewer. |
| `revisions_requested` | The reviewer has requested changes. Back to the author. |
| `approved` | The review passed. Ready to be included in a publication. |
| `rejected` | The review failed. Topic needs rework. |
| `published` | The topic is included in a published collection. |
| `archived` | The topic has been retired. |

### Typical Lifecycle

```
Create
  │
  ▼
draft ──→ pending_review ──→ approved ──→ published
                │                 ▲
                ▼                 │
        revisions_requested       │
                │                 │
                ▼                 │
             draft ───────────────┘  (incorporate feedback, re-submit)
                │
                ▼
            rejected
```

1. **Create** a topic. Status defaults to `draft`. Write and edit content in the rich-text editor.
2. **Submit for review** by creating a Review against the topic. This moves status to `pending_review`. A reviewer is notified by email and receives a time-limited token link to access the content without needing an account.
3. The **reviewer reads the topic** via their token link, leaves inline feedback, and submits a recommendation: `approve`, `approve_with_changes`, `reject`, or `needs_more_info`.
4. Once the review is **completed**:
   - Approved → status moves to `approved`
   - Changes requested (`approve_with_changes`) → status moves to `revisions_requested`
   - More information needed (`needs_more_info`) → status moves back to `draft`
   - Rejected → status moves to `rejected`
5. **Incorporate feedback** via the *Incorporate Feedback* dashboard. The author reviews each inline comment (accept, reject, or modify), applies word-level diff edits from the reviewer, and clicks **Update Topic**. This saves all changes and moves the topic status back to `draft`, removing it from the Incorporate Feedback queue.
6. The author can re-submit the revised topic for another review (repeat from step 2) or, if already approved, move directly to publication.
7. **Publish** the topic as part of a collection (see Collection Lifecycle above). Status moves to `published`. The publication captures a snapshot of the content at that moment — later edits to the topic do not affect the published snapshot.
8. **Archive** the topic when it is retired.

### What you can do with a Topic

| Action | Notes |
|---|---|
| Create | Status defaults to `draft` |
| Edit title and content | Any time while in `draft` or `revisions_requested` |
| Submit for review | Moves to `pending_review`; notifies reviewer by email |
| Review via token link | External reviewers do not need an account |
| Approve / request revisions / reject | Done by the reviewer; also supports bulk review (multiple topics, one email) |
| Incorporate feedback | *Incorporate Feedback* dashboard; accept/reject word-level diffs; clicking Update Topic returns topic to `draft` |
| Add to a collection | Topics can belong to multiple collections |
| Publish (via collection) | Captures a snapshot; status moves to `published` |
| Archive | Soft retire |
| Delete | Individual or bulk delete (admin) |

---

## How it All Connects — an End-to-End Example

Here is a complete walkthrough from a blank slate to a published document:

**1. Set up the project**
- Create a Project: *"Employee Handbook 2026"* → status `planning`
- Add your team as stakeholders and assign roles
- Add milestones: *"First draft"*, *"SME review"*, *"Publish"*
- Update project status to `active`

**2. Create the content structure**
- Create a root Collection: *"Employee Handbook"* (form number: `EH-2026`)
- Create child Collections: *"Onboarding"*, *"Benefits"*, *"Code of Conduct"*
- Create Topics inside each collection: *"Day One Checklist"*, *"Health Insurance Overview"*, etc.

**3. Write and review**
- Authors write topic content (status: `draft`)
- Submit each topic for review when ready (status: `pending_review`)
- Reviewers access via token links, leave feedback
- Authors address feedback; topics reach `approved`

**4. Publish**
- Configure any `{{variable}}` placeholders in topics (e.g., `{{company_name}}`)
- Publish the collection → a Publication is created with frozen snapshots of all topic content
- Export as PDF or mobile knowledge base for distribution

**5. Maintain**
- Edit topics after publication as policies change → re-publish the collection to update the snapshot
- Archive collections or topics that are no longer relevant
- When the project is complete, archive it

---

## Technical Appendix

### Data Models

#### Project

| Field | Type | Notes |
|---|---|---|
| `id` | Integer | Primary key |
| `name` | String(200) | Required |
| `description` | Text | Optional |
| `status` | Enum | `planning`, `active`, `review`, `completed`, `on_hold` |
| `start_date` | Date | Optional |
| `target_completion` | Date | Optional |
| `archived` | Boolean | Default `false` |
| `created_at` / `updated_at` | DateTime | Auto-managed |

Relationships: `stakeholders` → `ProjectStakeholder`, `milestones` → `ProjectMilestone`, `collections` → `Collection`

#### Collection

| Field | Type | Notes |
|---|---|---|
| `id` | Integer | Primary key |
| `name` | String(200) | Required |
| `description` | Text | Optional |
| `form_number` | String(100) | Required, unique |
| `parent_id` | Integer (FK) | Self-referencing; `null` for root |
| `project_id` | Integer (FK) | Optional |
| `position` | Integer | Sort order; default `0` |
| `archived` | Boolean | Default `false` |
| `created_at` / `updated_at` | DateTime | Auto-managed |

Topic membership is tracked via the `collection_topic_tree` pivot table, which stores `collection_id`, `topic_id`, `parent_topic_id` (for nesting), and `position`.

#### Topic

| Field | Type | Notes |
|---|---|---|
| `id` | Integer | Primary key |
| `title` | String(200) | Required |
| `content` | Text | HTML; sanitised on save |
| `frontmatter` | Text | YAML metadata |
| `status` | Enum | See states above |
| `created_at` / `updated_at` | DateTime | Auto-managed |

#### Publication & PublicationNode

A `Publication` is created when a collection is published. It has a `title` (set to the collection name) and contains a tree of `PublicationNode` records — one per topic — each holding a `title_snapshot` and `content_snapshot` with variables already substituted. Snapshots are immutable; re-publishing the collection replaces all nodes.

### API Endpoints

#### Projects (`/api/projects`)

| Method | Path | Action |
|---|---|---|
| GET | `/api/projects` | List all projects |
| POST | `/api/projects` | Create project |
| GET | `/api/projects/<id>` | Get project detail |
| PUT | `/api/projects/<id>` | Update project |
| POST | `/api/projects/<id>/archive` | Toggle archive state |
| GET/POST | `/api/projects/<id>/stakeholders` | Manage stakeholders |
| GET/POST | `/api/projects/<id>/reviews` | View / submit reviews |

#### Collections (`/api/collections`)

| Method | Path | Action |
|---|---|---|
| GET | `/api/collections` | List collections (tree) |
| POST | `/api/collections` | Create collection |
| GET | `/api/collections/<id>` | Get collection with topics |
| PUT | `/api/collections/<id>` | Update collection |
| DELETE | `/api/collections/<id>` | Delete (must be archived first if published) |
| POST | `/api/collections/<id>/archive` | Toggle archive state |
| POST | `/api/collections/<id>/publish` | Publish to snapshot |
| GET | `/api/collections/<id>/variables/check` | Check variable readiness |
| GET | `/api/collections/<id>/prepare-publish` | Preview before publish |

#### Topics (`/api/topics`)

| Method | Path | Action |
|---|---|---|
| GET | `/api/topics` | List topics (filterable by status) |
| POST | `/api/topics` | Create topic |
| GET | `/api/topics/<id>` | Get topic |
| PUT | `/api/topics/<id>` | Update topic |
| POST | `/api/topics/<id>/review` | Submit for review |
| GET | `/api/topics/usage-summary` | Collection membership overview |
| DELETE | `/api/topics/bulk` | Bulk delete (admin) |

#### Publications (`/api/publications`)

| Method | Path | Action |
|---|---|---|
| GET | `/api/publications` | List publications |
| POST | `/api/publications` | Create publication manually |
| GET | `/api/publications/<id>` | Get publication with node tree |
| POST | `/api/publications/<id>/nodes` | Rebuild node tree |
| GET | `/api/publications/<id>/export/pdf` | Export PDF (`?format=default\|corporate\|academic\|compact`) |
| GET | `/api/publications/<id>/export/mobile-kb` | Export mobile HTML |
| GET | `/api/publications/<id>/preview/mobile-kb` | Preview in browser |

### Entity Relationships

```
Project
├── ProjectStakeholder → Stakeholder (roles: project_manager, reviewer, SME, sponsor, stakeholder)
├── ProjectMilestone (status: planned, in_progress, completed, overdue)
└── Collection
    ├── Collection (nested children, cascade delete)
    ├── Topic (via collection_topic_tree pivot — many-to-many, ordered, hierarchical)
    └── Publication
        └── PublicationNode (snapshot per topic, hierarchical, variables substituted)

Topic
├── Review → Stakeholder
│   └── ReviewToken (time-limited external access link)
│   └── ReviewFeedback
└── TopicLink → Link
```
