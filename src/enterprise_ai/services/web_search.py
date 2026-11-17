import httpx
from enterprise_ai.core.config import get_settings

class SearchUnavailable(RuntimeError):
    pass

async def search_web(query: str, limit: int = 5) -> list[dict]:
    cfg = get_settings()
    if cfg.web_search_provider == "tavily":
        if not cfg.tavily_api_key:
            raise SearchUnavailable("TAVILY_API_KEY is required for the Tavily provider")
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.post("https://api.tavily.com/search", json={
                "api_key":cfg.tavily_api_key,"query":query,"max_results":min(limit,10),
                "search_depth":"basic","include_answer":False})
            response.raise_for_status()
            data=response.json()
        return [{"title":x.get("title",""),"url":x.get("url",""),
                 "snippet":x.get("content","")} for x in data.get("results",[])]
    # DuckDuckGo Instant Answer is a limited fallback, not a full web index.
    async with httpx.AsyncClient(timeout=10,headers={"User-Agent":"EnterpriseAI/1.0"}) as client:
        response=await client.get("https://api.duckduckgo.com/",
            params={"q":query,"format":"json","no_html":1,"skip_disambig":1})
        response.raise_for_status()
        data=response.json()
    items=[]
    abstract=data.get("AbstractText")
    if abstract:
        items.append({"title":data.get("Heading") or query,
                      "url":data.get("AbstractURL",""),"snippet":abstract})
    for topic in data.get("RelatedTopics",[]):
        if isinstance(topic,dict) and topic.get("Text") and topic.get("FirstURL"):
            items.append({"title":topic["Text"][:160],"url":topic["FirstURL"],
                          "snippet":topic["Text"]})
        if len(items)>=limit:
            break
    return items[:limit]
