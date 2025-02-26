import asyncpg
from config import settings

async def get_db_connection():
    return await asyncpg.connect(
        user=settings.DB_USER,
        password=settings.DB_PASSWORD,
        database=settings.DB_NAME,
        host=settings.DB_HOST,
        port=settings.DB_PORT,
    )

async def init_db():
    conn = await get_db_connection()
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS voice_messages (
            id SERIAL PRIMARY KEY,
            telegram_user_id BIGINT,
            file_name TEXT,
            file_data BYTEA,
            created_at TIMESTAMP DEFAULT NOW()
        )
    """)
    await conn.close()
