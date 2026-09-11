"""Async engine + sessionmaker.

Поддерживает два режима:
- Локально / тесты: SQLite (data/bot.db), если DATABASE_URL не задан.
- Хостинг (Railway/Render/VPS): Postgres, если задан DATABASE_URL
  (Railway выдаёт строку вида postgres://..., приводим к postgresql+asyncpg://).
Модели (db/models.py) не меняются — только движок.
"""
from __future__ import annotations

import os

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from .models import Base


def _resolve_db_url() -> str:
    raw = os.getenv("DATABASE_URL", "")
    if raw:
        # Railway/VPS часто дают postgres:// — SQLAlchemy нужен префикс asyncpg
        if raw.startswith("postgres://"):
            return "postgresql+asyncpg://" + raw[len("postgres://"):]
        if raw.startswith("postgresql://"):
            return "postgresql+asyncpg://" + raw[len("postgresql://"):]
        return raw
    # локальный фоллбэк
    os.makedirs("data", exist_ok=True)
    return "sqlite+aiosqlite:///data/bot.db"


DATABASE_URL = _resolve_db_url()
engine = create_async_engine(DATABASE_URL, echo=False, future=True)
SessionLocal = async_sessionmaker(
    bind=engine, expire_on_commit=False, class_=AsyncSession
)


async def init_db() -> None:
    """Создать таблицы (если ещё нет). Вызывается при старте бота."""
    if DATABASE_URL.startswith("sqlite"):
        os.makedirs("data", exist_ok=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_session() -> AsyncSession:
    """Фабрика сессий для зависимостей/хендлеров."""
    async with SessionLocal() as session:
        yield session
