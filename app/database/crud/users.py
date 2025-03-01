from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database.models.users import User
from app.database.crud.base import BaseRepository
from app.utils.utils import create_thread

class UserRepository(BaseRepository[User]):
    def __init__(self, session: AsyncSession = None):
        super().__init__(User, session)

    async def get_by_tg_id(self, tg_id: int) -> User | None:
        result = await self.session.execute(select(User).where(User.tg_id == tg_id))
        return result.scalars().first()

    async def get_or_create_thread(self, tg_id: int) -> str:
        result = await self.session.execute(select(User).where(User.tg_id == tg_id))
        user = result.scalars().first()

        if user.thread_id:
            return user.thread_id

        thread_id = await create_thread()
        user.thread_id = thread_id
        await self.session.commit()

        return thread_id

    async def refresh_user_thread(self, tg_id: int) -> str:
        result = await self.session.execute(select(User).where(User.tg_id == tg_id))
        user = result.scalars().first()

        new_thread = await create_thread()

        user.thread_id = new_thread
        await self.session.commit()

        return new_thread

    async def update_user_thread_id(self, tg_id: int, thread_id: str):
        result = await self.session.execute(select(User).where(User.tg_id == tg_id))
        user = result.scalars().first()

        user.thread_id = thread_id
        await self.session.commit()

    async def create_user(self, tg_id: int) -> User:
        existing_user = await self.get_by_tg_id(tg_id)
        if existing_user:
            return existing_user

        thread_id = await create_thread()
        new_user = await self.create(tg_id=tg_id, value=None, thread_id=thread_id)
        return new_user

    async def get_user_values(self, tg_id: int) -> User.value | None:
        result = await self.session.execute(select(User.value).where(User.tg_id == tg_id))
        return result.scalars().all()

    async def delete_user_values(self, tg_id: int):
        await self.session.execute(update(User).where(User.tg_id == tg_id).values(value=None))
        await self.session.commit()

    async def update_user_values(self, user_id: int, new_values: str):
        result = await self.session.execute(select(User).where(User.id == user_id))
        user = result.scalars().first()

        existing_values = set(user.value.split(", ")) if user.value else set()
        new_values_set = set(new_values.split(", "))

        updated_values = ", ".join(existing_values | new_values_set)

        await self.session.execute(
            update(User).where(User.id == user_id).values(value=updated_values)
        )
        await self.session.commit()
