from typing import Type, TypeVar, Generic, List, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, delete
from app.database.database import SessionLocal

T = TypeVar("T")

class BaseRepository(Generic[T]):
    def __init__(self, model: Type[T], session: AsyncSession = None):
        self.model = model
        self.session = session or SessionLocal()

    async def get_by_id(self, id: int) -> Optional[T]:
        result = await self.session.execute(select(self.model).where(self.model.id == id))
        return result.scalars().first()

    async def get_all(self, limit: int = 100) -> List[T]:
        result = await self.session.execute(select(self.model).limit(limit))
        return result.scalars().all()

    async def get_filtered(self, order_by=None, **filters) -> List[T]:
        stmt = select(self.model).filter_by(**filters)
        if order_by:
            stmt = stmt.order_by(order_by)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def create(self, **data) -> T:
        obj = self.model(**data)
        self.session.add(obj)
        await self.session.commit()
        await self.session.refresh(obj)
        return obj

    async def update(self, id: int, **data) -> Optional[T]:
        stmt = update(self.model).where(self.model.id == id).values(**data)
        await self.session.execute(stmt)
        await self.session.commit()
        return await self.get_by_id(id)

    async def delete(self, id: int) -> bool:
        stmt = delete(self.model).where(self.model.id == id)
        await self.session.execute(stmt)
        await self.session.commit()
        return True
