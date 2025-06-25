"""
API endpoint tests
"""
import json


class TestHealthEndpoints:
    """Test health and configuration endpoints"""
    
    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get('/')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
        assert data['service'] == 'reaper-agent'
        assert 'mode' in data
        assert 'modules' in data
    
    def test_config_endpoint(self, client):
        """Test configuration endpoint"""
        response = client.get('/config')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'dry_run_mode' in data
        assert 'audit_format' in data
        assert 'modules' in data
    
    def test_toggle_dry_run(self, client):
        """Test dry run toggle endpoint"""
        response = client.post('/toggle-dry-run')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'dry_run_mode' in data
        assert 'message' in data


class TestEventProcessing:
    """Test event processing endpoints"""
    
    def test_saas_access_event(self, client):
        """Test SaaS access event processing"""
        event = {
            "type": "unauthorized_saas_access",
            "event_id": "test-001",
            "user": "john.doe@company.com",
            "source": "slack"
        }
        
        response = client.post('/event', 
                             data=json.dumps(event),
                             content_type='application/json')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'processed'
        assert len(data['log']) > 0
    
    def test_s3_bucket_event(self, client):
        """Test S3 bucket event processing"""
        event = {
            "type": "open_s3_bucket",
            "event_id": "test-002",
            "bucket_name": "test-bucket",
            "region": "us-east-1"
        }
        
        response = client.post('/event',
                             data=json.dumps(event),
                             content_type='application/json')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'processed'
        assert len(data['log']) > 0
    
    def test_invalid_event_type(self, client):
        """Test handling of invalid event type"""
        event = {
            "type": "unknown_event",
            "event_id": "test-003"
        }
        
        response = client.post('/event',
                             data=json.dumps(event),
                             content_type='application/json')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'ignored'
    
    def test_missing_event_type(self, client):
        """Test handling of missing event type"""
        event = {
            "event_id": "test-004"
        }
        
        response = client.post('/event',
                             data=json.dumps(event),
                             content_type='application/json')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'error'
    
    def test_invalid_json(self, client):
        """Test handling of invalid JSON"""
        response = client.post('/event',
                             data="invalid json",
                             content_type='application/json')
        assert response.status_code == 400
    
    def test_missing_content_type(self, client):
        """Test handling of missing content type"""
        response = client.post('/event', data='{"test": "data"}')
        assert response.status_code == 400


class TestValidation:
    """Test event validation"""
    
    def test_saas_validation_success(self, client):
        """Test successful SaaS event validation"""
        event = {
            "type": "unauthorized_saas_access",
            "event_id": "test-005",
            "user": "jane.doe@company.com",
            "source": "slack"
        }
        
        response = client.post('/event',
                             data=json.dumps(event),
                             content_type='application/json')
        data = json.loads(response.data)
        
        assert any("[Validate] SUCCESS" in log for log in data['log'])
    
    def test_saas_validation_failure(self, client):
        """Test failed SaaS event validation"""
        event = {
            "type": "unauthorized_saas_access",
            "event_id": "test-006",
            "user": "jane.doe@company.com"
            # Missing 'source' field
        }
        
        response = client.post('/event',
                             data=json.dumps(event),
                             content_type='application/json')
        data = json.loads(response.data)
        
        assert data['status'] == 'validation_failed'
        assert any("[Validate] FAILED" in log for log in data['log'])
    
    def test_s3_validation_failure(self, client):
        """Test failed S3 event validation"""
        event = {
            "type": "open_s3_bucket",
            "event_id": "test-007",
            "bucket_name": "test-bucket"
            # Missing 'region' field
        }
        
        response = client.post('/event',
                             data=json.dumps(event),
                             content_type='application/json')
        data = json.loads(response.data)
        
        assert data['status'] == 'validation_failed'
        assert any("[Validate] FAILED" in log for log in data['log'])
