from fastapi import FastAPI
from enterprise_ai.api.router import api_router
from enterprise_ai.core.config import get_settings
from enterprise_ai.core.logging import configure_logging
from enterprise_ai.core.middleware import RequestContextMiddleware

def create_app() -> FastAPI:
    settings = get_settings()
    configure_logging(settings.log_level)
    app = FastAPI(title=settings.app_name, version="0.1.0", debug=settings.app_debug)
    app.add_middleware(RequestContextMiddleware)
    app.include_router(api_router, prefix=settings.api_v1_prefix)
    return app

app = create_app()
