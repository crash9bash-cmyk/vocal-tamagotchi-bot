"""Конфигурация бота.

Токен берётся из переменной окружения BOT_TOKEN (через .env).
Никогда не коммить .env и сам токен.
"""
from __future__ import annotations

import os

from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN: str | None = os.getenv("BOT_TOKEN")

# URL Mini App «Твой артист» (нужен публичный HTTPS, чтобы Telegram открыл).
# Локально можно оставить пустым — кнопка просто не показывается.
MINI_APP_URL: str = os.getenv("MINI_APP_URL", "")

# Строка БД. На хостинге (Railway/Render/VPS) сюда подставляется Postgres
# (например postgres://user:pass@host/db). Если пуста — бот берёт локальный
# SQLite (data/bot.db). SQLAlchemy-движок выбирается в db/session.py.
DATABASE_URL: str = os.getenv("DATABASE_URL", "")

# XP за прохождение урока (базовое начисление)
XP_PER_LESSON = 10
# Сколько уроков нужно пройти для +1 уровень (упрощённо)
XP_PER_LEVEL = 100


def require_token() -> str:
    """Вернуть токен или упасть с понятной ошибкой."""
    if not BOT_TOKEN:
        raise RuntimeError(
            "BOT_TOKEN не задан. Создай .env и впиши BOT_TOKEN=... "
            "(получить у @BotFather)."
        )
    return BOT_TOKEN
