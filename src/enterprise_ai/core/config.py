import json
from functools import lru_cache
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config=SettingsConfigDict(env_file=".env",env_file_encoding="utf-8",extra="ignore")
    app_name: str="Enterprise AI Assistant"
    app_env: str="development"
    app_debug: bool=False
    api_v1_prefix: str="/api/v1"
    host: str="0.0.0.0"
    port: int=Field(default=8000,ge=1,le=65535)
    log_level: str="INFO"
    database_url: str="postgresql://enterprise_ai:local_only_change_me@localhost:5434/enterprise_ai"
    ollama_base_url: str="http://localhost:11434"
    ollama_chat_model: str="llama3.2:3b"
    ollama_embedding_model: str="nomic-embed-text"
    embedding_dimensions: int=Field(default=768,ge=1)
    request_timeout_seconds: float=Field(default=60,gt=0,le=300)
    max_upload_bytes: int=Field(default=10485760,ge=1024)
    chunk_size: int=Field(default=900,ge=100)
    chunk_overlap: int=Field(default=150,ge=0)
    retrieval_top_k: int=Field(default=5,ge=1,le=20)
    max_context_characters: int=Field(default=10000,ge=1000)
    api_key: str=""
    web_search_provider: str="tavily"
    tavily_api_key: str=""
    langfuse_public_key: str=""
    langfuse_secret_key: str=""
    langfuse_host: str="https://cloud.langfuse.com"
    agent_max_steps: int=Field(default=5,ge=1,le=12)
    conversation_memory_turns: int=Field(default=12,ge=1,le=50)
    allowed_tools: str="calculator,utc_time,search_internal_documents,search_web_tool"
    mcp_servers_json: str="[]"
    cors_origins: str="http://localhost:3000,http://localhost:8000"

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls,value: str)->str:
        value=value.upper()
        if value not in {"DEBUG","INFO","WARNING","ERROR","CRITICAL"}:
            raise ValueError("Unsupported log level")
        return value

    @field_validator("chunk_overlap")
    @classmethod
    def validate_overlap(cls,value: int,info):
        if value>=info.data.get("chunk_size",900):
            raise ValueError("chunk_overlap must be smaller than chunk_size")
        return value

    @field_validator("api_v1_prefix")
    @classmethod
    def normalize_prefix(cls,value: str)->str:
        return "/"+value.strip("/")

    def allowed_tool_names(self)->set[str]:
        return {x.strip() for x in self.allowed_tools.split(",") if x.strip()}

    def configured_mcp_servers(self)->list[dict]:
        try:
            items=json.loads(self.mcp_servers_json)
        except json.JSONDecodeError as exc:
            raise ValueError("MCP_SERVERS_JSON must be valid JSON") from exc
        if not isinstance(items,list):
            raise ValueError("MCP_SERVERS_JSON must be a JSON array")
        names=set()
        for item in items:
            if not isinstance(item,dict) or not all(k in item for k in ("name","url","allowed_tools")):
                raise ValueError("Each MCP server needs name, url and allowed_tools")
            if not isinstance(item["name"],str) or not item["name"] or item["name"] in names:
                raise ValueError("MCP server names must be unique non-empty strings")
            if not isinstance(item["url"],str) or not item["url"].startswith(("http://","https://")):
                raise ValueError("MCP server URLs must use HTTP or HTTPS")
            if not isinstance(item["allowed_tools"],list) or not all(isinstance(x,str) for x in item["allowed_tools"]):
                raise ValueError("MCP allowed_tools must be a list of tool names")
            names.add(item["name"])
        return items

    def cors_origin_list(self)->list[str]:
        return [x.strip() for x in self.cors_origins.split(",") if x.strip()]

@lru_cache
def get_settings()->Settings:
    return Settings()
