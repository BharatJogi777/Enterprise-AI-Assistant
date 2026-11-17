from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from enterprise_ai.api.dependencies import require_api_key
from enterprise_ai.core.config import get_settings
from enterprise_ai.services.rag import ingest_document, list_documents

router = APIRouter(dependencies=[Depends(require_api_key)])

@router.post("", status_code=201)
async def upload_document(file: UploadFile = File(...)):
    cfg = get_settings()
    filename = (file.filename or "").strip()
    if not filename or not filename.lower().endswith((".txt", ".md")):
        raise HTTPException(status_code=415, detail="Only .txt and .md files are supported")
    content = await file.read(cfg.max_upload_bytes + 1)
    if len(content) > cfg.max_upload_bytes:
        raise HTTPException(status_code=413, detail="File exceeds upload limit")
    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="Document must be UTF-8") from None
    if not text.strip():
        raise HTTPException(status_code=400, detail="Document is empty")
    return await ingest_document(filename, text)

@router.get("")
async def get_documents():
    return {"items": await list_documents()}
