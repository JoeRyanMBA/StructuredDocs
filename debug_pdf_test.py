#!/usr/bin/env python3

import sys
import os

# Add the backend directory to the Python path
sys.path.insert(0, '/workspaces/StructuredDocs/backend')

from flask import Flask
from models import db, Publication
from routes.publications import generate_pdf
import traceback

def test_pdf_generation():
    """Test PDF generation with debug output"""
    
    # Create a minimal Flask app for database context
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////workspaces/StructuredDocs/instance/structured_docs.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize database
    db.init_app(app)
    
    with app.app_context():
        try:
            # Try to get a publication
            pub = Publication.query.first()
            
            if not pub:
                print("No publications found in database")
                return False
                
            print(f"Testing PDF generation for publication: {pub.title} (ID: {pub.id})")
            
            # Create a simple tree structure for testing
            test_tree = [{
                'id': 1,
                'topic_id': 1,
                'title': 'Test Topic',
                'content': '<p>This is test content for debugging PDF generation.</p>',
                'position': 1,
                'children': []
            }]
            
            # Test with background image
            print("\n--- Testing with background image ---")
            bg_path = os.path.join('/workspaces/StructuredDocs/backend', 'static', 'backgrounds', 'SC Cover Background.png')
            print(f"Background image path: {bg_path}")
            print(f"Background image exists: {os.path.exists(bg_path)}")
            
            # Test footer logo paths
            footer_logo = os.path.join('/workspaces/StructuredDocs/backend', 'static', 'backgrounds', 'USCENSUS_Footer_Logo.png')
            title_logo = os.path.join('/workspaces/StructuredDocs/backend', 'static', 'backgrounds', 'USCENSUS_Title_Page_Logo.png')
            print(f"Footer logo exists: {os.path.exists(footer_logo)}")
            print(f"Title logo exists: {os.path.exists(title_logo)}")
            
            # Generate PDF
            pdf_buffer = generate_pdf(pub, test_tree, 'default', bg_path)
            
            if pdf_buffer:
                output_path = '/workspaces/StructuredDocs/debug_pdf_test.pdf'
                with open(output_path, 'wb') as f:
                    f.write(pdf_buffer.getvalue())
                print(f"✅ PDF generated successfully: {output_path}")
                print(f"PDF size: {len(pdf_buffer.getvalue())} bytes")
                return True
            else:
                print("❌ PDF generation returned empty buffer")
                return False
                
        except Exception as e:
            print(f"❌ Error during PDF generation: {e}")
            print("Full traceback:")
            traceback.print_exc()
            return False

if __name__ == "__main__":
    success = test_pdf_generation()
    sys.exit(0 if success else 1)
