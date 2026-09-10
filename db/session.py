"""Async engine + sessionmaker (aiosqlite)."""
from __future__ import annotations

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from .models import Base

# v1: локальный SQLite-файл. Позже меняется на Postgres без правок моделей.
DB_PATH = "data/bot.db"
DATABASE_URL = f"sqlite+aiosqlite:///{DB_PATH}"

engine = create_async_engine(DATABASE_URL, echo=False, future=True)
SessionLocal = async_sessionmaker(
    bind=engine, expire_on_commit=False, class_=AsyncSession
)


async def init_db() -> None:
    """Создать таблицы (если ещё нет). Вызывается при старте бота."""
    import os

    os.makedirs("data", exist_ok=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_session() -> AsyncSession:
    """Фабрика сессий для зависимостей/хендлеров."""
    async with SessionLocal() as session:
        yield session
