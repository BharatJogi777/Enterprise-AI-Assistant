from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from enterprise_ai.api.dependencies import require_api_key
from enterprise_ai.agents.graph import run_agent
from enterprise_ai.agents.multi_agent import run_multi_agent
from enterprise_ai.core.config import get_settings
from enterprise_ai.services.memory import append_message, get_history, delete_conversation

router = APIRouter(dependencies=[Depends(require_api_key)])

class ConversationRequest(BaseModel):
    conversation_id: UUID
    message: str = Field(min_length=2,max_length=4000)

@router.post("/chat")
async def chat(payload: ConversationRequest):
    cid=str(payload.conversation_id)
    history=await get_history(cid,get_settings().conversation_memory_turns)
    await append_message(cid,"user",payload.message)
    try:
        result=await run_agent(payload.message,history)
    except Exception:
        raise HTTPException(status_code=502,detail="Assistant orchestration failed") from None
    await append_message(cid,"assistant",result["answer"])
    return {"conversation_id":cid,**result}

@router.post("/research")
async def multi_agent_research(payload: ConversationRequest):
    cid=str(payload.conversation_id)
    await append_message(cid,"user",payload.message)
    try:
        result=await run_multi_agent(payload.message)
    except Exception:
        raise HTTPException(status_code=502,detail="Multi-agent research workflow failed") from None
    await append_message(cid,"assistant",result["answer"])
    return {"conversation_id":cid,**result}

@router.delete("/{conversation_id}")
async def clear_conversation(conversation_id: UUID):
    deleted=await delete_conversation(str(conversation_id))
    return {"conversation_id":str(conversation_id),"deleted_messages":deleted}
