from fastapi import APIRouter
from enterprise_ai.services.database import database_ready
from enterprise_ai.services.ollama import ollama_ready

router = APIRouter()

@router.get("/health/live")
async def liveness():
    return {"status": "alive"}

@router.get("/health/ready")
async def readiness():
    db_ok, model_ok = await database_ready(), await ollama_ready()
    return {"status": "ready" if db_ok and model_ok else "not_ready",
            "dependencies": {"database": db_ok, "ollama": model_ok}}
