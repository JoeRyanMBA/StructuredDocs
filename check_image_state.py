#!/usr/bin/env python3
"""
Check what's in the database and on disk after an import.
Run this from the workspace root: python3 check_image_databases_state.py
"""

import sys
import os
from pathlib import Path

# For checking without Flask
def check_db_state():
    """Check database state directly"""
    # Try to connect to postgres directly
    try:
        import subprocess
        import json
        
        # First, let's check if docker is running
        result = subprocess.run(['docker', 'ps'], capture_output=True, text=True)
        if result.returncode != 0:
            print("⚠️  Docker is not running. Starting container...")
            subprocess.run(['docker', 'compose', '-f', 'docker-compose.app.yml', 'up', '-d'], 
                          capture_output=True, text=True)
        
        # Give it a moment to start
        import time
        time.sleep(5)
        
        # Now try to query the database
        print("\n📊 QUERYING DATABASE FOR IMPORT IMAGES:")
        print("-" * 70)
        
        # Use docker exec to run psql command
        query = """
        SELECT 
            ii.id,
            ii.document_id,
            ii.filename,
            ii.public_url,
            ii.backend_path,
            ii.frontend_path,
            id.id as doc_id,
            id.filename as doc_filename,
            id.source_type
        FROM import_images ii
        LEFT JOIN import_documents id ON ii.document_id = id.id
        ORDER BY ii.document_id DESC
        LIMIT 20;
        """
        
        result = subprocess.run([
            'docker', 'compose', '-f', 'docker-compose.app.yml',
            'exec', '-T', 'postgres',
            'psql', '-U', 'postgres', '-d', 'structureddocs',
            '-c', query
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print(result.stdout)
        else:
            print(f"Query failed: {result.stderr}")
    except Exception as e:
        print(f"Error checking database: {e}")

def check_disk_state():
    """Check disk state"""
    print("\n💾 CHECKING DISK STATE:")
    print("-" * 70)
    
    backend_images = Path('/workspaces/StructuredDocs/backend/static/images/imports')
    frontend_images = Path('/workspaces/StructuredDocs/frontend/public/images/imports')
    
    print(f"\nBackend images root: {backend_images}")
    if backend_images.exists():
        for doc_dir in backend_images.iterdir():
            if doc_dir.is_dir():
                files = list(doc_dir.glob('*'))
                print(f"  📁 Document {doc_dir.name}: {len(files)} files")
                for f in files[:3]:
                    size = f.stat().st_size if f.is_file() else "DIR"
                    print(f"     - {f.name} ({size})")
    else:
        print("  (does not exist)")
    
    print(f"\nFrontend images root: {frontend_images}")
    if frontend_images.exists():
        for doc_dir in frontend_images.iterdir():
            if doc_dir.is_dir():
                files = list(doc_dir.glob('*'))
                print(f"  📁 Document {doc_dir.name}: {len(files)} files")
    else:
        print("  (does not exist)")

if __name__ == '__main__':
    print("=" * 70)
    print("🔍 CHECKING DATABASE AND DISK STATE")
    print("=" * 70)
    check_disk_state()
    check_db_state()
    print("\n" + "=" * 70)
