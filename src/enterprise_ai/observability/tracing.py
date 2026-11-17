"""Optional Langfuse integration scaffold; app operation does not depend on telemetry."""
from enterprise_ai.core.config import get_settings

def langfuse_enabled() -> bool:
    cfg=get_settings()
    return bool(cfg.langfuse_public_key and cfg.langfuse_secret_key)

def flush_tracing() -> None:
    if not langfuse_enabled():
        return
    try:
        from langfuse import get_client
        get_client().flush()
    except Exception:
        # Telemetry failures must not break user requests.
        return
