import secrets
from fastapi import Header, HTTPException
from enterprise_ai.core.config import get_settings

async def require_api_key(x_api_key: str | None = Header(default=None)) -> None:
    cfg = get_settings()
    if not cfg.api_key:
        if cfg.app_env.lower() not in {"development","test"}:
            raise HTTPException(status_code=503, detail="API_KEY must be configured")
        return
    if not x_api_key or not secrets.compare_digest(x_api_key, cfg.api_key):
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
