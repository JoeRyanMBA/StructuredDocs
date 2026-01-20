#!/usr/bin/env python3
"""
Helper to inspect and optionally delete ImportImage rows whose files are missing.
- Safe dry run by default (no DB writes).
- Confirms before deleting when --no-dry-run is used.
- Locates backend/frontend paths relative to the repo root or STRUCTUREDDOCS_ROOT.
"""

import argparse
import os
import sys
from pathlib import Path
from typing import List, Optional, Tuple


def locate_repo_root(explicit_root: Optional[str]) -> Path:
    """Return the repo root by env override, explicit flag, or directory walk."""
    if explicit_root:
        return Path(explicit_root).expanduser().resolve()

    env_root = os.getenv("STRUCTUREDDOCS_ROOT")
    if env_root:
        return Path(env_root).expanduser().resolve()

    here = Path(__file__).resolve()
    for candidate in [here, *here.parents]:
        if (candidate / "backend").exists() and (candidate / "frontend").exists():
            return candidate
    raise SystemExit("Could not locate repo root; set --root or STRUCTUREDDOCS_ROOT.")


def ensure_backend_on_path(repo_root: Path) -> None:
    backend_path = repo_root / "backend"
    if str(backend_path) not in sys.path:
        sys.path.insert(0, str(backend_path))


def confirm(prompt: str, assume_yes: bool) -> bool:
    if assume_yes:
        return True
    answer = input(f"{prompt} [y/N]: ").strip().lower()
    return answer in {"y", "yes"}


class ImageCheckResult:
    def __init__(
        self,
        doc_id: int,
        db_images: list,
        missing: List[Tuple[object, Path, Path]],
        present: List[Tuple[object, bool, bool]],
        backend_dir: Path,
        frontend_dir: Path,
    ) -> None:
        self.doc_id = doc_id
        self.db_images = db_images
        self.missing = missing
        self.present = present
        self.backend_dir = backend_dir
        self.frontend_dir = frontend_dir


def analyze_import_images(doc_id: int, repo_root: Path):
    """Fetch ImportImage rows and flag those without files."""
    backend_dir = repo_root / "backend/static/images/imports" / str(doc_id)
    frontend_dir = repo_root / "frontend/public/images/imports" / str(doc_id)

    from models import ImportImage  # imported lazily after sys.path setup
    from app import app

    with app.app_context():
        db_images = ImportImage.query.filter_by(document_id=doc_id).all()

    missing: List[Tuple[object, Path, Path]] = []
    present: List[Tuple[object, bool, bool]] = []

    for img in db_images:
        filename = Path(img.filename).name
        backend_path = backend_dir / filename
        frontend_path = frontend_dir / filename

        exists_backend = backend_path.exists()
        exists_frontend = frontend_path.exists()

        if not exists_backend and not exists_frontend:
            missing.append((img, backend_path, frontend_path))
        else:
            present.append((img, exists_backend, exists_frontend))

    return ImageCheckResult(doc_id, db_images, missing, present, backend_dir, frontend_dir)


def print_report(result: ImageCheckResult) -> None:
    print("=" * 80)
    print(f"IMPORT {result.doc_id} IMAGE CHECK")
    print("=" * 80)
    print(f"Backend dir : {result.backend_dir}")
    print(f"Frontend dir: {result.frontend_dir}")
    print(f"Total DB records : {len(result.db_images)}")
    print(f"Missing on disk : {len(result.missing)}")
    print(f"Present on disk : {len(result.present)}")

    if result.missing:
        print("\nWill delete these records if run with --no-dry-run:")
        for img, backend_path, frontend_path in result.missing:
            print(
                f"- id={img.id} filename={img.filename} | "
                f"backend: {'missing' if not backend_path.exists() else 'ok'}, "
                f"frontend: {'missing' if not frontend_path.exists() else 'ok'}"
            )

    if result.present:
        print("\nRecords that still have at least one file present:")
        for img, backend_ok, frontend_ok in result.present:
            status = []
            if backend_ok:
                status.append("backend")
            if frontend_ok:
                status.append("frontend")
            print(f"- id={img.id} filename={img.filename} | files present: {', '.join(status)}")


def delete_missing_records(result: ImageCheckResult, assume_yes: bool) -> None:
    if not result.missing:
        print("No missing records to delete.")
        return

    if not confirm(
        f"Delete {len(result.missing)} DB record(s) for import {result.doc_id}?", assume_yes
    ):
        print("Aborted; no changes made.")
        return

    from app import app, db

    with app.app_context():
        for img, _, _ in result.missing:
            db.session.delete(img)
        db.session.commit()
    print(f"Deleted {len(result.missing)} record(s) for import {result.doc_id}.")


def check_source_document(doc_id: int) -> None:
    """Report whether the source document is still available for re-import."""
    from app import app
    from models import ImportedDocument

    with app.app_context():
        doc = ImportedDocument.query.get(doc_id)
        if not doc:
            print(f"Source document {doc_id} not found in DB.")
            return

        print("- Source document present in DB")
        print(f"  id       : {doc.id}")
        print(f"  title    : {doc.title}")
        print(f"  filename : {doc.original_filename}")
        print(f"  status   : {doc.status}")

        if not doc.file_path:
            print("  file_path: missing in DB")
            return

        file_path = Path(doc.file_path)
        if file_path.exists():
            size = file_path.stat().st_size
            print(f"  file_path: exists at {file_path} ({size:,} bytes)")
        else:
            print(f"  file_path: missing on disk ({file_path})")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Inspect and optionally delete ImportImage rows with missing files."
    )
    parser.add_argument(
        "--doc-id",
        type=int,
        nargs="+",
        default=[64],
        help="Document ID(s) to check (space-separated).",
    )
    parser.add_argument(
        "--no-dry-run",
        action="store_true",
        help="Delete missing image records after confirmation.",
    )
    parser.add_argument(
        "--yes",
        action="store_true",
        help="Skip confirmation prompts (use with caution).",
    )
    parser.add_argument(
        "--check-source",
        action="store_true",
        help="Also report whether the source document file is available.",
    )
    parser.add_argument(
        "--root",
        type=str,
        help="Override repo root path (defaults to STRUCTUREDDOCS_ROOT or autodetect).",
    )

    args = parser.parse_args()

    repo_root = locate_repo_root(args.root)
    ensure_backend_on_path(repo_root)

    # Imports after sys.path is prepared
    _ = __import__("app")
    _ = __import__("models")

    for doc_id in args.doc_id:
        result = analyze_import_images(doc_id, repo_root)
        print_report(result)
        if args.check_source:
            check_source_document(doc_id)
        if args.no_dry_run:
            delete_missing_records(result, assume_yes=args.yes)
        else:
            print("Dry run only; no database changes made.")
        print("\n")


if __name__ == "__main__":
    main()
