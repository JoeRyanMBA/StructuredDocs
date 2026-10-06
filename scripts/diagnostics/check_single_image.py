#!/usr/bin/env python3
"""
Check if a specific imported image exists in the database and on disk.
"""
import sys
from pathlib import Path

sys.path.insert(0, '/workspaces/StructuredDocs')
sys.path.insert(0, '/workspaces/StructuredDocs/backend')

from backend import create_app
from backend.models import ImportImage

app = create_app()

image_filename = 'image15_462f879d.png'

with app.app_context():
    matches = ImportImage.query.filter_by(filename=image_filename).all()
    if not matches:
        print(f'❌ No ImportImage record found for {image_filename}')
        sys.exit(1)
    for img in matches:
        print(f'Found DB record:')
        print(f'  document_id: {img.document_id}')
        print(f'  filename:    {img.filename}')
        print(f'  backend_path: {img.backend_path}')
        print(f'  frontend_path: {img.frontend_path}')
        backend_exists = Path(img.backend_path).exists()
        frontend_exists = Path(img.frontend_path).exists()
        print(f'  Exists on backend:  {backend_exists}')
        print(f'  Exists on frontend: {frontend_exists}')
        print(f'  public_url: {img.public_url}')
        print(f'  created_at: {img.created_at}')
        print(f'  width: {img.width}, height: {img.height}, format: {img.format}')
        print(f'  file_size: {img.file_size}, mime_type: {img.mime_type}')
        print('---')
