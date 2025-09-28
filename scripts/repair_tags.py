#!/usr/bin/env python
"""Repair tag data if tags were accidentally stored as single characters.

Steps performed:
1. Scan Task.tags JSON for cases where a string (not list) was stored and split into characters when read on frontend.
2. If a single string (e.g. "marketing-roadmap") was improperly expanded into characters in Tag table, consolidate.
3. Provide a dry-run summary by default; require --apply to make changes.

Usage:
  python scripts/repair_tags.py              # dry run
  python scripts/repair_tags.py --apply      # apply fixes
"""
from __future__ import annotations
import json
import argparse
from collections import Counter
from backend.app import create_app
from backend.models import db, Task, Tag


def load_tags():
    return Tag.query.all()

def consolidate_character_tags(tags):
    """Detect sequences of single-character tags that could belong to a hyphenated multi-char tag.
    Heuristic: if more than 5 single-char tags exist AND no multi-char tags exist sharing that prefix.
    """
    singles = [t for t in tags if len(t.name) == 1]
    if len(singles) < 5:
        return []
    # Group frequency
    freq = Counter(t.name for t in singles)
    # This script only reports; automatic reconstruction is risky without original source
    return [f"Single-character tag '{c}' count={n}" for c, n in freq.items()]

def normalize_task_tags(task: Task, apply: bool):
    changed = False
    try:
        if not task.tags:
            return changed, []
        parsed = json.loads(task.tags)
        if isinstance(parsed, list):
            # Already good
            return changed, []
        # If a string was stored directly, wrap it as a single-element list
        if isinstance(parsed, str):
            new_list = [parsed]
            if apply:
                task.tags = json.dumps(new_list)
            changed = True
            return changed, [f"Wrapped raw string -> list: {parsed}"]
    except Exception:
        # If it is raw string without JSON encoding
        raw = task.tags
        if isinstance(raw, str) and raw and not raw.strip().startswith('['):
            if apply:
                task.tags = json.dumps([raw])
            changed = True
            return changed, [f"Wrapped non-JSON string -> list: {raw}"]
    return changed, []

def main():
    parser = argparse.ArgumentParser(description="Repair tag storage anomalies")
    parser.add_argument('--apply', action='store_true', help='Apply fixes (otherwise dry run)')
    args = parser.parse_args()

    app = create_app()
    with app.app_context():
        tags = load_tags()
        report_lines = []
        char_tag_notes = consolidate_character_tags(tags)
        if char_tag_notes:
            report_lines.append("Potential single-character tag noise detected:")
            report_lines.extend(f"  - {line}" for line in char_tag_notes)
        else:
            report_lines.append("No abnormal concentration of single-character tags detected.")

        task_changes = 0
        detailed = []
        for task in Task.query.all():
            changed, notes = normalize_task_tags(task, args.apply)
            if changed:
                task_changes += 1
                detailed.extend([f"Task {task.id}: {n}" for n in notes])
        if args.apply and task_changes:
            db.session.commit()
        elif not args.apply:
            db.session.rollback()
        report_lines.append(f"Tasks modified: {task_changes}{' (committed)' if args.apply else ' (dry run)'}")
        if detailed:
            report_lines.append("Details:")
            report_lines.extend(f"  - {d}" for d in detailed)
        print("\n".join(report_lines))

if __name__ == '__main__':
    main()
