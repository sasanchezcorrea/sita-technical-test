# OptiFlight Coordinator Job Processor 

## Application Code (`app/`)

- **`main.py`** - Main FastAPI application with all endpoints and business logic
- **`config.py`** - Configuration management and settings
- **`models.py`** - Pydantic data models for requests/responses
- **`kubernetes_orchestrator.py`** - Kubernetes job orchestration and management
- **`gunicorn_config.py`** - Production WSGI server configuration

## Container Configuration

- **`Dockerfile`** - Multi-stage production container build
- **`requirements.txt`** - Python dependencies and versions

## Testing

- **`tests/test_config.py`** - Comprehensive unit and integration tests


## Prerequisites Validation

```bash
# Verify Docker installation
docker --version
python3 --version
pwd && ls -la
```

## Cross-checking

Commands to verify prerequisites and file structure:

```bash
### Container Build and Testing

```bash
# Build Docker image
docker build -t optiflight-coordinator:latest .

# Clean up existing containers
docker stop optiflight-coordinator || true
docker rm optiflight-coordinator || true

# Run container with proper configuration
docker run -d --name optiflight-coordinator \
  -p 8000:8000 \
  -e LOG_LEVEL=info \
  optiflight-coordinator:latest

# Verify container is running
docker ps | grep optiflight-coordinator
```

### Health Check Validation

```bash
# Basic health check
curl http://localhost:8000/health

# Detailed health check with dependencies
curl http://localhost:8000/health/detailed

# Metrics summary endpoint
curl http://localhost:8000/metrics/summary
```

### API Functionality Testing

```bash
# Create tenant configuration
curl -X POST http://localhost:8000/api/v1/config/tenants \
  -H "Content-Type: application/json" \
  -d '{
    "airline": "ABC",
    "max_parallel_executions": 10,
    "active_modules": [
      {
        "name": "route_optimizer",
        "image": "sita/route-optimizer",
        "version": "v1.2.0",
        "enabled": true,
        "cpu_request": "200m",
        "cpu_limit": "1000m",
        "memory_request": "256Mi",
        "memory_limit": "1Gi",
        "timeout_seconds": 300,
        "env_vars": {"LOG_LEVEL": "INFO"}
      }
    ],
    "rate_limit_per_minute": 1000,
    "namespace": "airline-abc",
    "priority": 1
  }'

# Process position report event
curl -X POST http://localhost:8000/api/v1/events/position-report \
  -H "Content-Type: application/json" \
  -d '{
    "flight_id": "ABC123",
    "airline": "ABC",
    "aircraft_type": "A320",
    "registration": "N123AB",
    "latitude": 37.7749,
    "longitude": -122.4194,
    "altitude": 35000,
    "speed": 450,
    "heading": 90,
    "timestamp": "2025-09-08T10:30:00Z"
  }'

# Process flight plan event
curl -X POST http://localhost:8000/api/v1/events/flight-plan \
  -H "Content-Type: application/json" \
  -d '{
    "flight_id": "ABC456",
    "airline": "ABC",
    "aircraft_type": "B737",
    "registration": "N456CD",
    "route": ["KJFK", "KORD", "KLAX"],
    "departure_time": "2025-09-09T14:00:00Z",
    "arrival_time": "2025-09-09T18:00:00Z"
  }'
```

### Job Management Testing

```bash
# List all jobs
curl http://localhost:8000/api/v1/jobs

# Filter jobs by airline
curl "http://localhost:8000/api/v1/jobs?airline=ABC"

# Get specific job status (use job_id from previous responses)
curl http://localhost:8000/api/v1/jobs/{job_id}

# Get administrative statistics
curl http://localhost:8000/api/v1/admin/stats
```

### Local Development Testing

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install essential dependencies
pip install fastapi uvicorn prometheus-client structlog httpx

# Run with uvicorn (alternative approach)
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

### Container Management

```bash
# View container logs
docker logs optiflight-coordinator

# Stop and clean up
docker stop optiflight-coordinator
docker rm optiflight-coordinator
```
