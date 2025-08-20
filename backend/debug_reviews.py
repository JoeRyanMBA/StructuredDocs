#!/usr/bin/env python3

print("Step 1: Testing basic imports...")
from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
print("Flask imports successful")

print("Step 2: Testing SQLAlchemy imports...")
from sqlalchemy import or_, and_
print("SQLAlchemy imports successful")

print("Step 3: Testing models imports...")
from models import db, Topic, Collection, ImportDocument, Review, Stakeholder
print("Models imports successful")

print("Step 4: Creating blueprint...")
reviews_bp = Blueprint('reviews', __name__, url_prefix='/api/reviews')
print("Blueprint created successfully")

print("Step 5: Testing Review model methods...")
try:
    # Test that the Review model has the to_dict method
    import inspect
    if hasattr(Review, 'to_dict'):
        print("Review.to_dict method exists")
    else:
        print("ERROR: Review.to_dict method missing")
        
    # Try to create a simple route
    @reviews_bp.route('/test')
    def test():
        return jsonify({"status": "ok"})
    print("Route created successfully")
    
except Exception as e:
    print(f"ERROR in step 5: {e}")
    import traceback
    traceback.print_exc()

print("All tests passed!")
print(f"reviews_bp type: {type(reviews_bp)}")
print(f"reviews_bp name: {reviews_bp.name}")
