"""Data models for OptiFlight Coordinator."""

from pydantic import BaseModel, Field, ConfigDict
from typing import List, Dict, Optional, Any
from datetime import datetime, timezone
from enum import Enum
import uuid


def utc_now() -> datetime:
    """Get current UTC datetime with timezone info."""
    return datetime.now(timezone.utc)


class EventType(str, Enum):
    """Event types supported by the system."""

    POSITION_REPORT = "position_report"
    FLIGHT_PLAN = "flight_plan"


class JobStatus(str, Enum):
    """Job execution status."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Coordinate(BaseModel):
    """Geographic coordinate."""

    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)


class PositionReportEvent(BaseModel):
    """Position report event model."""

    model_config = ConfigDict(str_strip_whitespace=True)

    flight_id: str
    airline: str
    aircraft_type: str
    registration: str
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    timestamp: Optional[datetime] = Field(default_factory=utc_now)
    altitude: Optional[float] = None
    speed: Optional[float] = None
    heading: Optional[float] = None


class FlightPlanEvent(BaseModel):
    """Flight plan event model."""

    model_config = ConfigDict(str_strip_whitespace=True)

    flight_id: str
    airline: str
    aircraft_type: str
    registration: str
    route: List[Coordinate]
    timestamp: Optional[datetime] = Field(default_factory=utc_now)
    departure_airport: Optional[str] = None
    arrival_airport: Optional[str] = None
    estimated_duration: Optional[int] = None  # minutes


class ModuleConfig(BaseModel):
    """Configuration for optimization modules."""

    name: str
    image: str
    version: str = "latest"
    enabled: bool = True
    cpu_request: str = "100m"
    cpu_limit: str = "500m"
    memory_request: str = "128Mi"
    memory_limit: str = "512Mi"
    timeout_seconds: int = 300
    env_vars: Dict[str, str] = Field(default_factory=dict)


class TenantConfig(BaseModel):
    """Multi-tenant configuration."""

    model_config = ConfigDict(str_strip_whitespace=True)

    airline: str = Field(..., min_length=1, max_length=10)
    max_parallel_executions: int = Field(default=10, ge=1, le=100)
    active_modules: List[ModuleConfig] = Field(default_factory=list)
    rate_limit_per_minute: int = Field(default=1000, ge=1)
    namespace: Optional[str] = Field(default=None)
    priority: int = Field(default=1, ge=1, le=10)
    resource_quota: Dict[str, str] = Field(default_factory=dict)

    def get_namespace(self) -> str:
        """Get the namespace, generating if not set."""
        if self.namespace:
            return self.namespace
        airline_value = str(self.airline)
        return f"airline-{airline_value.lower()}"


class JobRequest(BaseModel):
    """Job execution request."""

    job_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_type: EventType
    event_data: Dict[str, Any]
    airline: str
    module_name: str
    priority: int = Field(default=1, ge=1, le=10)
    timeout_seconds: Optional[int] = None


class JobResult(BaseModel):
    """Job execution result."""

    job_id: str
    status: JobStatus
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    result_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    pod_name: Optional[str] = None
    namespace: str


class HealthCheck(BaseModel):
    """Health check response."""

    status: str
    timestamp: datetime = Field(default_factory=utc_now)
    version: str
    dependencies: Dict[str, str] = Field(default_factory=dict)


class MetricsResponse(BaseModel):
    """Metrics response model."""

    active_jobs: int
    completed_jobs_24h: int
    failed_jobs_24h: int
    average_job_duration: float
    tenants_count: int
    cpu_usage_percent: float
    memory_usage_percent: float
