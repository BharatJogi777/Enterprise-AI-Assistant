from fastapi import APIRouter
from enterprise_ai.services.database import database_ready
from enterprise_ai.services.ollama import ollama_ready

router = APIRouter()

@router.get("/health/live")
async def liveness():
    return {"status":"alive"}

@router.get("/health/ready")
async def readiness():
    db_ok, ollama_ok = await database_ready(), await ollama_ready()
    ready = db_ok and ollama_ok
    return {"status":"ready" if ready else "not_ready",
            "dependencies":{"database":db_ok,"ollama":ollama_ok}}
