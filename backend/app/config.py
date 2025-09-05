"""
Application configuration management.

Handles environment-based configuration with validation and type safety.
"""

import os
from functools import lru_cache
from typing import List, Optional

from pydantic import BaseModel, validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # Application
    app_name: str = "Equity Research Dashboard API"
    app_version: str = "1.0.0"
    debug: bool = False
    environment: str = "development"
    
    # API
    api_v1_prefix: str = "/api/v1"
    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:5173"]
    cors_allow_credentials: bool = True
    cors_allow_methods: List[str] = ["*"]
    cors_allow_headers: List[str] = ["*"]
    
    # Database
    database_url: str = "postgresql+asyncpg://postgres:password@localhost:5432/equity_research"
    database_echo: bool = False
    database_pool_size: int = 10
    database_max_overflow: int = 20
    database_pool_timeout: int = 30
    database_pool_recycle: int = 3600
    
    # Redis
    redis_url: str = "redis://localhost:6379/0"
    redis_max_connections: int = 20
    redis_socket_timeout: int = 5
    redis_socket_connect_timeout: int = 5
    redis_retry_on_timeout: bool = True
    
    # Authentication
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7
    password_min_length: int = 8
    
    # Security
    bcrypt_rounds: int = 12
    rate_limit_requests: int = 1000
    rate_limit_window: int = 3600  # 1 hour
    
    # External APIs
    alpha_vantage_api_key: Optional[str] = None
    financial_modeling_prep_api_key: Optional[str] = None
    tiingo_api_key: Optional[str] = None
    yahoo_finance_enabled: bool = True
    
    # Monitoring
    sentry_dsn: Optional[str] = None
    prometheus_enabled: bool = True
    log_level: str = "INFO"
    log_format: str = "json"
    
    # File Storage
    upload_max_size: int = 10 * 1024 * 1024  # 10MB
    upload_allowed_extensions: List[str] = [".pdf", ".xlsx", ".csv", ".json"]
    
    # WebSocket
    websocket_heartbeat_interval: int = 30
    websocket_max_connections: int = 1000
    
    @validator("cors_origins", pre=True)
    def assemble_cors_origins(cls, v):
        """Parse CORS origins from string or list."""
        if isinstance(v, str):
            return [i.strip() for i in v.split(",")]
        return v
    
    @validator("environment")
    def validate_environment(cls, v):
        """Validate environment setting."""
        allowed = ["development", "staging", "production"]
        if v not in allowed:
            raise ValueError(f"Environment must be one of {allowed}")
        return v
    
    @validator("log_level")
    def validate_log_level(cls, v):
        """Validate log level."""
        allowed = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in allowed:
            raise ValueError(f"Log level must be one of {allowed}")
        return v.upper()
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached application settings."""
    return Settings()


# Global settings instance
settings = get_settings()
