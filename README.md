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

Use the included test script to verify functionality:

```bash
python test_reaper.py
```

This will:
- Test health endpoints
- Process events in both LIVE and DRY RUN modes
- Toggle between modes
- Verify audit trail generation

## 🔒 Security Features

- **Non-root container execution**
- **Mock SDK integration** for safe testing
- **Comprehensive logging** for compliance
- **Input validation** on all events
- **Dry run mode** to prevent accidental actions

## 📁 File Structure

```
reaper/
├── reaper.py              # Main application
├── config.yaml           # Configuration file
├── requirements.txt       # Python dependencies
├── Dockerfile            # Container definition
├── docker-compose.yml    # Orchestration
├── test_reaper.py        # Test suite
├── logs/
│   ├── audit_trail.md    # Audit trail (markdown)
│   └── reaper_actions.log # Application logs
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
