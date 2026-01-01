"""
Tarento AI Complaint Tracking System - Configuration
Pydantic Settings for all configuration options
"""

from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field
import json


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Application
    ENVIRONMENT: str = "development"
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True
    API_VERSION: str = "v1"
    
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/tarento_complaints"
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 0
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # JWT Authentication
    SECRET_KEY: str = "dev_secret_key_change_in_production_must_be_32_chars_min"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Google Gemini AI
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-pro"
    GEMINI_TEMPERATURE: float = 0.2
    GEMINI_MAX_TOKENS: int = 2048
    
    # Groq AI (Alternative)
    GROQ_API_KEY: str = ""
    
    # Email IMAP
    EMAIL_HOST: str = "imap.gmail.com"
    EMAIL_PORT: int = 993
    EMAIL_USERNAME: str = ""
    EMAIL_PASSWORD: str = ""
    EMAIL_USE_TLS: bool = True
    
    # SMTP
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM_EMAIL: str = "noreply@tarento.com"
    SMTP_FROM_NAME: str = "Tarento Complaint System"
    
    # SLA Thresholds (hours)
    SLA_CRITICAL: int = 4
    SLA_HIGH: int = 24
    SLA_MEDIUM: int = 72
    SLA_LOW: int = 168
    
    # Agent Schedules
    AGENT_EMAIL_PARSER_SCHEDULE: str = "*/5 * * * *"
    AGENT_CATEGORIZATION_SCHEDULE: str = "*/2 * * * *"
    AGENT_MAPPING_SCHEDULE: str = "*/3 * * * *"
    AGENT_ESCALATION_SCHEDULE: str = "0 * * * *"
    AGENT_PATTERN_SCHEDULE: str = "0 2 * * *"
    AGENT_INSIGHT_SCHEDULE: str = "0 3 * * 0"
    
    # CORS
    CORS_ORIGINS: str = '["http://localhost:3000","http://localhost:5173","http://localhost:3001","http://localhost:8001"]'
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins from JSON string"""
        try:
            return json.loads(self.CORS_ORIGINS)
        except json.JSONDecodeError:
            return ["http://localhost:3000", "http://localhost:5173", "http://localhost:3001", "http://localhost:8001"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
