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


# Пороги комнат — СИНХРОНИЗИРОВАНЫ с Mini App (TIERS в mini_app/index.html).
# (название, minXP, minStreak)
TIERS: list[tuple[str, int, int]] = [
    ("🏠 Своя комната", 0, 0),
    ("🎼 Репетиционная", 100, 3),
    ("🎧 Студия", 500, 7),
    ("🏆 Топ-студия", 2000, 14),
]


def tier_index(xp: int, streak: int) -> int:
    """Индекс текущей комнаты (та же логика, что tierFromData в Mini App)."""
    tier = 0
    for i, (_name, min_xp, min_streak) in enumerate(TIERS):
        if xp >= min_xp or streak >= min_streak:
            tier = i
    return tier


def next_tier(xp: int, streak: int) -> dict | None:
    """Инфо о следующей комнате или None, если уже максимум."""
    tier = tier_index(xp, streak)
    if tier >= len(TIERS) - 1:
        return None
    name, min_xp, min_streak = TIERS[tier + 1]
    return {
        "name": name,
        "xp_left": max(0, min_xp - xp),
        "streak_left": max(0, min_streak - streak),
    }


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
