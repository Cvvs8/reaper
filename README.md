# Reaper Agent - Containerized Security Automation

A containerized Flask-based security automation agent that processes security events and applies remediation actions with comprehensive audit trails, mock SDK integration, and dry run capabilities.

## 🚀 Features

- **Dry Run Mode**: Test remediation actions without executing them
- **Audit Trail**: Comprehensive logging in Markdown or JSON format
- **Mock SDK Integration**: Safe testing with simulated API calls
- **Containerized**: Docker and Docker Compose ready
- **Health Monitoring**: Built-in health checks and status endpoints
- **Modular Design**: Easy to extend with new remediation modules

## Quick Start

### Using Docker Compose (Recommended)

1. Build and run the container:
   ```bash
   docker-compose up -d
   ```

2. Test the health endpoint:
   ```bash
   curl http://localhost:5001/
   ```

3. Send a test event:
   ```bash
   curl -X POST http://localhost:5001/event \
     -H "Content-Type: application/json" \
     -d '{
       "type": "unauthorized_saas_access",
       "event_id": "test-001",
       "user": "john.doe@company.com",
       "source": "slack"
     }'
   ```

### Using Docker directly

1. Build the image:
   ```bash
   docker build -t reaper-agent .
   ```

2. Run the container:
   ```bash
   docker run -d \
     --name reaper-agent \
     -p 5001:5001 \
     -v $(pwd)/logs:/app/logs \
     -v $(pwd)/config.yaml:/app/config.yaml:ro \
     reaper-agent
   ```

## 🔧 API Endpoints

### Core Endpoints

- `GET /` - Health check and status
- `POST /event` - Process security events
- `GET /config` - Get current configuration
- `POST /toggle-dry-run` - Toggle between dry run and live mode
- `GET /audit` - Get audit trail information

### Example API Calls

#### Check Status
```bash
curl http://localhost:5001/
```

#### Toggle Dry Run Mode
```bash
curl -X POST http://localhost:5001/toggle-dry-run
```

#### Process S3 Security Event
```bash
curl -X POST http://localhost:5001/event \
  -H "Content-Type: application/json" \
  -d '{
    "type": "open_s3_bucket",
    "event_id": "s3-incident-001",
    "bucket_name": "my-exposed-bucket",
    "region": "us-east-1",
    "severity": "critical"
  }'
```

## 🛠️ Configuration

The agent uses `config.yaml` to define modules and settings:

```yaml
# Reaper Agent Configuration
settings:
  dry_run_mode: false  # Set to true to simulate actions
  audit_format: "markdown"  # Options: "markdown", "json"
  audit_file: "logs/audit_trail.md"

modules:
  unauthorized_saas_access:
    class: SaaSAccessReaper
    description: "Handles unauthorized access events for SaaS platforms."

  open_s3_bucket:
    class: S3VisibilityReaper
    description: "Handles publicly exposed S3 buckets."
```

## 📊 Audit Trail

The agent maintains detailed audit trails in two formats:

### Markdown Format (Default)
- Human-readable reports with timestamps
- Detailed event information and processing logs
- API response details
- Mode indicators (LIVE vs DRY RUN)

### JSON Format
- Machine-readable structured data
- Easy integration with log analysis tools
- Programmatic access to audit data

Example audit entry location: `logs/audit_trail.md` or `logs/audit_trail.json`

## 🧪 Testing

### Unit Tests with Pytest

```bash
# Run all tests locally
pytest

# Or use the test runner script
python run_tests.py

# Run with coverage (requires pytest-cov)
pip install pytest-cov
pytest --cov=app

# Run specific test file
pytest tests/test_api.py

# Run with verbose output
pytest -v
```

### Testing in Docker

```bash
# Build and start the container
docker-compose up -d

# Run tests in the container (multiple ways)
docker-compose exec reaper-agent pytest                    # Direct pytest
docker-compose exec reaper-agent pytest tests/ -v         # Verbose with explicit path
docker-compose exec reaper-agent python run_tests.py      # Python test runner
docker-compose exec reaper-agent ./run_docker_tests.sh    # Bash script runner

# Stop the container
docker-compose down
```

**Note**: The `pytest.ini` configuration ensures tests are discovered correctly in the Docker environment.

### Integration Testing

Use the included integration test script to verify end-to-end functionality:

```bash
# Start the agent first
python main.py

# In another terminal, run the integration tests
python test_reaper.py
```

**What the integration tests cover:**
- ✅ Health check and status endpoints
- ✅ Configuration retrieval  
- ✅ Security event processing (SaaS access, S3 buckets)
- ✅ Dry run mode functionality
- ✅ Audit trail generation
- ✅ Error handling and validation
- ✅ API response format validation

This complements the unit tests and provides real-world usage examples.

## 🚀 Development

### Running Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py

# Or run as module
python -m app.main
```

### Adding New Modules

1. Create a new class in `app/modules/` inheriting from `BaseReaperModule`
2. Implement `validate()`, `execute()`, and `report()` methods
3. Add the module to `app/modules/__init__.py`
4. Add the module mapping to `app/agent.py`
5. Update `config.yaml` with the new event type
6. Create corresponding tests

## 🔒 Security Features

- **Non-root container execution**
- **Mock SDK integration** for safe testing
- **Comprehensive logging** for compliance
- **Input validation** on all events
- **Dry run mode** to prevent accidental actions

## 📁 Project Structure

```
reaper/
├── app/
│   ├── __init__.py
│   ├── main.py             # Flask app and API endpoints
│   ├── agent.py            # ReaperAgent class
│   ├── modules/
│   │   ├── __init__.py
│   │   ├── base.py         # BaseReaperModule class
│   │   ├── saas_access.py  # SaaS access remediation
│   │   └── s3_visibility.py # S3 bucket remediation
│   ├── sdks/
│   │   ├── __init__.py
│   │   ├── base.py         # Base SDK class
│   │   ├── slack.py        # Mock Slack API
│   │   └── aws.py          # Mock AWS API
│   └── utils/
│       ├── __init__.py
│       └── audit.py        # AuditTrailManager
├── tests/
│   ├── __init__.py
│   ├── conftest.py         # Pytest configuration
│   └── test_api.py         # API tests
├── logs/                   # Generated logs directory
├── config.yaml            # Configuration file
├── main.py                # Main entry point
├── test_reaper.py         # Manual test script
├── requirements.txt       # Python dependencies
├── pytest.ini            # Pytest configuration
├── Dockerfile            # Container definition
├── docker-compose.yml    # Orchestration
└── README.md            # This file
```

## 🐳 Container Management

### View Logs
```bash
docker-compose logs -f reaper-agent
```

### Restart Service
```bash
docker-compose restart reaper-agent
```

### Stop Service
```bash
docker-compose down
```

### Rebuild After Changes
```bash
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

## 🔄 Development

### Adding New Modules

1. Create a new class inheriting from `BaseReaperModule`
2. Implement `validate()`, `execute()`, and `report()` methods
3. Add module to `config.yaml`
4. Add mock SDK calls as needed

### Environment Variables

- `FLASK_ENV`: Set to `production` by default
- `PYTHONUNBUFFERED`: Ensures real-time log output

## 📈 Monitoring

The container includes health checks that verify:
- Service responsiveness
- Configuration validity
- Module initialization

Check container health:
```bash
docker-compose ps
```
