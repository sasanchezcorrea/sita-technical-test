"""Configuration management for OptiFlight Coordinator."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    # Application
    app_name: str = "OptiFlight Coordinator"
    app_version: str = "1.0.0"
    debug: bool = False
    log_level: str = "INFO"

    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_workers: int = 1

    # Database - PostgreSQL (Primary-Replica Architecture)
    database_url: str | None = None  # Legacy, prefer individual settings
    database_host: str = "postgresql"
    database_port: int = 5432
    database_name: str = "optiflight_db"
    database_username: str = "optiflight"
    database_password: str = "secure-optiflight-password"
    database_pool_size: int = 20
    database_max_overflow: int = 10
    database_pool_timeout: int = 30
    database_pool_recycle: int = 3600
    database_echo: bool = False

    # Database - Read Replica Configuration
    database_replica_enabled: bool = True
    database_replica_host: str = "postgresql-read"
    database_replica_port: int = 5432

    # Redis - Cluster Configuration
    redis_url: str = "redis://localhost:6379"  # Legacy, prefer cluster settings
    redis_enabled: bool = True
    redis_host: str = "redis"
    redis_port: int = 6379
    redis_password: str = "secure-redis-password"
    redis_db: int = 0
    redis_cluster_enabled: bool = True
    redis_cluster_nodes: str = "redis-0:6379,redis-1:6379,redis-2:6379"
    redis_max_connections: int = 50
    redis_socket_timeout: int = 5
    redis_socket_connect_timeout: int = 5
    redis_retry_on_timeout: bool = True
    redis_decode_responses: bool = True

    # Kubernetes
    kubernetes_namespace: str = "optiflight-system"
    in_cluster: bool = True

    # Message Queues - Kafka
    kafka_enabled: bool = True
    kafka_bootstrap_servers: str = "kafka:9092"
    kafka_username: str = "optiflight"
    kafka_password: str = "secure-kafka-password"
    kafka_consumer_group: str = "optiflight-coordinator"
    kafka_auto_offset_reset: str = "earliest"

    # Message Queues - RabbitMQ
    rabbitmq_enabled: bool = True
    rabbitmq_host: str = "rabbitmq"
    rabbitmq_port: int = 5672
    rabbitmq_username: str = "optiflight"
    rabbitmq_password: str = "secure-rabbitmq-password"
    rabbitmq_vhost: str = "/"
    rabbitmq_exchange: str = "optiflight"

    # Event Processing Mode (rest, kafka, rabbitmq, dual)
    event_processing_mode: str = "dual"

    # Rate Limiting
    rate_limit_per_minute: int = 1000

    # Optimization Modules
    module_timeout_seconds: int = 300
    max_concurrent_jobs_per_tenant: int = 10

    # Monitoring
    metrics_enabled: bool = True
    tracing_enabled: bool = True

    # External Services Configuration
    external_services_mode: str = "mock"  # "mock" or "real"

    # OptiCore API
    opticore_base_url: str = "http://mock-opticore:8001"
    opticore_api_key: str | None = None
    opticore_timeout: int = 30

    # Freya Climb API
    freya_climb_url: str = "http://mock-freya-climb:8002"
    freya_climb_api_key: str | None = None
    freya_climb_timeout: int = 30

    # Freya Level API
    freya_level_url: str = "http://mock-freya-level:8003"
    freya_level_api_key: str | None = None
    freya_level_timeout: int = 30

    # V.M. API (Weather/NOTAM service)
    vm_api_url: str = "http://mock-vm-api:8004"
    vm_api_key: str | None = None
    vm_api_timeout: int = 30

    # V.A.Z. API (Airspace/Navigation service)
    vaz_api_url: str = "http://mock-vaz-api:8005"
    vaz_api_key: str | None = None
    vaz_api_timeout: int = 30

    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
_settings: Settings | None = None


def get_settings() -> Settings:
    """
    Get application settings singleton.

    Returns:
        Settings instance
    """
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


# Create default settings instance for backward compatibility
settings = get_settings()
