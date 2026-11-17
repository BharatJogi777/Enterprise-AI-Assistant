from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from enterprise_ai.api.dependencies import require_api_key
from enterprise_ai.core.config import get_settings
from enterprise_ai.services.web_search import search_web, SearchUnavailable
from enterprise_ai.services.mcp_client import list_remote_tools, call_remote_tool

router = APIRouter(dependencies=[Depends(require_api_key)])

class WebSearchRequest(BaseModel):
    query: str = Field(min_length=2, max_length=500)
    limit: int = Field(default=5, ge=1, le=10)

class MCPCallRequest(BaseModel):
    tool_name: str = Field(min_length=1, max_length=128)
    arguments: dict = Field(default_factory=dict)

@router.post("/web-search")
async def web_search(payload: WebSearchRequest):
    try:
        results = await search_web(payload.query, payload.limit)
        return {"query":payload.query, "results":results,
                "provider":get_settings().web_search_provider}
    except SearchUnavailable as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception:
        raise HTTPException(status_code=502, detail="Web search provider failed") from None

@router.get("/mcp/tools")
async def mcp_tools():
    cfg = get_settings()
    if not cfg.mcp_server_url:
        raise HTTPException(status_code=503, detail="MCP_SERVER_URL is not configured")
    try:
        tools = await list_remote_tools(cfg.mcp_server_url)
        allowed = cfg.mcp_allowed_tool_names()
        return {"tools":[item for item in tools if item["name"] in allowed]}
    except Exception:
        raise HTTPException(status_code=502, detail="Unable to list MCP tools") from None

@router.post("/mcp/call")
async def mcp_call(payload: MCPCallRequest):
    cfg = get_settings()
    if not cfg.mcp_server_url:
        raise HTTPException(status_code=503, detail="MCP_SERVER_URL is not configured")
    if payload.tool_name not in cfg.mcp_allowed_tool_names():
        raise HTTPException(status_code=403, detail="MCP tool is not allowlisted")
    try:
        result = await call_remote_tool(cfg.mcp_server_url, payload.tool_name, payload.arguments)
        if result["is_error"]:
            raise HTTPException(status_code=502, detail="MCP tool returned an error")
        return {"tool":payload.tool_name, "result":result["content"]}
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=502, detail="MCP tool execution failed") from None
