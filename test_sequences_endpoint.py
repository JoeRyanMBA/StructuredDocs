#!/usr/bin/env python3
"""Diagnostic script to check what sequential review sequences API returns."""
import json
import sys
sys.path.insert(0, '/workspaces/StructuredDocs')

from backend.app import create_app
from backend.models import ReviewSequence, Topic, Stakeholder
from backend.extensions import db

# Create app and context
app = create_app()

with app.app_context():
    # Find a topic that has a sequence
    sequences = ReviewSequence.query.all()
    
    if not sequences:
        print("❌ No sequences found in database")
    else:
        print(f"✅ Found {len(sequences)} sequence(s)")
        for seq in sequences[:3]:  # Check first 3
            print(f"\n📋 Sequence ID: {seq.id}")
            print(f"   Topic ID: {seq.topic_id}")
            print(f"   Status: {seq.status}")
            print(f"   Steps in DB: {len(seq.steps)}")
            
            # Test to_dict WITHOUT include_steps
            dict_without = seq.to_dict()
            print(f"   to_dict() keys: {list(dict_without.keys())}")
            print(f"   'steps' in to_dict(): {'steps' in dict_without}")
            
            # Test to_dict WITH include_steps
            dict_with = seq.to_dict(include_steps=True)
            print(f"   to_dict(include_steps=True) keys: {list(dict_with.keys())}")
            print(f"   'steps' in to_dict(include_steps=True): {'steps' in dict_with}")
            
            if 'steps' in dict_with:
                print(f"   Steps returned: {len(dict_with['steps'])}")
                for step in dict_with['steps'][:2]:
                    print(f"     - Step {step.get('step_order')}: {step.get('step_name')} (reviewer_id: {step.get('reviewer_id')}, reviewer_name: {step.get('reviewer_name')})")
