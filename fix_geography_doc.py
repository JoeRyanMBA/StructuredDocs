#!/usr/bin/env python3
"""
Quick script to add sample content to the Geography.docx import document
so we can test the review workflow.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.models import db, ImportDocument, ImportItem
from backend.app import create_app

def add_sample_content():
    app = create_app()
    
    with app.app_context():
        # Find the Geography.docx document
        doc = ImportDocument.query.filter_by(filename='Geography.docx').first()
        
        if not doc:
            print("Geography.docx document not found!")
            return
            
        print(f"Found document: ID={doc.id}, filename={doc.filename}")
        
        # Delete any existing items
        ImportItem.query.filter_by(document_id=doc.id).delete()
        
        # Add sample content items
        sample_items = [
            {
                'heading_order': 0,
                'title': 'Introduction to Geography',
                'content': 'Geography is the study of places and the relationships between people and their environments. It examines the physical characteristics of Earth\'s surface and the human societies spread across it.'
            },
            {
                'heading_order': 1,
                'title': 'Physical Geography',
                'content': 'Physical geography focuses on the natural environment and the processes that shape it. This includes the study of landforms, climate, water bodies, soil, and ecosystems. Key concepts include plate tectonics, weathering and erosion, and the water cycle.'
            },
            {
                'heading_order': 2,
                'title': 'Human Geography',
                'content': 'Human geography examines how human activities are distributed across space, how they use and perceive space, and how they create and sustain places. Topics include population distribution, urbanization, cultural landscapes, and economic activities.'
            },
            {
                'heading_order': 3,
                'title': 'Geographic Information Systems',
                'content': 'GIS technology integrates hardware, software, and data for capturing, managing, analyzing, and displaying all forms of geographically referenced information. It allows us to view, understand, question, interpret, and visualize data in many ways.'
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
        print(f"Added {len(sample_items)} content items to Geography.docx")
        print("Document is now ready for review!")

if __name__ == '__main__':
    add_sample_content()
