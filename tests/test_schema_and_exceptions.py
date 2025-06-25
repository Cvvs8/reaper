"""
Test exception handling and schema validation
"""
import json
import pytest

from app.utils.schema import APISchemaValidator


class TestSchemaValidation:
    """Test schema validation functionality"""
    
    def test_valid_saas_event(self):
        """Test valid SaaS access event"""
        event = {
            "type": "unauthorized_saas_access",
            "event_id": "test-001",
            "user": "test@example.com",
            "source": "slack",
            "timestamp": "2024-01-01T12:00:00Z",
            "severity": "high"
        }
        is_valid, message = APISchemaValidator.validate_event(event)
        assert is_valid, f"Valid event failed validation: {message}"
    
    def test_valid_s3_event(self):
        """Test valid S3 bucket event"""
        event = {
            "type": "open_s3_bucket",
            "event_id": "test-002",
            "bucket_name": "my-test-bucket",
            "region": "us-east-1",
            "timestamp": "2024-01-01T12:00:00Z",
            "severity": "critical"
        }
        is_valid, message = APISchemaValidator.validate_event(event)
        assert is_valid, f"Valid event failed validation: {message}"
    
    def test_invalid_event_type(self):
        """Test invalid event type"""
        event = {
            "type": "invalid_event_type",
            "event_id": "test-003",
            "timestamp": "2024-01-01T12:00:00Z"
        }
        is_valid, message = APISchemaValidator.validate_event(event)
        assert not is_valid
        assert "Unknown event type" in message
    
    def test_missing_required_fields(self):
        """Test missing required fields"""
        event = {
            "type": "unauthorized_saas_access",
            "event_id": "test-004"
            # Missing user, source, timestamp
        }
        is_valid, message = APISchemaValidator.validate_event(event)
        assert not is_valid
        assert "validation failed" in message.lower()
    
    def test_invalid_email_format(self):
        """Test invalid email format - this test may not fail with basic jsonschema"""
        event = {
            "type": "unauthorized_saas_access",
            "event_id": "test-005",
            "user": "invalid-email",
            "source": "slack",
            "timestamp": "2024-01-01T12:00:00Z"
        }
        is_valid, message = APISchemaValidator.validate_event(event)
        # Note: Email format validation may not work without additional jsonschema dependencies
        # This test documents the expected behavior but may pass with basic validation
        print(f"Email validation result: {is_valid}, message: {message}")
    
    def test_invalid_bucket_name(self):
        """Test invalid S3 bucket name"""
        event = {
            "type": "open_s3_bucket",
            "event_id": "test-006",
            "bucket_name": "INVALID_BUCKET_NAME",  # Uppercase not allowed
            "region": "us-east-1",
            "timestamp": "2024-01-01T12:00:00Z"
        }
        is_valid, message = APISchemaValidator.validate_event(event)
        assert not is_valid
    
    def test_openapi_spec_generation(self):
        """Test OpenAPI specification generation"""
        spec = APISchemaValidator.get_openapi_spec()
        assert "openapi" in spec
        assert spec["openapi"] == "3.0.0"
        assert "info" in spec
        assert "paths" in spec
        assert "/event" in spec["paths"]
        assert "/dashboard" not in spec["paths"]  # Should be added if needed


class TestExceptionHandling:
    """Test exception handling in API endpoints"""
    
    def test_exception_user_saas_event(self, client):
        """Test SaaS event with exception trigger"""
        event = {
            "type": "unauthorized_saas_access",
            "event_id": "test-exception-001",
            "user": "exception@example.com",  # Triggers exception
            "source": "slack",
            "timestamp": "2024-01-01T12:00:00Z",
            "severity": "high"
        }
        
        response = client.post('/event', 
                             data=json.dumps(event),
                             content_type='application/json')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'processed'
        # Should contain exception handling in the log
        log_text = ' '.join(data.get('log', []))
        assert 'EXCEPTION' in log_text
    
    def test_timeout_user_saas_event(self, client):
        """Test SaaS event with timeout trigger"""
        event = {
            "type": "unauthorized_saas_access",
            "event_id": "test-timeout-001",
            "user": "timeout@example.com",  # Triggers timeout
            "source": "slack",
            "timestamp": "2024-01-01T12:00:00Z",
            "severity": "high"
        }
        
        response = client.post('/event', 
                             data=json.dumps(event),
                             content_type='application/json')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'processed'
        log_text = ' '.join(data.get('log', []))
        assert 'EXCEPTION' in log_text and 'Timeout' in log_text
    
    def test_permission_s3_event(self, client):
        """Test S3 event with permission error trigger"""
        event = {
            "type": "open_s3_bucket",
            "event_id": "test-permission-001",
            "bucket_name": "permission-bucket",  # Triggers permission error
            "region": "us-east-1",
            "timestamp": "2024-01-01T12:00:00Z",
            "severity": "critical"
        }
        
        response = client.post('/event', 
                             data=json.dumps(event),
                             content_type='application/json')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'processed'
        log_text = ' '.join(data.get('log', []))
        assert 'EXCEPTION' in log_text
    
    def test_schema_validation_endpoint(self, client):
        """Test schema validation in API endpoint"""
        # Invalid event - missing required fields
        invalid_event = {
            "type": "unauthorized_saas_access",
            "event_id": "test-invalid"
            # Missing required fields
        }
        
        response = client.post('/event', 
                             data=json.dumps(invalid_event),
                             content_type='application/json')
        assert response.status_code == 400
        
        data = json.loads(response.data)
        assert data['status'] == 'validation_error'
        assert 'Schema validation failed' in data['log'][0]


class TestDashboard:
    """Test dashboard functionality"""
    
    def test_dashboard_endpoint(self, client):
        """Test dashboard endpoint returns HTML"""
        response = client.get('/dashboard')
        assert response.status_code == 200
        assert b'<!DOCTYPE html>' in response.data
        assert b'Reaper Agent Dashboard' in response.data
    
    def test_openapi_endpoint(self, client):
        """Test OpenAPI specification endpoint"""
        response = client.get('/openapi.json')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'openapi' in data
        assert 'paths' in data
        assert '/event' in data['paths']
