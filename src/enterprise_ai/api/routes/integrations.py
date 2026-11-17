from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from enterprise_ai.api.dependencies import require_api_key
from enterprise_ai.core.config import get_settings
from enterprise_ai.services.web_search import search_web, SearchUnavailable
from enterprise_ai.services.mcp_client import list_remote_tools, call_remote_tool

router=APIRouter(dependencies=[Depends(require_api_key)])

class WebSearchRequest(BaseModel):
    query: str=Field(min_length=2,max_length=500)
    limit: int=Field(default=5,ge=1,le=10)

class MCPCallRequest(BaseModel):
    server_name: str=Field(min_length=1,max_length=128)
    tool_name: str=Field(min_length=1,max_length=128)
    arguments: dict=Field(default_factory=dict)

@router.post("/web-search")
async def web_search(payload: WebSearchRequest):
    try:
        return {"query":payload.query,"results":await search_web(payload.query,payload.limit),
                "provider":get_settings().web_search_provider}
    except SearchUnavailable as exc:
        raise HTTPException(status_code=503,detail=str(exc)) from exc
    except Exception:
        raise HTTPException(status_code=502,detail="Web search provider failed") from None

@router.get("/mcp/tools")
async def mcp_tools():
    cfg=get_settings()
    try:
        servers=cfg.configured_mcp_servers()
    except ValueError:
        raise HTTPException(status_code=503,detail="MCP server configuration is invalid") from None
    if not servers:
        raise HTTPException(status_code=503,detail="No MCP servers are configured")
    output=[]
    for server in servers:
        try:
            discovered=await list_remote_tools(server["url"])
            allowed=set(server["allowed_tools"])
            output.append({"server":server["name"],
                "tools":[x for x in discovered if x["name"] in allowed]})
        except Exception:
            output.append({"server":server["name"],"error":"Unable to list tools"})
    return {"servers":output}

@router.post("/mcp/call")
async def mcp_call(payload: MCPCallRequest):
    try:
        servers=get_settings().configured_mcp_servers()
    except ValueError:
        raise HTTPException(status_code=503,detail="MCP server configuration is invalid") from None
    server=next((x for x in servers if x["name"]==payload.server_name),None)
    if server is None:
        raise HTTPException(status_code=404,detail="MCP server is not configured")
    if payload.tool_name not in set(server["allowed_tools"]):
        raise HTTPException(status_code=403,detail="MCP tool is not allowlisted for this server")
    try:
        result=await call_remote_tool(server["url"],payload.tool_name,payload.arguments)
        if result["is_error"]:
            raise HTTPException(status_code=502,detail="MCP tool returned an error")
        return {"server":payload.server_name,"tool":payload.tool_name,"result":result["content"]}
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=502,detail="MCP tool execution failed") from None
