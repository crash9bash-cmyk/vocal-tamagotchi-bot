"""Хендлер /start — регистрация пользователя + главное меню."""
from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

from db.session import SessionLocal
from db.models import User, UserStats
from keyboards import main_menu
from config import MINI_APP_URL

router = Router()


async def _register_user(session, tg_user) -> User:
    """Создать User + UserStats при первом запуске, иначе вернуть существующего."""
    user = (
        await session.execute(
            User.__table__.select().where(User.telegram_id == tg_user.id)
        )
    ).scalar_one_or_none()
    if user is None:
        user = User(telegram_id=tg_user.id, username=tg_user.username or None)
        session.add(user)
        await session.flush()  # нужен user.id для stats
        session.add(UserStats(user_id=user.id))
        await session.commit()
    return user


@router.message(Command("start"))
async def cmd_start(message: Message) -> None:
    async with SessionLocal() as session:
        user = await _register_user(session, message.from_user)
    await message.answer(
        f"Привет, {message.from_user.first_name}! 👋\n\n"
        f"Я — твой вокальный тамагочи. Растим артиста вместе.\n"
        f"Уровень: {user.level} · XP: {user.xp} · стрик: {user.current_streak} дн.\n\n"
        f"Что делаем?",
        reply_markup=main_menu(
            MINI_APP_URL,
            level=user.level,
            xp=user.xp,
            streak=user.current_streak,
        ),
    )


@router.callback_query(F.data == "open_profile")
async def cb_open_profile(query: CallbackQuery) -> None:
    # реальный рендер профиля — в profile.py; здесь просто делегируем
    await query.answer()
    # импорт ленивый, чтобы избежать циклов при старте
    from .profile import render_profile

    await render_profile(query)
