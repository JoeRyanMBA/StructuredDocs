"""
seed_help_links.py — Populate the help_links table with end-user descriptions.

All entries are created with enabled=False so admins can review and toggle on
only the locations they want. Running this script again is safe: existing entries
are skipped (not overwritten).

Usage:
    python seed_help_links.py
"""

import sys, os
sys.path.insert(0, os.path.dirname(__file__))

ENTRIES = [
    # ── Authoring ─────────────────────────────────────────────────────────
    {
        "feature_key": "topics.list",
        "title": "Topics",
        "description": (
            "Topics are the core content units in StructuredDocs. Each topic holds a "
            "piece of documentation — an article, procedure, or reference entry — that "
            "can be organised into collections, sent for review, and included in publications. "
            "Use this page to browse all your topics, filter by status or tag, and open any "
            "topic to view or edit it."
        ),
    },
    {
        "feature_key": "topics.create",
        "title": "Create Topic",
        "description": (
            "Give your topic a title and write your content using the rich-text editor. "
            "You can assign the topic to a collection, set its status (Draft, In Review, "
            "Approved), and add tags to make it easier to find. Save at any time — your "
            "topic won't be visible in publications until you include it in one."
        ),
    },
    {
        "feature_key": "topics.edit",
        "title": "Edit Topic",
        "description": (
            "Edit your topic's content using the built-in rich-text editor. Format text, "
            "insert images, add tables, and embed reusable Snippets for audience-specific "
            "content. Use the toolbar at the top to access formatting options. "
            "Click Save when you're done — unsaved changes will prompt a warning if you "
            "try to leave the page."
        ),
    },
    {
        "feature_key": "topics.view",
        "title": "Topic Detail",
        "description": (
            "View a topic's content and take action from this page: request a review from "
            "a subject matter expert, add the topic to a publication, or export it. "
            "The status badge shows whether the topic is a Draft, In Review, or Approved. "
            "Use the breadcrumbs at the top to navigate back to the collection or project."
        ),
    },

    # ── Collections ───────────────────────────────────────────────────────
    {
        "feature_key": "collections.dashboard",
        "title": "Collections",
        "description": (
            "Collections group related topics together into a structured hierarchy — "
            "similar to chapters or sections in a book. Use this dashboard to create new "
            "collections, browse existing ones, and see how your content is organised. "
            "Collections can be nested inside other collections to represent sub-sections."
        ),
    },
    {
        "feature_key": "collections.organize",
        "title": "Organise Collection",
        "description": (
            "Drag and drop topics to set the order they appear in this collection. "
            "The order you set here is the order topics will appear when the collection "
            "is published or exported as a PDF. Changes are saved automatically."
        ),
    },

    # ── Projects ──────────────────────────────────────────────────────────
    {
        "feature_key": "projects.list",
        "title": "Projects",
        "description": (
            "Projects are the top-level organiser in StructuredDocs. Each project "
            "contains collections of topics, along with tasks, milestones, and "
            "stakeholders to help you manage the full lifecycle of creating, reviewing, "
            "and publishing documentation. Use this page to create new projects or open "
            "an existing one to see its contents."
        ),
    },
    {
        "feature_key": "projects.tasks",
        "title": "Tasks",
        "description": (
            "Tasks let you track the work items needed to complete your documentation "
            "project — for example, 'Write first draft of Chapter 3' or 'SME review "
            "of safety procedures'. Assign tasks to team members, set due dates, and "
            "mark them complete as you progress."
        ),
    },
    {
        "feature_key": "projects.milestones",
        "title": "Milestones",
        "description": (
            "Milestones mark key dates in your documentation project — such as a first "
            "draft deadline, a review sign-off date, or a publication target. "
            "Link tasks to milestones to track whether you're on schedule."
        ),
    },
    {
        "feature_key": "projects.stakeholders",
        "title": "Stakeholders",
        "description": (
            "Stakeholders are the people involved in your documentation project — "
            "subject matter experts, approvers, sponsors, and reviewers. Adding them "
            "here makes it easy to reference who is responsible for what and ensures "
            "the right people are included when requesting reviews."
        ),
    },

    # ── Import ────────────────────────────────────────────────────────────
    {
        "feature_key": "import.upload",
        "title": "Import Content",
        "description": (
            "Import existing documents into StructuredDocs without retyping them. "
            "Upload a Word (.docx) or Markdown (.md) file and the system will "
            "automatically convert it into topics, using headings to define where "
            "each topic begins. You can review and edit the result before anything "
            "is saved to your topic library."
        ),
    },
    {
        "feature_key": "import.dashboard",
        "title": "Import Dashboard",
        "description": (
            "Track all your document imports from this dashboard. See which imports "
            "are still being processed, which are ready for you to review, and which "
            "have already been committed into your topic library. Click any import to "
            "open its review page."
        ),
    },
    {
        "feature_key": "import.review",
        "title": "Review Import",
        "description": (
            "Before an imported document becomes topics in your library, you can review "
            "its structure here. Check how headings were parsed into individual topics, "
            "edit titles and content as needed, and then Approve to commit everything "
            "or Reject to discard the import."
        ),
    },

    # ── Publishing ────────────────────────────────────────────────────────
    {
        "feature_key": "publish.dashboard",
        "title": "Publications",
        "description": (
            "A publication is a curated, ordered set of topics assembled for "
            "distribution to your audience. From this dashboard you can create new "
            "publications, manage which topics they include, and export them as "
            "a formatted PDF or a self-contained mobile knowledge base."
        ),
    },
    {
        "feature_key": "publish.pdf",
        "title": "Export as PDF",
        "description": (
            "Export your publication as a professionally formatted PDF document. "
            "Choose a layout style — Default, Corporate, Academic, or Compact — "
            "to match your organisation's style guide. You can also add a cover "
            "background image. The PDF includes a table of contents and page numbers."
        ),
    },
    {
        "feature_key": "publish.mobile-kb",
        "title": "Export Mobile Knowledge Base",
        "description": (
            "Export your publication as a self-contained HTML knowledge base — a single "
            "file that works entirely offline and is optimised for reading on mobile "
            "devices. Share it by email, post it to an intranet, or distribute it on "
            "a USB drive. No internet connection is needed to read it."
        ),
    },

    # ── Reviews ───────────────────────────────────────────────────────────
    {
        "feature_key": "reviews.dashboard",
        "title": "Reviews",
        "description": (
            "The review workflow lets subject matter experts (SMEs) read your topics and "
            "leave inline feedback before content is published. This dashboard shows all "
            "your pending, in-progress, and completed reviews so you can track what "
            "still needs attention."
        ),
    },
    {
        "feature_key": "reviews.request",
        "title": "Request a Review",
        "description": (
            "Ask a subject matter expert to review a topic. You can select an internal "
            "reviewer from your team, or generate a secure, time-limited link to share "
            "with an external reviewer who doesn't have an account. The reviewer can "
            "leave comments directly on the content without needing to log in."
        ),
    },
    {
        "feature_key": "reviews.feedback",
        "title": "Review Feedback",
        "description": (
            "Read and respond to the feedback your reviewer left. For each comment you "
            "can Accept the suggested change, Reject it with a note, or mark it as "
            "Modified to indicate you've addressed it differently. Once all feedback is "
            "resolved, mark the review complete."
        ),
    },
    {
        "feature_key": "reviews.bulk",
        "title": "Bulk Review",
        "description": (
            "Send multiple topics to the same reviewer in a single session — ideal when "
            "a subject matter expert needs to sign off on an entire collection or project "
            "at once. The reviewer receives one link and can navigate between all assigned "
            "topics without switching sessions."
        ),
    },

    # ── Snippets ──────────────────────────────────────────────────────────
    {
        "feature_key": "snippets.library",
        "title": "Snippets",
        "description": (
            "Snippets are reusable blocks of content you write once and insert into any "
            "topic. Use them for standard disclaimers, safety warnings, repeated "
            "procedures, or audience-specific content. When you update a snippet, the "
            "change appears everywhere it's used the next time the topic is published."
        ),
    },

    # ── Variables ─────────────────────────────────────────────────────────
    {
        "feature_key": "variables.list",
        "title": "Variables",
        "description": (
            "Variables are named placeholders you insert into topics using double "
            "curly braces — for example {{product_name}} or {{version}}. Define the "
            "value for each variable here. When you export a publication, every "
            "placeholder is automatically replaced with the current value, so you "
            "only need to update the version number in one place."
        ),
    },

    # ── Tags ──────────────────────────────────────────────────────────────
    {
        "feature_key": "tags.list",
        "title": "Tags",
        "description": (
            "Tags let you categorise topics, tasks, images, and other content with "
            "short labels — for example 'safety', 'onboarding', or 'version-2'. "
            "Apply tags throughout the system to make content easier to filter, "
            "search, and group when building publications."
        ),
    },

    # ── Links ─────────────────────────────────────────────────────────────
    {
        "feature_key": "links.list",
        "title": "Links",
        "description": (
            "This page lists all the cross-topic links in your content. Use it to "
            "find broken links (topics that have been deleted or moved), see which "
            "topics reference other topics, and keep your internal linking consistent "
            "across your documentation library."
        ),
    },

    # ── Images ────────────────────────────────────────────────────────────
    {
        "feature_key": "images.list",
        "title": "Images",
        "description": (
            "Browse all images that have been uploaded directly or extracted from "
            "imported documents. From here you can see which topics each image appears "
            "in, copy the image URL to use it elsewhere, and remove images that are "
            "no longer needed."
        ),
    },

    # ── Admin ─────────────────────────────────────────────────────────────
    {
        "feature_key": "admin.dashboard",
        "title": "Admin Dashboard",
        "description": (
            "The admin dashboard gives system administrators a summary of the "
            "platform's current state: total users, content counts, and system health. "
            "From here you can manage user accounts, send announcements, review "
            "bug reports and feedback, view the audit log, and adjust system settings."
        ),
    },
    {
        "feature_key": "admin.users",
        "title": "User Management",
        "description": (
            "Create and manage user accounts for your StructuredDocs instance. "
            "Assign roles: Authors can create and edit content; Reviewers can leave "
            "feedback on topics shared with them; Admins have full access to all "
            "settings and user management. You can also deactivate accounts for "
            "users who no longer need access."
        ),
    },
    {
        "feature_key": "admin.audit",
        "title": "Audit Log",
        "description": (
            "The audit log is an immutable, time-stamped record of every create, "
            "update, and delete action taken in the system — who performed it, when, "
            "and on which record. Use it to investigate unexpected changes, meet "
            "compliance requirements, or understand how your content has evolved over time."
        ),
    },
]


def run():
    from backend.app import create_app
    from backend.models import db, HelpLink

    app = create_app()
    with app.app_context():
        created = 0
        skipped = 0
        for entry in ENTRIES:
            existing = HelpLink.query.filter_by(feature_key=entry["feature_key"]).first()
            if existing:
                skipped += 1
                continue
            link = HelpLink(
                feature_key=entry["feature_key"],
                title=entry["title"],
                description=entry["description"],
                kb_url="",
                enabled=False,
            )
            db.session.add(link)
            created += 1

        db.session.commit()
        print(f"✅  Created {created} help link(s).  Skipped {skipped} already-existing.")


if __name__ == "__main__":
    run()
