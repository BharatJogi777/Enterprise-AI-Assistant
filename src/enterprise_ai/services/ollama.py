import httpx
from enterprise_ai.core.config import get_settings

async def _post(path: str, payload: dict) -> dict:
    cfg = get_settings()
    async with httpx.AsyncClient(base_url=cfg.ollama_base_url,
                                 timeout=cfg.request_timeout_seconds) as client:
        response = await client.post(path, json=payload)
        response.raise_for_status()
        return response.json()

async def embed_texts(texts: list[str]) -> list[list[float]]:
    cfg = get_settings()
    data = await _post("/api/embed", {"model": cfg.ollama_embedding_model, "input": texts})
    vectors = data.get("embeddings")
    if not isinstance(vectors, list) or len(vectors) != len(texts):
        raise RuntimeError("Ollama returned an invalid embedding response")
    if any(len(v) != cfg.embedding_dimensions for v in vectors):
        raise RuntimeError("Embedding dimensions do not match EMBEDDING_DIMENSIONS")
    return vectors

async def chat(prompt: str) -> str:
    cfg = get_settings()
    data = await _post("/api/chat", {"model": cfg.ollama_chat_model,
        "messages": [{"role": "user", "content": prompt}], "stream": False,
        "options": {"temperature": 0.1}})
    answer = data.get("message", {}).get("content")
    if not isinstance(answer, str) or not answer.strip():
        raise RuntimeError("Ollama returned an empty response")
    return answer.strip()

async def ollama_ready() -> bool:
    try:
        cfg = get_settings()
        async with httpx.AsyncClient(base_url=cfg.ollama_base_url, timeout=3) as client:
            response = await client.get("/api/tags")
            return response.is_success
    except httpx.HTTPError:
        return False
