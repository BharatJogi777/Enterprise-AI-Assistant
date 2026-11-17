from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from enterprise_ai.api.router import api_router
from enterprise_ai.core.config import get_settings
from enterprise_ai.core.logging import configure_logging
from enterprise_ai.core.middleware import RequestContextMiddleware

def create_app() -> FastAPI:
    cfg = get_settings()
    configure_logging(cfg.log_level)
    app = FastAPI(title=cfg.app_name, version="1.0.0", debug=cfg.app_debug,
                  description="Local-first enterprise assistant API.")
    app.add_middleware(RequestContextMiddleware)
    app.add_middleware(CORSMiddleware, allow_origins=cfg.cors_origin_list(),
                       allow_credentials=False, allow_methods=["GET","POST","DELETE"],
                       allow_headers=["Authorization","Content-Type","X-API-Key","X-Request-ID"])
    app.include_router(api_router, prefix=cfg.api_v1_prefix)
    return app

app = create_app()
