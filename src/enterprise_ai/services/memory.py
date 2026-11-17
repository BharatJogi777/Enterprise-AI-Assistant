from enterprise_ai.services.database import connect, initialize_database

async def ensure_memory_schema() -> None:
    await initialize_database()
    async with await connect() as conn:
        await conn.execute("""CREATE TABLE IF NOT EXISTS conversation_messages (
            id BIGSERIAL PRIMARY KEY, conversation_id TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('user','assistant')),
            content TEXT NOT NULL, created_at TIMESTAMPTZ NOT NULL DEFAULT NOW())""")
        await conn.execute("""CREATE INDEX IF NOT EXISTS conversation_messages_recent
            ON conversation_messages(conversation_id, created_at DESC)""")
        await conn.commit()

async def append_message(conversation_id: str, role: str, content: str) -> None:
    await ensure_memory_schema()
    async with await connect() as conn:
        await conn.execute("INSERT INTO conversation_messages(conversation_id,role,content) VALUES (%s,%s,%s)",
                           (conversation_id,role,content[:12000]))
        await conn.commit()

async def get_history(conversation_id: str, turns: int = 12) -> list[dict]:
    await ensure_memory_schema()
    async with await connect() as conn:
        rows=await (await conn.execute("""SELECT role,content FROM (
            SELECT role,content,created_at,id FROM conversation_messages
            WHERE conversation_id=%s ORDER BY created_at DESC,id DESC LIMIT %s
            ) recent ORDER BY created_at ASC,id ASC""",(conversation_id,turns*2))).fetchall()
    return [dict(row) for row in rows]

async def delete_conversation(conversation_id: str) -> int:
    await ensure_memory_schema()
    async with await connect() as conn:
        cursor=await conn.execute("DELETE FROM conversation_messages WHERE conversation_id=%s",
                                  (conversation_id,))
        await conn.commit()
        return cursor.rowcount
