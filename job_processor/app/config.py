"""Configuration management for OptiFlight Coordinator."""

from pydantic_settings import BaseSettings
from typing import Optional


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

    # Database
    database_url: Optional[str] = None
    redis_url: str = "redis://localhost:6379"

    # Kubernetes
    kubernetes_namespace: str = "optiflight-system"
    in_cluster: bool = True

    # Rate Limiting
    rate_limit_per_minute: int = 1000

    # Optimization Modules
    module_timeout_seconds: int = 300
    max_concurrent_jobs_per_tenant: int = 10

    # Monitoring
    metrics_enabled: bool = True
    tracing_enabled: bool = True

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
