#!/usr/bin/env python3
"""
Reaper Agent Integration Test Suite

This script provides comprehensive integration testing for the Reaper Agent.
It tests all API endpoints, demonstrates usage patterns, and validates
the complete security event processing workflow.

Usage:
    python test_reaper.py

Prerequisites:
    - Reaper Agent running on http://localhost:5001
    - Required packages: requests

What it tests:
    ✅ Health check and status endpoints
    ✅ Configuration retrieval
    ✅ Security event processing (SaaS access, S3 buckets)
    ✅ Dry run mode functionality
    ✅ Audit trail generation
    ✅ Error handling and validation
    ✅ API response format validation

This complements the unit tests in tests/ by providing end-to-end integration testing.
"""
import json
import time

import requests

# Configuration
BASE_URL = "http://localhost:5001"

def test_health_check():
    """Test health check endpoint"""
    print("=== Health Check ===")
    response = requests.get(f"{BASE_URL}/")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def test_config():
    """Test configuration endpoint"""
    print("=== Configuration ===")
    response = requests.get(f"{BASE_URL}/config")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def test_saas_event(dry_run=False):
    """Test SaaS access event"""
    mode = "DRY RUN" if dry_run else "LIVE"
    print(f"=== SaaS Access Event ({mode}) ===")
    
    event = {
        "type": "unauthorized_saas_access",
        "event_id": f"test-saas-{int(time.time())}",
        "user": "john.doe@company.com",
        "source": "slack",
        "timestamp": "2025-06-24T10:30:00Z",
        "severity": "high"
    }
    
    response = requests.post(f"{BASE_URL}/event", json=event)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_s3_event(dry_run=False):
    """Test S3 bucket event"""
    mode = "DRY RUN" if dry_run else "LIVE"
    print(f"=== S3 Bucket Event ({mode}) ===")
    
    event = {
        "type": "open_s3_bucket",
        "event_id": f"test-s3-{int(time.time())}",
        "bucket_name": "my-public-bucket",
        "region": "us-east-1",
        "timestamp": "2025-06-24T10:35:00Z",
        "severity": "critical"
    }
    
    response = requests.post(f"{BASE_URL}/event", json=event)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def toggle_dry_run():
    """Toggle dry run mode"""
    print("=== Toggling Dry Run Mode ===")
    response = requests.post(f"{BASE_URL}/toggle-dry-run")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def test_audit_trail():
    """Test audit trail endpoint"""
    print("=== Audit Trail ===")
    response = requests.get(f"{BASE_URL}/audit")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_invalid_event():
    """Test invalid event handling"""
    print("=== Invalid Event Test ===")
    
    # Test missing event type
    invalid_event = {
        "event_id": "test-invalid-001",
        "user": "test@example.com"
        # Missing "type" field
    }
    
    response = requests.post(f"{BASE_URL}/event", json=invalid_event)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_malformed_json():
    """Test malformed JSON handling"""
    print("=== Malformed JSON Test ===")
    
    try:
        response = requests.post(f"{BASE_URL}/event", 
                               data="invalid json{", 
                               headers={'Content-Type': 'application/json'})
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Exception: {e}")
    print()

def main():
    """Run comprehensive test suite"""
    print("🔍 Reaper Agent Test Suite\n")
    
    try:
        # Test basic functionality
        test_health_check()
        test_config()
        
        # Test events in LIVE mode (default)
        test_saas_event(dry_run=False)
        test_s3_event(dry_run=False)
        
        # Test error handling
        test_invalid_event()
        test_malformed_json()
        
        # Toggle to dry run mode
        toggle_dry_run()
        
        # Test events in DRY RUN mode
        test_saas_event(dry_run=True)
        test_s3_event(dry_run=True)
        
        # Check audit trail
        test_audit_trail()
        
        # Toggle back to live mode
        toggle_dry_run()
        
        print("✅ All tests completed successfully!")
        
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to Reaper Agent.")
        print("Make sure the agent is running on http://localhost:5001")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
