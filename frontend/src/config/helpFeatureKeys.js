/**
 * Central registry of all HelpIcon feature keys used in the app.
 *
 * HOW TO ADD A NEW HELP ICON:
 * 1. Add an entry here (key, label, location, hint).
 * 2. Drop <HelpIcon feature="your.key" /> into the relevant Vue template.
 * 3. Go to Admin → Help Links and toggle it on with a description.
 */

export const HELP_FEATURE_KEYS = [
  // ── Authoring ────────────────────────────────────────────────────────────
  {
    key: 'topics.list',
    label: 'Topics',
    location: 'Topics list page (header)',
    hint: 'Overview of what topics are and how to create and organise them.',
  },
  {
    key: 'topics.create',
    label: 'Create Topic',
    location: 'Create Topic page (header)',
    hint: 'Explains topic fields: title, content, status, and collection membership.',
  },
  {
    key: 'topics.edit',
    label: 'Edit Topic',
    location: 'Edit Topic page (header)',
    hint: 'Tips for using the rich-text editor, inserting snippets, and saving.',
  },
  {
    key: 'topics.view',
    label: 'Topic Detail',
    location: 'Topic detail/view page (header)',
    hint: 'What users can do from the topic view: request reviews, publish, export.',
  },

  // ── Collections ──────────────────────────────────────────────────────────
  {
    key: 'collections.dashboard',
    label: 'Collections Dashboard',
    location: 'Collections Dashboard (header)',
    hint: 'How collections work: grouping topics, nesting, and hierarchy.',
  },
  {
    key: 'collections.organize',
    label: 'Organize Collection',
    location: 'Organize page (header)',
    hint: 'How to drag-and-drop topics to reorder them within a collection.',
  },

  // ── Projects ─────────────────────────────────────────────────────────────
  {
    key: 'projects.list',
    label: 'Projects',
    location: 'Projects page (header)',
    hint: 'How projects work: grouping collections with tasks, milestones, and stakeholders.',
  },
  {
    key: 'projects.tasks',
    label: 'Tasks',
    location: 'Projects page — Tasks tab',
    hint: 'Creating and managing tasks, assigning them, and tracking completion.',
  },
  {
    key: 'projects.milestones',
    label: 'Milestones',
    location: 'Projects page — Milestones tab',
    hint: 'Setting milestone dates and linking tasks to track project progress.',
  },
  {
    key: 'projects.stakeholders',
    label: 'Stakeholders',
    location: 'Projects page — Stakeholders tab',
    hint: 'Adding stakeholders and their roles to a project.',
  },

  // ── Import ───────────────────────────────────────────────────────────────
  {
    key: 'import.upload',
    label: 'Import Content',
    location: 'Import Content page (header)',
    hint: 'Explains the import tool and supported file types (.docx, .md).',
  },
  {
    key: 'import.dashboard',
    label: 'Import Dashboard',
    location: 'Import Dashboard (header)',
    hint: 'Tracking the status of in-progress and completed document imports.',
  },
  {
    key: 'import.review',
    label: 'Import Review',
    location: 'Import Review page (header)',
    hint: 'How to review staged import content before committing it as topics.',
  },

  // ── Publishing ───────────────────────────────────────────────────────────
  {
    key: 'publish.dashboard',
    label: 'Publication Dashboard',
    location: 'Publication Dashboard (header)',
    hint: 'Overview of publications, exporting PDFs and mobile knowledge bases.',
  },
  {
    key: 'publish.pdf',
    label: 'Publish to PDF',
    location: 'Publish PDF page (header)',
    hint: 'Choosing format options and generating a PDF from your publication.',
  },
  {
    key: 'publish.mobile-kb',
    label: 'Publish Mobile KB',
    location: 'Publish Mobile KB page (header)',
    hint: 'Creating a self-contained HTML knowledge base for offline or mobile use.',
  },

  // ── Reviews ──────────────────────────────────────────────────────────────
  {
    key: 'reviews.dashboard',
    label: 'Reviews Dashboard',
    location: 'Reviews Dashboard (header)',
    hint: 'Overview of the review workflow: requesting reviews, tokens, and feedback.',
  },
  {
    key: 'reviews.request',
    label: 'Request Review',
    location: 'Request Review modal',
    hint: 'How to request a review from an internal reviewer or external SME.',
  },
  {
    key: 'reviews.feedback',
    label: 'Review Feedback',
    location: 'Review Feedback page (header)',
    hint: 'Reviewing inline feedback from SMEs and accepting or rejecting suggestions.',
  },
  {
    key: 'reviews.bulk',
    label: 'Bulk Review',
    location: 'Bulk Review Portal (header)',
    hint: 'Sending multiple topics for review in a single session.',
  },

  // ── Snippets ─────────────────────────────────────────────────────────────
  {
    key: 'snippets.library',
    label: 'Snippets Library',
    location: 'Snippets Library page (header)',
    hint: 'Reusable content blocks that can be inserted into topics by audience tag.',
  },

  // ── Variables ────────────────────────────────────────────────────────────
  {
    key: 'variables.list',
    label: 'Variables',
    location: 'Admin Variables page (header)',
    hint: 'Publish-time variables that get substituted when a publication is exported.',
  },

  // ── Tags ─────────────────────────────────────────────────────────────────
  {
    key: 'tags.list',
    label: 'Tags',
    location: 'All Tags page (header)',
    hint: 'Using tags to categorise and filter topics, tasks, and other resources.',
  },

  // ── Links ─────────────────────────────────────────────────────────────────
  {
    key: 'links.list',
    label: 'Links',
    location: 'All Links page (header)',
    hint: 'Managing cross-topic links and checking for broken references.',
  },

  // ── Images ───────────────────────────────────────────────────────────────
  {
    key: 'images.list',
    label: 'Images',
    location: 'All Images page (header)',
    hint: 'Browsing and managing images uploaded or extracted during imports.',
  },

  // ── Admin ─────────────────────────────────────────────────────────────────
  {
    key: 'admin.dashboard',
    label: 'Admin Dashboard',
    location: 'Admin Dashboard (header)',
    hint: 'Overview of system health, user counts, and quick administrative actions.',
  },
  {
    key: 'admin.users',
    label: 'User Management',
    location: 'Admin — Manage Users page (header)',
    hint: 'Creating accounts, setting roles (author, reviewer, admin), and deactivating users.',
  },
  {
    key: 'admin.audit',
    label: 'Audit Log',
    location: 'Admin — Audit Log page (header)',
    hint: 'Immutable record of all create, update, and delete actions in the system.',
  },
]

/** Quick lookup: key → registry entry */
export const HELP_KEY_MAP = Object.fromEntries(
  HELP_FEATURE_KEYS.map(e => [e.key, e])
)
