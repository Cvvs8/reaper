#!/usr/bin/env python3
"""
Test script for Reaper Agent with audit trail and dry run features
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
