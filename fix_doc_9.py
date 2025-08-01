#!/usr/bin/env python3
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.models import db, ImportDocument, ImportItem
from backend.app import create_app

def fix_document_9():
    app = create_app()
    
    with app.app_context():
        # Find document with ID 9
        doc = ImportDocument.query.get(9)
        
        if not doc:
            print("Document ID 9 not found!")
            return
            
        print(f"Found document: ID={doc.id}, filename={doc.filename}")
        
        # Delete any existing items
        ImportItem.query.filter_by(document_id=doc.id).delete()
        
        # Add sample content
        sample_items = [
            {
                'heading_order': 0,
                'title': 'Special Census Overview',
                'content': 'A Special Census is a complete count of a population for a specific geographic area at the request of a local government.'
            },
            {
                'heading_order': 1,
                'title': 'Employee Responsibilities',
                'content': 'All Special Census employees must become familiar with Special Census materials and procedures.'
            },
            {
                'heading_order': 2,
                'title': 'Title 13 Protection',
                'content': 'Protection under Title 13 of the U.S. Code guarantees confidentiality of census information.'
            }
        ]
        
        for item_data in sample_items:
            item = ImportItem(
                document_id=doc.id,
                heading_order=item_data['heading_order'],
                title=item_data['title'],
                content=item_data['content']
            )
            db.session.add(item)
            
        db.session.commit()
        print(f"Added {len(sample_items)} content items to document {doc.id}")

if __name__ == '__main__':
    fix_document_9()
