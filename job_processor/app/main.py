"""
OptiFlight Coordinator - Main FastAPI Application

A professional-grade, multi-tenant job processing system for flight optimization.
Designed for high-availability, scalability, and resilience in Kubernetes environments.
"""

import asyncio
from contextlib import asynccontextmanager
from typing import Dict, List, Optional
import time
import uuid
from datetime import datetime, timedelta

from fastapi import FastAPI, HTTPException, status, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from prometheus_client import Counter, Histogram, Gauge, generate_latest
from fastapi.responses import PlainTextResponse
import structlog

# Note: In a real implementation, these would be proper imports
# For the demo, we'll use simplified versions
try:
    from .config import settings
    from .models import (
        TenantConfig,
        PositionReportEvent,
        FlightPlanEvent,
        JobRequest,
        JobResult,
        JobStatus,
        EventType,
        HealthCheck,
        MetricsResponse,
    )
    from .kubernetes_orchestrator import KubernetesOrchestrator
except ImportError:
    # Fallback for demo - simplified versions
    class Settings:
        app_name = "OptiFlight Coordinator"
        app_version = "1.0.0"
        debug = False
        api_host = "0.0.0.0"
        api_port = 8000
        metrics_enabled = True
        rate_limit_per_minute = 1000
        max_concurrent_jobs_per_tenant = 10

    settings = Settings()

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# Metrics
REQUEST_COUNT = Counter(
    "http_requests_total", "Total HTTP requests", ["method", "endpoint", "status"]
)
REQUEST_DURATION = Histogram("http_request_duration_seconds", "HTTP request duration")
ACTIVE_JOBS = Gauge("active_jobs_total", "Number of active optimization jobs")
JOB_DURATION = Histogram(
    "job_duration_seconds", "Job execution duration", ["airline", "status"]
)
TENANT_JOBS = Counter("tenant_jobs_total", "Jobs per tenant", ["airline", "status"])

# In-memory storage (in production, use Redis/PostgreSQL)
TENANT_CONFIGS: Dict[str, dict] = {}
ACTIVE_JOBS_STORE: Dict[str, dict] = {}
JOB_RESULTS_STORE: Dict[str, dict] = {}

# Rate limiting storage
RATE_LIMIT_STORE: Dict[str, List[float]] = {}

# Kubernetes orchestrator
k8s_orchestrator = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management."""
    # Startup
    logger.info("Starting OptiFlight Coordinator")

    global k8s_orchestrator
    try:
        # Initialize Kubernetes orchestrator
        k8s_orchestrator = "KubernetesOrchestrator()"  # Simplified for demo
        logger.info("Kubernetes orchestrator initialized")
    except Exception as e:
        logger.error("Failed to initialize Kubernetes orchestrator", error=str(e))
        # In production, this might be a critical failure

    # Load initial tenant configurations (from database in production)
    await load_initial_configs()

    yield

    # Shutdown
    logger.info("Shutting down OptiFlight Coordinator")


async def load_initial_configs():
    """Load initial tenant configurations."""
    # Sample configurations for demo
    sample_configs = [
        {
            "airline": "ABC",
            "max_parallel_executions": 10,
            "active_modules": [
                {
                    "name": "route_optimizer",
                    "image": "sita/route-optimizer",
                    "version": "v1.2.0",
                    "enabled": True,
                    "cpu_request": "200m",
                    "cpu_limit": "1000m",
                    "memory_request": "256Mi",
                    "memory_limit": "1Gi",
                    "timeout_seconds": 300,
                    "env_vars": {"LOG_LEVEL": "INFO"},
                }
            ],
            "rate_limit_per_minute": 1000,
            "namespace": "airline-abc",
            "priority": 1,
            "resource_quota": {
                "requests.cpu": "4",
                "requests.memory": "8Gi",
                "limits.cpu": "16",
                "limits.memory": "32Gi",
            },
        }
    ]

    for config in sample_configs:
        TENANT_CONFIGS[config["airline"]] = config
        logger.info("Loaded configuration for tenant", airline=config["airline"])


# Initialize FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Multi-tenant flight optimization job processor",
    lifespan=lifespan,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(GZipMiddleware, minimum_size=1000)


# Rate limiting helper
def check_rate_limit(airline: str, limit_per_minute: int = None) -> bool:
    """Check if airline is within rate limits."""
    if limit_per_minute is None:
        limit_per_minute = settings.rate_limit_per_minute

    now = time.time()
    minute_ago = now - 60

    if airline not in RATE_LIMIT_STORE:
        RATE_LIMIT_STORE[airline] = []

    # Clean old entries
    RATE_LIMIT_STORE[airline] = [
        ts for ts in RATE_LIMIT_STORE[airline] if ts > minute_ago
    ]

    # Check limit
    if len(RATE_LIMIT_STORE[airline]) >= limit_per_minute:
        return False

    # Add current request
    RATE_LIMIT_STORE[airline].append(now)
    return True


# Dependency for getting tenant config
async def get_tenant_config(airline: str) -> dict:
    """Get tenant configuration with validation."""
    if airline not in TENANT_CONFIGS:
        logger.warning("Tenant configuration not found", airline=airline)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Configuration for airline '{airline}' not found",
        )

    config = TENANT_CONFIGS[airline]

    # Check rate limiting
    rate_limit = config.get("rate_limit_per_minute", settings.rate_limit_per_minute)
    if not check_rate_limit(airline, rate_limit):
        logger.warning("Rate limit exceeded", airline=airline)
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded for airline '{airline}'",
        )

    return config


# Health Check Endpoints
@app.get("/health", response_model=dict)
async def health_check():
    """Basic health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": settings.app_version,
    }


@app.get("/health/detailed", response_model=dict)
async def detailed_health_check():
    """Detailed health check with dependencies."""
    dependencies = {
        "kubernetes": "connected" if k8s_orchestrator else "disconnected",
        "config_store": "connected",
        "metrics": "enabled" if settings.metrics_enabled else "disabled",
    }

    overall_status = (
        "healthy"
        if all(
            status == "connected" or status == "enabled"
            for status in dependencies.values()
        )
        else "degraded"
    )

    return {
        "status": overall_status,
        "timestamp": datetime.utcnow().isoformat(),
        "version": settings.app_version,
        "dependencies": dependencies,
    }


# Metrics endpoint
@app.get("/metrics", response_class=PlainTextResponse)
async def metrics():
    """Prometheus metrics endpoint."""
    if not settings.metrics_enabled:
        raise HTTPException(status_code=404, detail="Metrics disabled")

    # Update active jobs metric
    ACTIVE_JOBS.set(len(ACTIVE_JOBS_STORE))

    return generate_latest()


@app.get("/metrics/summary", response_model=dict)
async def metrics_summary():
    """Human-readable metrics summary."""
    now = datetime.utcnow()
    yesterday = now - timedelta(days=1)

    completed_24h = len(
        [
            job
            for job in JOB_RESULTS_STORE.values()
            if job.get("completed_at")
            and datetime.fromisoformat(job["completed_at"]) > yesterday
            and job.get("status") == "completed"
        ]
    )

    failed_24h = len(
        [
            job
            for job in JOB_RESULTS_STORE.values()
            if job.get("completed_at")
            and datetime.fromisoformat(job["completed_at"]) > yesterday
            and job.get("status") == "failed"
        ]
    )

    # Calculate average job duration
    completed_jobs = [
        job
        for job in JOB_RESULTS_STORE.values()
        if job.get("duration_seconds") and job.get("status") == "completed"
    ]

    avg_duration = (
        sum(job["duration_seconds"] for job in completed_jobs) / len(completed_jobs)
        if completed_jobs
        else 0
    )

    return {
        "active_jobs": len(ACTIVE_JOBS_STORE),
        "completed_jobs_24h": completed_24h,
        "failed_jobs_24h": failed_24h,
        "average_job_duration": round(avg_duration, 2),
        "tenants_count": len(TENANT_CONFIGS),
        "cpu_usage_percent": 45.2,  # Mock data - would come from K8s metrics
        "memory_usage_percent": 67.8,  # Mock data - would come from K8s metrics
    }


# Configuration Management Endpoints
@app.post("/api/v1/config/tenants", status_code=status.HTTP_201_CREATED)
async def create_tenant_config(config: dict):
    """Create or update tenant configuration."""
    airline = config.get("airline")
    if not airline:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Airline field is required"
        )

    # Validate configuration structure
    required_fields = ["airline", "max_parallel_executions", "active_modules"]
    for field in required_fields:
        if field not in config:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Required field '{field}' is missing",
            )

    TENANT_CONFIGS[airline] = config

    logger.info("Tenant configuration created/updated", airline=airline)

    return {
        "message": f"Configuration for airline '{airline}' created/updated successfully",
        "config": config,
    }


@app.get("/api/v1/config/tenants/{airline}")
async def get_tenant_config_endpoint(airline: str):
    """Get tenant configuration."""
    config = await get_tenant_config(airline)
    return config


@app.get("/api/v1/config/tenants")
async def list_tenant_configs():
    """List all tenant configurations."""
    return {
        "tenants": list(TENANT_CONFIGS.keys()),
        "total": len(TENANT_CONFIGS),
        "configurations": TENANT_CONFIGS,
    }


@app.delete("/api/v1/config/tenants/{airline}")
async def delete_tenant_config(airline: str):
    """Delete tenant configuration."""
    if airline not in TENANT_CONFIGS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Configuration for airline '{airline}' not found",
        )

    del TENANT_CONFIGS[airline]
    logger.info("Tenant configuration deleted", airline=airline)

    return {"message": f"Configuration for airline '{airline}' deleted successfully"}


# Event Processing Endpoints
@app.post("/api/v1/events/position-report")
async def process_position_report(event: dict, background_tasks: BackgroundTasks):
    """Process position report event."""
    start_time = time.time()

    try:
        # Validate required fields
        required_fields = [
            "flight_id",
            "airline",
            "aircraft_type",
            "registration",
            "latitude",
            "longitude",
        ]
        for field in required_fields:
            if field not in event:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Required field '{field}' is missing",
                )

        airline = event["airline"]
        config = await get_tenant_config(airline)

        # Create job requests for active modules
        job_results = []
        for module in config.get("active_modules", []):
            if not module.get("enabled", True):
                continue

            job_id = str(uuid.uuid4())
            job_request = {
                "job_id": job_id,
                "event_type": "position_report",
                "event_data": event,
                "airline": airline,
                "module_name": module["name"],
                "priority": config.get("priority", 1),
                "timeout_seconds": module.get("timeout_seconds", 300),
            }

            # Add to background processing
            background_tasks.add_task(
                execute_optimization_job, job_request, module, config
            )

            job_results.append(
                {"job_id": job_id, "module": module["name"], "status": "submitted"}
            )

            # Store job info
            ACTIVE_JOBS_STORE[job_id] = {
                "job_id": job_id,
                "airline": airline,
                "module": module["name"],
                "status": "pending",
                "submitted_at": datetime.utcnow().isoformat(),
                "event_type": "position_report",
            }

        duration = time.time() - start_time
        REQUEST_DURATION.observe(duration)
        REQUEST_COUNT.labels(
            method="POST", endpoint="/events/position-report", status="200"
        ).inc()

        logger.info(
            "Position report processed",
            flight_id=event["flight_id"],
            airline=airline,
            jobs_submitted=len(job_results),
        )

        return {
            "message": "Position report processed successfully",
            "flight_id": event["flight_id"],
            "jobs_submitted": len(job_results),
            "jobs": job_results,
        }

    except HTTPException:
        REQUEST_COUNT.labels(
            method="POST", endpoint="/events/position-report", status="4xx"
        ).inc()
        raise
    except Exception as e:
        REQUEST_COUNT.labels(
            method="POST", endpoint="/events/position-report", status="500"
        ).inc()
        logger.error("Error processing position report", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error processing position report",
        )


@app.post("/api/v1/events/flight-plan")
async def process_flight_plan(event: dict, background_tasks: BackgroundTasks):
    """Process flight plan event."""
    start_time = time.time()

    try:
        # Validate required fields
        required_fields = [
            "flight_id",
            "airline",
            "aircraft_type",
            "registration",
            "route",
        ]
        for field in required_fields:
            if field not in event:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Required field '{field}' is missing",
                )

        airline = event["airline"]
        config = await get_tenant_config(airline)

        # Create job requests for active modules
        job_results = []
        for module in config.get("active_modules", []):
            if not module.get("enabled", True):
                continue

            job_id = str(uuid.uuid4())
            job_request = {
                "job_id": job_id,
                "event_type": "flight_plan",
                "event_data": event,
                "airline": airline,
                "module_name": module["name"],
                "priority": config.get("priority", 1),
                "timeout_seconds": module.get("timeout_seconds", 300),
            }

            # Add to background processing
            background_tasks.add_task(
                execute_optimization_job, job_request, module, config
            )

            job_results.append(
                {"job_id": job_id, "module": module["name"], "status": "submitted"}
            )

            # Store job info
            ACTIVE_JOBS_STORE[job_id] = {
                "job_id": job_id,
                "airline": airline,
                "module": module["name"],
                "status": "pending",
                "submitted_at": datetime.utcnow().isoformat(),
                "event_type": "flight_plan",
            }

        duration = time.time() - start_time
        REQUEST_DURATION.observe(duration)
        REQUEST_COUNT.labels(
            method="POST", endpoint="/events/flight-plan", status="200"
        ).inc()

        logger.info(
            "Flight plan processed",
            flight_id=event["flight_id"],
            airline=airline,
            jobs_submitted=len(job_results),
        )

        return {
            "message": "Flight plan processed successfully",
            "flight_id": event["flight_id"],
            "jobs_submitted": len(job_results),
            "jobs": job_results,
        }

    except HTTPException:
        REQUEST_COUNT.labels(
            method="POST", endpoint="/events/flight-plan", status="4xx"
        ).inc()
        raise
    except Exception as e:
        REQUEST_COUNT.labels(
            method="POST", endpoint="/events/flight-plan", status="500"
        ).inc()
        logger.error("Error processing flight plan", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error processing flight plan",
        )


# Job Management Endpoints
@app.get("/api/v1/jobs/{job_id}")
async def get_job_status(job_id: str):
    """Get status of a specific job."""
    # Check active jobs first
    if job_id in ACTIVE_JOBS_STORE:
        return ACTIVE_JOBS_STORE[job_id]

    # Check completed jobs
    if job_id in JOB_RESULTS_STORE:
        return JOB_RESULTS_STORE[job_id]

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail=f"Job '{job_id}' not found"
    )


@app.get("/api/v1/jobs")
async def list_jobs(
    airline: Optional[str] = None, status_filter: Optional[str] = None, limit: int = 100
):
    """List jobs with optional filtering."""
    all_jobs = {**ACTIVE_JOBS_STORE, **JOB_RESULTS_STORE}

    # Filter by airline
    if airline:
        all_jobs = {
            job_id: job
            for job_id, job in all_jobs.items()
            if job.get("airline") == airline
        }

    # Filter by status
    if status_filter:
        all_jobs = {
            job_id: job
            for job_id, job in all_jobs.items()
            if job.get("status") == status_filter
        }

    # Limit results
    jobs_list = list(all_jobs.values())[:limit]

    return {
        "jobs": jobs_list,
        "total": len(jobs_list),
        "filtered": bool(airline or status_filter),
    }


@app.delete("/api/v1/jobs/{job_id}")
async def cancel_job(job_id: str):
    """Cancel a running job."""
    if job_id not in ACTIVE_JOBS_STORE:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Active job '{job_id}' not found",
        )

    job = ACTIVE_JOBS_STORE[job_id]

    # Simulate job cancellation (in production, would cancel K8s job)
    job["status"] = "cancelled"
    job["cancelled_at"] = datetime.utcnow().isoformat()

    # Move to results store
    JOB_RESULTS_STORE[job_id] = job
    del ACTIVE_JOBS_STORE[job_id]

    TENANT_JOBS.labels(airline=job["airline"], status="cancelled").inc()

    logger.info("Job cancelled", job_id=job_id, airline=job["airline"])

    return {"message": f"Job '{job_id}' cancelled successfully", "job": job}


# Background task for job execution
async def execute_optimization_job(
    job_request: dict, module_config: dict, tenant_config: dict
):
    """Execute optimization job in background."""
    job_id = job_request["job_id"]
    airline = job_request["airline"]

    start_time = time.time()

    try:
        # Update job status to running
        if job_id in ACTIVE_JOBS_STORE:
            ACTIVE_JOBS_STORE[job_id]["status"] = "running"
            ACTIVE_JOBS_STORE[job_id]["started_at"] = datetime.utcnow().isoformat()

        logger.info(
            "Starting optimization job", job_id=job_id, module=module_config["name"]
        )

        # Simulate job execution (in production, would submit to Kubernetes)
        execution_time = module_config.get("timeout_seconds", 300)
        await asyncio.sleep(min(execution_time, 5))  # Max 5 seconds for demo

        # Simulate successful completion
        result_data = {
            "optimization_result": "sample_result",
            "recommendations": ["recommendation_1", "recommendation_2"],
            "confidence_score": 0.95,
            "processing_time": time.time() - start_time,
        }

        duration = time.time() - start_time

        # Move job to completed
        completed_job = {
            "job_id": job_id,
            "airline": airline,
            "module": module_config["name"],
            "status": "completed",
            "submitted_at": ACTIVE_JOBS_STORE.get(job_id, {}).get("submitted_at"),
            "started_at": ACTIVE_JOBS_STORE.get(job_id, {}).get("started_at"),
            "completed_at": datetime.utcnow().isoformat(),
            "duration_seconds": duration,
            "result_data": result_data,
            "event_type": job_request["event_type"],
        }

        JOB_RESULTS_STORE[job_id] = completed_job
        if job_id in ACTIVE_JOBS_STORE:
            del ACTIVE_JOBS_STORE[job_id]

        # Update metrics
        JOB_DURATION.labels(airline=airline, status="completed").observe(duration)
        TENANT_JOBS.labels(airline=airline, status="completed").inc()

        logger.info(
            "Optimization job completed",
            job_id=job_id,
            airline=airline,
            module=module_config["name"],
            duration=duration,
        )

    except Exception as e:
        # Handle job failure
        duration = time.time() - start_time

        failed_job = {
            "job_id": job_id,
            "airline": airline,
            "module": module_config["name"],
            "status": "failed",
            "submitted_at": ACTIVE_JOBS_STORE.get(job_id, {}).get("submitted_at"),
            "started_at": ACTIVE_JOBS_STORE.get(job_id, {}).get("started_at"),
            "failed_at": datetime.utcnow().isoformat(),
            "duration_seconds": duration,
            "error_message": str(e),
            "event_type": job_request["event_type"],
        }

        JOB_RESULTS_STORE[job_id] = failed_job
        if job_id in ACTIVE_JOBS_STORE:
            del ACTIVE_JOBS_STORE[job_id]

        # Update metrics
        JOB_DURATION.labels(airline=airline, status="failed").observe(duration)
        TENANT_JOBS.labels(airline=airline, status="failed").inc()

        logger.error(
            "Optimization job failed",
            job_id=job_id,
            airline=airline,
            module=module_config["name"],
            error=str(e),
        )


# Admin endpoints
@app.get("/api/v1/admin/stats")
async def get_admin_stats():
    """Get administrative statistics."""
    return {
        "system": {
            "uptime": "running",  # Would calculate actual uptime
            "version": settings.app_version,
            "debug_mode": settings.debug,
        },
        "tenants": {
            "total": len(TENANT_CONFIGS),
            "airlines": list(TENANT_CONFIGS.keys()),
        },
        "jobs": {
            "active": len(ACTIVE_JOBS_STORE),
            "completed": len(JOB_RESULTS_STORE),
            "total_processed": len(JOB_RESULTS_STORE),
        },
        "performance": {
            "rate_limiting_active": len(RATE_LIMIT_STORE),
            "avg_response_time": "~50ms",  # Mock data
        },
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
        log_level="info",
    )
