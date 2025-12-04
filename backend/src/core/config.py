"""Application configuration using Pydantic Settings."""
from typing import List
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""
    
    # Application
    APP_NAME: str = "Smart Heaven"
    APP_VERSION: str = "2.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "production"
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Database
    DATABASE_URL: str
    DB_ECHO: bool = False
    
    # MQTT
    MQTT_BROKER_HOST: str = "192.168.31.153"
    MQTT_BROKER_PORT: int = 1883
    MQTT_USERNAME: str = ""
    MQTT_PASSWORD: str = ""
    MQTT_CLIENT_ID: str = "smart_heaven_server"
    
    # MQTT Topics
    MQTT_TOPIC_BUTTON: str = "casa/evento/botao"
    MQTT_TOPIC_COMMAND: str = "casa/servidor/comando_lampada"
    MQTT_TOPIC_STATE: str = "casa/estado/lampada"
    MQTT_TOPIC_DEBUG: str = "debug/esp8266"
    MQTT_TOPIC_WEB_COMMAND: str = "casa/servidor_web/comando_lampada"
    MQTT_TOPIC_ESP_COMMAND: str = "casa/esp/acionar_lampada"
    
    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "https://www.smart-heaven.com"
    ]
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True
    )
    
    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse CORS origins from string or list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v


# Global settings instance
settings = Settings()
