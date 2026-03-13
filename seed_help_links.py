"""
seed_help_links.py — Populate the help_links table with end-user descriptions.

All entries are created with enabled=False so admins can review and toggle on
only the locations they want. Running this script again is safe: existing entries
with descriptions are skipped; entries with empty descriptions are backfilled.

Usage:
    python seed_help_links.py
"""

import sys, os
sys.path.insert(0, os.path.dirname(__file__))

# The canonical ENTRIES list and seed_help_links() live inside the backend package
# so the same data is used both here and during app startup.
from backend.utils.seed_help_links import seed_help_links  # noqa: E402


def run():
    from backend.app import create_app
    from backend.models import db, HelpLink

    app = create_app()
    with app.app_context():
        created, updated, skipped = seed_help_links(db, HelpLink)
        print(f"✅  Created {created}, updated {updated}, skipped {skipped} help link(s).")


if __name__ == "__main__":
    run()
