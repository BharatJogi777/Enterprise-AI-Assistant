import psycopg
from psycopg.rows import dict_row
from enterprise_ai.core.config import get_settings

async def connect():
    return await psycopg.AsyncConnection.connect(get_settings().database_url,
                                                  row_factory=dict_row)

async def initialize_database() -> None:
    cfg = get_settings()
    async with await connect() as conn:
        await conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
        await conn.execute("""CREATE TABLE IF NOT EXISTS documents (
            id BIGSERIAL PRIMARY KEY, filename TEXT NOT NULL,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW())""")
        await conn.execute(f"""CREATE TABLE IF NOT EXISTS document_chunks (
            id BIGSERIAL PRIMARY KEY,
            document_id BIGINT NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
            chunk_index INTEGER NOT NULL, content TEXT NOT NULL,
            embedding vector({cfg.embedding_dimensions}) NOT NULL,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            UNIQUE(document_id, chunk_index))""")
        await conn.execute("""CREATE INDEX IF NOT EXISTS document_chunks_embedding_hnsw
            ON document_chunks USING hnsw (embedding vector_cosine_ops)""")
        await conn.commit()

async def database_ready() -> bool:
    try:
        async with await connect() as conn:
            await conn.execute("SELECT 1")
        return True
    except Exception:
        return False
