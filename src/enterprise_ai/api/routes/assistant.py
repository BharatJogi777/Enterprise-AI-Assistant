from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from enterprise_ai.api.dependencies import require_api_key
from enterprise_ai.services.rag import answer_question, search_documents

router = APIRouter(dependencies=[Depends(require_api_key)])

class AskRequest(BaseModel):
    question: str = Field(min_length=3, max_length=4000)
    top_k: int | None = Field(default=None, ge=1, le=20)

class SearchRequest(BaseModel):
    query: str = Field(min_length=2, max_length=2000)
    top_k: int | None = Field(default=None, ge=1, le=20)

@router.post("/ask")
async def ask(payload: AskRequest):
    return await answer_question(payload.question, payload.top_k)

@router.post("/search")
async def search(payload: SearchRequest):
    return {"results": await search_documents(payload.query, payload.top_k)}
