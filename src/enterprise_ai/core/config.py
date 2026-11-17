from functools import lru_cache
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")
    app_name: str = "Enterprise AI Assistant"
    app_env: str = "development"
    app_debug: bool = False
    api_v1_prefix: str = "/api/v1"
    host: str = "0.0.0.0"
    port: int = Field(default=8000, ge=1, le=65535)
    log_level: str = "INFO"
    database_url: str = "postgresql://enterprise_ai:local_only_change_me@localhost:5434/enterprise_ai"
    ollama_base_url: str = "http://localhost:11434"
    ollama_chat_model: str = "llama3.2:3b"
    ollama_embedding_model: str = "nomic-embed-text"
    embedding_dimensions: int = Field(default=768, ge=1)
    request_timeout_seconds: float = Field(default=60, gt=0, le=300)
    max_upload_bytes: int = Field(default=10485760, ge=1024)
    chunk_size: int = Field(default=900, ge=100)
    chunk_overlap: int = Field(default=150, ge=0)
    retrieval_top_k: int = Field(default=5, ge=1, le=20)
    max_context_characters: int = Field(default=10000, ge=1000)
    api_key: str = ""

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, value: str) -> str:
        value = value.upper()
        if value not in {"DEBUG","INFO","WARNING","ERROR","CRITICAL"}:
            raise ValueError("Unsupported log level")
        return value

    @field_validator("chunk_overlap")
    @classmethod
    def validate_overlap(cls, value: int, info):
        if value >= info.data.get("chunk_size", 900):
            raise ValueError("chunk_overlap must be smaller than chunk_size")
        return value

    @field_validator("api_v1_prefix")
    @classmethod
    def normalize_prefix(cls, value: str) -> str:
        return "/" + value.strip("/")

@lru_cache
def get_settings() -> Settings:
    return Settings()
