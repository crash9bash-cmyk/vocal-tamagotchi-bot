"""Единая логика прогресса: XP, уровень, стрик.

Модель — КУМУЛЯТИВНАЯ: user.xp только растёт, уровень выводится из него.
Так работают пороги комнат в Mini App (TIERS: 100 / 500 / 2000 XP) —
поэтому residual-модель (списание XP при апгрейде) здесь не годится.

Используется и уроками (handlers/lessons.py), и голосовой игрой
(handlers/voice.py), чтобы прогресс считался одинаково.
"""
from __future__ import annotations

import datetime as dt

from config import XP_PER_LEVEL
from db.models import User


def level_for_xp(xp: int) -> int:
    """Уровень по накопленному XP (1 + каждые XP_PER_LEVEL)."""
    return max(1, xp // XP_PER_LEVEL + 1)


def apply_activity(user: User, xp_gain: int, today: dt.date | None = None) -> dict:
    """Начислить XP за активность, пересчитать уровень и стрик.

    Стрик:
      - первый раз / был перерыв > 1 дня  -> 1
      - уже занимался сегодня             -> без изменений
      - занимался вчера                   -> +1

    Возвращает dict со сводкой (для сообщений пользователю).
    """
    today = today or dt.date.today()
    old_level = user.level

    user.xp += max(0, xp_gain)
    user.level = level_for_xp(user.xp)

    last = user.last_active
    if last is None:
        user.current_streak = 1
    elif last == today:
        pass
    elif last == today - dt.timedelta(days=1):
        user.current_streak = (user.current_streak or 0) + 1
    else:
        user.current_streak = 1
    user.last_active = today

    return {
        "xp_gain": xp_gain,
        "xp": user.xp,
        "level": user.level,
        "leveled_up": user.level > old_level,
        "streak": user.current_streak,
    }
