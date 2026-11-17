from fastapi import APIRouter
from enterprise_ai.api.routes import health, documents, assistant

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(documents.router, prefix="/documents", tags=["documents"])
api_router.include_router(assistant.router, prefix="/assistant", tags=["assistant"])
