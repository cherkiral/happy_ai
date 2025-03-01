import asyncio
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import desc
from app.database.models.messages import Message
from app.database.crud.base import BaseRepository

class MessageRepository(BaseRepository[Message]):
    def __init__(self, session: AsyncSession = None):
        super().__init__(Message, session)

    async def save_user_message(self, tg_id: int, message_text: str) -> Message:
        await asyncio.sleep(0.01) # по-другому не проходили тесты, видимо все одновременно сохраняло
        created_at = datetime.now(timezone.utc).replace(tzinfo=None)
        return await self.create(tg_id=tg_id, text=message_text, created_at=created_at)

    async def get_last_messages(self, tg_id: int, limit: int = 10) -> list[str]:
        result = await self.session.execute(
            select(Message.text)
            .where(Message.tg_id == tg_id)
            .order_by(desc(Message.created_at))
            .limit(limit)
        )
        return [row[0] for row in result.fetchall()]