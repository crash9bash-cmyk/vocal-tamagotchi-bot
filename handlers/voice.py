"""Обработка результатов v2-тренировки голоса из Mini App.

Mini App (игра «Спой ноту») по завершении шлёт данные через
WebApp.sendData(JSON), Telegram доставляет их боту как Message с
web_app_data. Здесь начисляем XP и поднимаем вокальную технику.
"""
from __future__ import annotations

import json

from aiogram import Router, F
from aiogram.types import Message

from sqlalchemy import select

from db.session import SessionLocal
from db.models import User, UserStats
from config import XP_PER_LESSON

router = Router()

# 5 XP за каждое попадание в ноту (чуть щедрее урока, но голос — сложнее)
XP_PER_HIT = 5
# сколько пунктов техники даёт одно попадание (до 100)
TECH_PER_HIT = 2


@router.message(F.web_app_data)
async def on_voice_report(message: Message) -> None:
    raw = message.web_app_data.data
    try:
        data = json.loads(raw)
    except (ValueError, TypeError):
        return

    if data.get("type") != "pitch":
        return

    hits = max(0, int(data.get("hits", 0) or 0))
    rounds = max(0, int(data.get("rounds", 0) or 0))

    if hits <= 0:
        await message.answer(
            "🎤 Тренировка записана, но попаданий пока нет — ещё чуть-чуть, и попадёшь!"
        )
        return

    tg_id = message.from_user.id
    async with SessionLocal() as session:
        user = (
            await session.execute(select(User).where(User.telegram_id == tg_id))
        ).scalar_one_or_none()
        if user is None:
            await message.answer("Сначала нажми /start, чтобы создать артиста.")
            return

        xp_gain = hits * XP_PER_HIT
        user.xp += xp_gain
        # пересчёт уровня (каждые XP_PER_LEVEL очков = +1 уровень, от 1)
        user.level = max(1, user.xp // XP_PER_LESSON + 1)

        stats = await session.get(UserStats, user.id)
        if stats is None:
            stats = UserStats(user_id=user.id)
            session.add(stats)
        stats.vocal_technique = min(100.0, stats.vocal_technique + hits * TECH_PER_HIT)

        await session.commit()

        await message.answer(
            f"🎤 Молодец! Попал в ноту <b>{hits}</b> раз"
            + (f" из {rounds}" if rounds else "")
            + f".\n+{xp_gain} XP, вокальная техника ↑\nУровень: {user.level}"
        )
