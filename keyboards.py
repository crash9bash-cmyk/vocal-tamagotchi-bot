"""Inline-клавиатуры (по плану: Inline-кнопки для уроков/квизов)."""
from __future__ import annotations

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def main_menu() -> InlineKeyboardMarkup:
    """Кнопки под стартовым сообщением."""
    builder = InlineKeyboardBuilder()
    builder.button(text="🎤 Твой артист", callback_data="open_profile")
    builder.button(text="📚 Уроки", callback_data="open_lessons")
    builder.adjust(2)
    return builder.as_markup()


def units_menu(units: list[tuple[int, str, str | None, bool]]) -> InlineKeyboardMarkup:
    """units: (unit_id, title, description, unlocked)."""
    builder = InlineKeyboardBuilder()
    for uid, title, _desc, unlocked in units:
        label = f"🔒 {title}" if not unlocked else title
        builder.button(text=label, callback_data=f"unit:{uid}")
    builder.button(text="⬅️ Назад", callback_data="open_lessons")
    builder.adjust(1)
    return builder.as_markup()


def lessons_menu(lessons: list[tuple[int, str, bool]]) -> InlineKeyboardMarkup:
    """lessons: (lesson_id, title, completed)."""
    builder = InlineKeyboardBuilder()
    for lid, title, completed in lessons:
        mark = "✅ " if completed else ""
        builder.button(text=f"{mark}{title}", callback_data=f"lesson:{lid}")
    builder.button(text="⬅️ Назад", callback_data="back_to_units")
    builder.adjust(1)
    return builder.as_markup()


def quiz_options(lesson_id: int, options: list[str]) -> InlineKeyboardMarkup:
    """Варианты ответа на квиз (inline-кнопки)."""
    builder = InlineKeyboardBuilder()
    for idx, opt in enumerate(options):
        builder.button(text=opt, callback_data=f"quiz:{lesson_id}:{idx}")
    builder.adjust(1)
    return builder.as_markup()
