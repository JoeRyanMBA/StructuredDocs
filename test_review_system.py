#!/usr/bin/env python3
"""
Test script for the token-based review system

This script demonstrates the complete workflow:
1. Generate a review token for external reviewer access
2. Simulate external reviewer accessing the portal
3. Submit feedback through the token-based system
"""

import requests
import json
from datetime import datetime

# Backend base URL
BASE_URL = "http://localhost:5050"

def test_token_generation():
    """Test generating a review token"""
    print("🔐 Testing Review Token Generation...")
    
    token_data = {
        "review_id": 1,  # Assuming we have a review with ID 1
        "reviewer_email": "external.reviewer@company.com",
        "reviewer_name": "External Reviewer"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/review-tokens/generate", json=token_data)
        
        if response.status_code == 200:
            result = response.json()
            token = result.get('token')
            print(f"✅ Token generated successfully: {token[:20]}...")
            print(f"📧 Email template ready for: {result.get('reviewer_email')}")
            return token
        else:
            print(f"❌ Token generation failed: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend server. Make sure it's running on port 5050.")
        return None

def test_token_validation(token):
    """Test validating and using a review token"""
    if not token:
        print("⏭️ Skipping token validation - no token available")
        return
        
    print(f"\n🔍 Testing Token Validation for token: {token[:20]}...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/review-tokens/validate/{token}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Token is valid!")
            print(f"📋 Review ID: {result.get('review_id')}")
            print(f"📧 Reviewer: {result.get('reviewer_name')} ({result.get('reviewer_email')})")
            return result
        else:
            print(f"❌ Token validation failed: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend server.")
        return None

def test_feedback_submission(token):
    """Test submitting feedback through the token"""
    if not token:
        print("⏭️ Skipping feedback submission - no token available")
        return
        
    print(f"\n📝 Testing Feedback Submission...")
    
    feedback_data = {
        "accuracy_rating": 4,
        "clarity_rating": 5,
        "completeness_rating": 3,
        "accuracy_comments": "The technical details are mostly accurate, but section 3.2 needs clarification.",
        "clarity_comments": "Very well written and easy to understand.",
        "completeness_comments": "Missing some implementation details in the deployment section.",
        "general_comments": "Overall excellent work. Just needs minor revisions.",
        "suggestions": "Consider adding more code examples and deployment diagrams."
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/review-tokens/{token}/feedback", json=feedback_data)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Feedback submitted successfully!")
            print(f"📊 Feedback ID: {result.get('feedback_id')}")
            print(f"🎯 Average Rating: {result.get('average_rating')}")
            return result
        else:
            print(f"❌ Feedback submission failed: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend server.")
        return None

def test_complete_workflow():
    """Test the complete review workflow"""
    print("🚀 Testing Complete Token-Based Review System\n")
    print("=" * 60)
    
    # Step 1: Generate token
    token = test_token_generation()
    
    # Step 2: Validate token
    validation_result = test_token_validation(token)
    
    # Step 3: Submit feedback
    feedback_result = test_feedback_submission(token)
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 WORKFLOW SUMMARY")
    print("=" * 60)
    
    if token:
        print("✅ Token Generation: SUCCESS")
        print(f"   🔗 External URL: http://localhost:5173/review/{token}")
    else:
        print("❌ Token Generation: FAILED")
        
    if validation_result:
        print("✅ Token Validation: SUCCESS")
    else:
        print("❌ Token Validation: FAILED")
        
    if feedback_result:
        print("✅ Feedback Submission: SUCCESS")
    else:
        print("❌ Feedback Submission: FAILED")
    
    print("\n🎯 Next Steps:")
    print("1. Create a review in the system")
    print("2. Generate tokens for external reviewers")
    print("3. Share review URLs with stakeholders")
    print("4. Collect and incorporate feedback")

if __name__ == "__main__":
    test_complete_workflow()
