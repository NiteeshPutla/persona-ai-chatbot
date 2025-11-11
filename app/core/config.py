"""
Centralized configuration management using Pydantic Settings.
"""
try:
    from pydantic_settings import BaseSettings
except ImportError:
    # Fallback for older pydantic versions
    from pydantic import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # API Configuration
    api_title: str = "Persona-Switching AI Chatbot"
    api_version: str = "1.0.0"
    api_description: str = "An agentic chatbot that can dynamically switch between different expert personas"
    
    # OpenAI Configuration
    openai_api_key: Optional[str] = None
    model_name: str = "gpt-3.5-turbo"
    temperature: float = 0.7
    
    # Database Configuration
    database_url: str = "sqlite:///chatbot.db"
    database_echo: bool = False  # SQLAlchemy echo mode
    
    # Logging Configuration
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = False
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()

