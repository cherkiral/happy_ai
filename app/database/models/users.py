from typing import Optional
from sqlalchemy import Integer, String, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from app.database.database import Base

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    tg_id: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)
    value: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    thread_id: Mapped[Optional[str]] = mapped_column(String, nullable=True) #Чтобы ии понимал от какого юзера сообщение
    created_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now())