"""Экран «Твой артист» — /profile и render_profile (для callback)."""
from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

from db.session import SessionLocal
from db.models import User, UserStats
from keyboards import main_menu

router = Router()


def _format(user: User, stats: UserStats | None) -> str:
    s = stats or UserStats()
    return (
        f"🎤 <b>Твой артист</b>\n\n"
        f"Уровень: {user.level}   XP: {user.xp}\n"
        f"🔥 Стрик: {user.current_streak} дн.\n\n"
        f"<b>Статы:</b>\n"
        f"🎶 Вокальная техника: {s.vocal_technique:.0f}\n"
        f"💚 Здоровье голоса:   {s.voice_health:.0f}\n"
        f"✨ Харизма:           {s.charisma:.0f}\n"
        f"👂 Муз. теория/слух:  {s.music_theory:.0f}\n"
    )


async def _load(user_id: int):
    async with SessionLocal() as session:
        user = await session.get(User, user_id)
        stats = await session.get(UserStats, user_id) if user else None
    return user, stats


@router.message(Command("profile"))
async def cmd_profile(message: Message) -> None:
    user, stats = await _load(message.from_user.id)
    if user is None:
        await message.answer("Сначала нажми /start, чтобы создать артиста.")
        return
    await message.answer(_format(user, stats), reply_markup=main_menu())


async def render_profile(query: CallbackQuery) -> None:
    """Вызывается из стартового меню по callback open_profile."""
    user, stats = await _load(query.from_user.id)
    if user is None:
        await query.message.answer("Сначала нажми /start.")
        return
    await query.message.edit_text(_format(user, stats), reply_markup=main_menu())
