"""Unit tests for Pydantic models."""

import pytest
from datetime import datetime, timezone
from app.models import (
    TenantConfig,
    ModuleConfig,
    JobRequest,
    JobStatus,
    JobResult,
    EventType,
    PositionReportEvent,
    FlightPlanEvent,
    Coordinate,
    HealthCheck,
    MetricsResponse,
)


class TestModuleConfig:
    """Test ModuleConfig model."""

    def test_module_config_creation(self) -> None:
        """Test creating a valid ModuleConfig."""
        config = ModuleConfig(
            name="route_optimizer",
            image="sita/route-optimizer",
            version="v1.0.0",
            enabled=True,
            timeout_seconds=300,
        )
        
        assert config.name == "route_optimizer"
        assert config.image == "sita/route-optimizer"
        assert config.version == "v1.0.0"
        assert config.enabled is True
        assert config.timeout_seconds == 300

    def test_module_config_defaults(self) -> None:
        """Test ModuleConfig with default values."""
        config = ModuleConfig(
            name="fuel_optimizer",
            image="sita/fuel-optimizer",
        )
        
        assert config.name == "fuel_optimizer"
        assert config.image == "sita/fuel-optimizer"
        assert config.version == "latest"
        assert config.enabled is True
        assert config.timeout_seconds == 300


class TestTenantConfig:
    """Test TenantConfig model."""

    def test_tenant_config_creation(self) -> None:
        """Test creating a valid TenantConfig."""
        modules = [
            ModuleConfig(name="route_optimizer", image="sita/route-optimizer"),
            ModuleConfig(name="fuel_optimizer", image="sita/fuel-optimizer"),
        ]
        
        config = TenantConfig(
            airline="ABC",
            max_parallel_executions=10,
            active_modules=modules,
            rate_limit_per_minute=1000,
        )
        
        assert config.airline == "ABC"
        assert config.max_parallel_executions == 10
        assert len(config.active_modules) == 2
        assert config.rate_limit_per_minute == 1000

    def test_get_namespace(self) -> None:
        """Test namespace generation."""
        config = TenantConfig(
            airline="TEST_AIRLINE",
            max_parallel_executions=5,
        )
        
        namespace = config.get_namespace()
        assert namespace == "tenant-test-airline"

    def test_get_namespace_special_chars(self) -> None:
        """Test namespace generation with special characters."""
        config = TenantConfig(
            airline="SPECIAL-CHARS_123",
            max_parallel_executions=5,
        )
        
        namespace = config.get_namespace()
        assert namespace == "tenant-special-chars-123"

    def test_tenant_config_defaults(self) -> None:
        """Test TenantConfig with default values."""
        config = TenantConfig(airline="XYZ")
        
        assert config.airline == "XYZ"
        assert config.max_parallel_executions == 5
        assert config.active_modules == []
        assert config.rate_limit_per_minute == 100


"""Unit tests for Pydantic models."""

import pytest
from datetime import datetime, timezone
from app.models import (
    TenantConfig,
    ModuleConfig,
    JobRequest,
    JobStatus,
    JobResult,
    EventType,
    PositionReportEvent,
    FlightPlanEvent,
    Coordinate,
    HealthCheck,
    MetricsResponse,
)


class TestModuleConfig:
    """Test ModuleConfig model."""

    def test_module_config_creation(self) -> None:
        """Test creating a valid ModuleConfig."""
        config = ModuleConfig(
            name="route_optimizer",
            image="sita/route-optimizer",
            version="v1.0.0",
            enabled=True,
            timeout_seconds=300,
        )
        
        assert config.name == "route_optimizer"
        assert config.image == "sita/route-optimizer"
        assert config.version == "v1.0.0"
        assert config.enabled is True
        assert config.timeout_seconds == 300

    def test_module_config_defaults(self) -> None:
        """Test ModuleConfig with default values."""
        config = ModuleConfig(
            name="fuel_optimizer",
            image="sita/fuel-optimizer",
        )
        
        assert config.name == "fuel_optimizer"
        assert config.image == "sita/fuel-optimizer"
        assert config.version == "latest"
        assert config.enabled is True
        assert config.timeout_seconds == 300
        assert config.cpu_request == "100m"
        assert config.memory_request == "128Mi"


class TestTenantConfig:
    """Test TenantConfig model."""

    def test_tenant_config_creation(self) -> None:
        """Test creating a valid TenantConfig."""
        modules = [
            ModuleConfig(name="route_optimizer", image="sita/route-optimizer"),
            ModuleConfig(name="fuel_optimizer", image="sita/fuel-optimizer"),
        ]
        
        config = TenantConfig(
            airline="ABC",
            max_parallel_executions=10,
            active_modules=modules,
            rate_limit_per_minute=1000,
        )
        
        assert config.airline == "ABC"
        assert config.max_parallel_executions == 10
        assert len(config.active_modules) == 2
        assert config.rate_limit_per_minute == 1000

    def test_get_namespace(self) -> None:
        """Test namespace generation."""
        config = TenantConfig(
            airline="TEST_AIRLINE",
            max_parallel_executions=5,
        )
        
        namespace = config.get_namespace()
        assert namespace == "airline-test_airline"

    def test_get_namespace_with_custom_namespace(self) -> None:
        """Test namespace with custom value."""
        config = TenantConfig(
            airline="ABC",
            namespace="custom-namespace"
        )
        
        namespace = config.get_namespace()
        assert namespace == "custom-namespace"

    def test_tenant_config_defaults(self) -> None:
        """Test TenantConfig with default values."""
        config = TenantConfig(airline="XYZ")
        
        assert config.airline == "XYZ"
        assert config.max_parallel_executions == 10
        assert config.active_modules == []
        assert config.rate_limit_per_minute == 1000


class TestCoordinate:
    """Test Coordinate model."""

    def test_coordinate_creation(self) -> None:
        """Test creating a valid Coordinate."""
        coord = Coordinate(latitude=41.405937, longitude=2.178605)
        
        assert coord.latitude == 41.405937
        assert coord.longitude == 2.178605

    def test_coordinate_validation(self) -> None:
        """Test Coordinate validation."""
        with pytest.raises(ValueError):
            Coordinate(latitude=91.0, longitude=0.0)  # Invalid latitude
            
        with pytest.raises(ValueError):
            Coordinate(latitude=0.0, longitude=181.0)  # Invalid longitude


class TestPositionReportEvent:
    """Test PositionReportEvent model."""

    def test_position_report_creation(self) -> None:
        """Test creating a valid PositionReportEvent."""
        report = PositionReportEvent(
            flight_id="ABC123",
            airline="ABC",
            aircraft_type="A320",
            registration="ABC-001",
            latitude=41.405937,
            longitude=2.178605,
        )
        
        assert report.flight_id == "ABC123"
        assert report.airline == "ABC"
        assert report.aircraft_type == "A320"
        assert report.registration == "ABC-001"
        assert report.latitude == 41.405937
        assert report.longitude == 2.178605
        assert isinstance(report.timestamp, datetime)

    def test_position_report_timestamp(self) -> None:
        """Test that timestamp is timezone-aware."""
        report = PositionReportEvent(
            flight_id="ABC123",
            airline="ABC",
            aircraft_type="A320",
            registration="ABC-001",
            latitude=41.405937,
            longitude=2.178605,
        )
        
        assert report.timestamp.tzinfo is not None
        assert report.timestamp.tzinfo == timezone.utc

    def test_position_report_optional_fields(self) -> None:
        """Test PositionReportEvent with optional fields."""
        report = PositionReportEvent(
            flight_id="ABC123",
            airline="ABC",
            aircraft_type="A320",
            registration="ABC-001",
            latitude=41.405937,
            longitude=2.178605,
            altitude=35000.0,
            speed=450.0,
            heading=90.0,
        )
        
        assert report.altitude == 35000.0
        assert report.speed == 450.0
        assert report.heading == 90.0


class TestFlightPlanEvent:
    """Test FlightPlanEvent model."""

    def test_flight_plan_creation(self) -> None:
        """Test creating a valid FlightPlanEvent."""
        route = [
            Coordinate(latitude=41.405937, longitude=2.178605),
            Coordinate(latitude=42.506379, longitude=1.521825),
        ]
        
        plan = FlightPlanEvent(
            flight_id="XYZ456",
            airline="XYZ",
            aircraft_type="B777",
            registration="XYZ-002",
            route=route,
        )
        
        assert plan.flight_id == "XYZ456"
        assert plan.airline == "XYZ"
        assert plan.aircraft_type == "B777"
        assert plan.registration == "XYZ-002"
        assert len(plan.route) == 2
        assert isinstance(plan.timestamp, datetime)

    def test_flight_plan_optional_fields(self) -> None:
        """Test FlightPlanEvent with optional fields."""
        route = [Coordinate(latitude=41.405937, longitude=2.178605)]
        
        plan = FlightPlanEvent(
            flight_id="XYZ456",
            airline="XYZ",
            aircraft_type="B777",
            registration="XYZ-002",
            route=route,
            departure_airport="MAD",
            arrival_airport="BCN",
            estimated_duration=120,
        )
        
        assert plan.departure_airport == "MAD"
        assert plan.arrival_airport == "BCN"
        assert plan.estimated_duration == 120


class TestJobRequest:
    """Test JobRequest model."""

    def test_job_request_creation(self) -> None:
        """Test creating a valid JobRequest."""
        request = JobRequest(
            event_type=EventType.POSITION_REPORT,
            event_data={"flight_id": "ABC123", "latitude": 41.0, "longitude": 2.0},
            airline="ABC",
            module_name="route_optimizer",
        )
        
        assert request.event_type == EventType.POSITION_REPORT
        assert request.airline == "ABC"
        assert request.module_name == "route_optimizer"
        assert request.event_data["flight_id"] == "ABC123"
        assert len(request.job_id) > 0  # UUID generated

    def test_job_request_defaults(self) -> None:
        """Test JobRequest with default values."""
        request = JobRequest(
            event_type=EventType.FLIGHT_PLAN,
            event_data={},
            airline="XYZ",
            module_name="fuel_optimizer",
        )
        
        assert request.priority == 1
        assert request.timeout_seconds is None


class TestJobResult:
    """Test JobResult model."""

    def test_job_result_creation(self) -> None:
        """Test creating a valid JobResult."""
        started_at = datetime.now(timezone.utc)
        
        job = JobResult(
            job_id="job-789",
            status=JobStatus.RUNNING,
            namespace="airline-abc",
            started_at=started_at,
        )
        
        assert job.job_id == "job-789"
        assert job.status == JobStatus.RUNNING
        assert job.namespace == "airline-abc"
        assert job.started_at == started_at
        assert job.completed_at is None
        assert job.duration_seconds is None

    def test_job_result_with_completion(self) -> None:
        """Test JobResult with completion data."""
        started_at = datetime.now(timezone.utc)
        completed_at = datetime.now(timezone.utc)
        
        job = JobResult(
            job_id="job-999",
            status=JobStatus.COMPLETED,
            namespace="airline-ghi",
            started_at=started_at,
            completed_at=completed_at,
            duration_seconds=120.5,
            result_data={"optimized_route": "MAD-BCN"},
        )
        
        assert job.status == JobStatus.COMPLETED
        assert job.completed_at == completed_at
        assert job.duration_seconds == 120.5
        assert job.result_data["optimized_route"] == "MAD-BCN"


class TestJobStatus:
    """Test JobStatus enum."""

    def test_job_status_values(self) -> None:
        """Test JobStatus enum values."""
        assert JobStatus.PENDING == "pending"
        assert JobStatus.RUNNING == "running"
        assert JobStatus.COMPLETED == "completed"
        assert JobStatus.FAILED == "failed"
        assert JobStatus.CANCELLED == "cancelled"


class TestEventType:
    """Test EventType enum."""

    def test_event_type_values(self) -> None:
        """Test EventType enum values."""
        assert EventType.POSITION_REPORT == "position_report"
        assert EventType.FLIGHT_PLAN == "flight_plan"


class TestHealthCheck:
    """Test HealthCheck model."""

    def test_health_check_creation(self) -> None:
        """Test creating a valid HealthCheck."""
        health = HealthCheck(
            status="healthy",
            version="1.0.0",
            dependencies={"kubernetes": "ok", "redis": "ok"}
        )
        
        assert health.status == "healthy"
        assert health.version == "1.0.0"
        assert health.dependencies["kubernetes"] == "ok"
        assert isinstance(health.timestamp, datetime)


class TestMetricsResponse:
    """Test MetricsResponse model."""

    def test_metrics_response_creation(self) -> None:
        """Test creating a valid MetricsResponse."""
        metrics = MetricsResponse(
            active_jobs=5,
            completed_jobs_24h=100,
            failed_jobs_24h=2,
            average_job_duration=45.5,
            tenants_count=3,
            cpu_usage_percent=75.0,
            memory_usage_percent=60.0,
        )
        
        assert metrics.active_jobs == 5
        assert metrics.completed_jobs_24h == 100
        assert metrics.failed_jobs_24h == 2
        assert metrics.average_job_duration == 45.5
        assert metrics.tenants_count == 3
        assert metrics.cpu_usage_percent == 75.0
        assert metrics.memory_usage_percent == 60.0
