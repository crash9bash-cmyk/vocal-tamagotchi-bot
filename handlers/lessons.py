"""Экран «Уроки» + FSM прохождения урока.

Поток (по плану 1.2): теория → квиз → аудиопример → начисление XP.
На этом этапе контент в БД пустой — хендлеры готовы, но покажут
«контент готовится». Наполнение юнитами — отдельная задача.
"""
from __future__ import annotations

import json

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery

from db.session import SessionLocal
from db.models import (
    Unit,
    Lesson,
    QuizQuestion,
    AudioExample,
    User,
    UserProgress,
    UserStats,
)
from config import XP_PER_LESSON
from keyboards import units_menu, lessons_menu, quiz_options, main_menu

router = Router()


class LessonFlow(StatesGroup):
    """Состояния прохождения одного урока."""

    theory = State()
    quiz = State()
    audio = State()


# --- /lessons ---------------------------------------------------------------
@router.message(Command("lessons"))
async def cmd_lessons(message: Message) -> None:
    await _show_units(message)


async def _show_units(target: Message | CallbackQuery) -> None:
    async with SessionLocal() as session:
        units = (await session.execute(Unit.__table__.select().order_by(Unit.order))).scalars().all()
    if not units:
        text = "📚 Уроки готовятся — контент появится скоро!"
        if isinstance(target, Message):
            await target.answer(text, reply_markup=main_menu())
        else:
            await target.message.edit_text(text, reply_markup=main_menu())
        return

    rows = [(u.id, u.title, u.description, True) for u in units]
    if isinstance(target, Message):
        await target.answer("Выбери юнит:", reply_markup=units_menu(rows))
    else:
        await target.message.edit_text("Выбери юнит:", reply_markup=units_menu(rows))


# --- навигация по юнитам/урокам --------------------------------------------
@router.callback_query(F.data == "open_lessons")
async def cb_open_lessons(query: CallbackQuery) -> None:
    await query.answer()
    await _show_units(query)


@router.callback_query(F.data == "back_to_units")
async def cb_back_to_units(query: CallbackQuery) -> None:
    await query.answer()
    await _show_units(query)


@router.callback_query(F.data.startswith("unit:"))
async def cb_unit(query: CallbackQuery) -> None:
    await query.answer()
    unit_id = int(query.data.split(":")[1])
    async with SessionLocal() as session:
        lessons = (
            await session.execute(
                Lesson.__table__.select()
                .where(Lesson.unit_id == unit_id)
                .order_by(Lesson.order)
            )
        ).scalars().all()
        # какие уроки уже пройдены этим юзером
        done = set(
            r[0]
            for r in (
                await session.execute(
                    UserProgress.__table__.select()
                    .where(UserProgress.user_id == query.from_user.id)
                    .with_only_columns(UserProgress.lesson_id)
                )
            ).all()
        )
    rows = [(l.id, l.title, l.id in done) for l in lessons]
    await query.message.edit_text(
        "Уроки юнита:", reply_markup=lessons_menu(rows)
    )


@router.callback_query(F.data.startswith("lesson:"))
async def cb_lesson(query: CallbackQuery, state: FSMContext) -> None:
    await query.answer()
    lesson_id = int(query.data.split(":")[1])
    async with SessionLocal() as session:
        lesson = await session.get(Lesson, lesson_id)
        if lesson is None:
            await query.message.answer("Урок не найден.")
            return
        quiz = (
            await session.execute(
                QuizQuestion.__table__.select().where(QuizQuestion.lesson_id == lesson_id)
            )
        ).scalars().all()
        audio = (
            await session.execute(
                AudioExample.__table__.select().where(AudioExample.lesson_id == lesson_id)
            )
        ).scalars().all()

    # показываем теорию
    await query.message.edit_text(f"📖 <b>{lesson.title}</b>\n\n{lesson.theory_text}")

    if quiz:
        await state.update_data(lesson_id=lesson_id, quiz_index=0, quiz_total=len(quiz))
        await state.set_state(LessonFlow.quiz)
        await _ask_quiz(query, lesson_id, 0, quiz[0])
    else:
        # нет квиза — сразу к аудио/завершению
        await _finish_lesson(query, lesson_id, audio, state)


# --- квиз --------------------------------------------------------------------
async def _ask_quiz(query: CallbackQuery, lesson_id: int, idx: int, q: QuizQuestion) -> None:
    options = json.loads(q.options)
    await query.message.answer(
        f"❓ Вопрос {idx + 1}:\n{q.question_text}",
        reply_markup=quiz_options(lesson_id, options),
    )


@router.callback_query(F.data.startswith("quiz:"), LessonFlow.quiz)
async def cb_quiz(query: CallbackQuery, state: FSMContext) -> None:
    await query.answer()
    _, lesson_id_s, chosen_s = query.data.split(":")
    lesson_id = int(lesson_id_s)
    chosen = int(chosen_s)

    data = await state.get_data()
    idx = data.get("quiz_index", 0)
    total = data.get("quiz_total", 1)

    async with SessionLocal() as session:
        q = (
            await session.execute(
                QuizQuestion.__table__.select()
                .where(QuizQuestion.lesson_id == lesson_id)
                .order_by(QuizQuestion.id)
            )
        ).scalars().all()[idx]
        correct = chosen == q.correct_option
        audio = (
            await session.execute(
                AudioExample.__table__.select().where(AudioExample.lesson_id == lesson_id)
            )
        ).scalars().all()

    await query.message.answer("✅ Верно!" if correct else "❌ Не совсем. Подсказка есть в теории.")

    if idx + 1 < total:
        await state.update_data(quiz_index=idx + 1)
        await _ask_quiz(query, lesson_id, idx + 1,
                        (await _quiz_at(lesson_id, idx + 1)))
    else:
        await _finish_lesson(query, lesson_id, audio, state)


async def _quiz_at(lesson_id: int, idx: int) -> QuizQuestion:
    async with SessionLocal() as session:
        rows = (
            await session.execute(
                QuizQuestion.__table__.select()
                .where(QuizQuestion.lesson_id == lesson_id)
                .order_by(QuizQuestion.id)
            )
        ).scalars().all()
    return rows[idx]


# --- завершение урока + начисление XP ---------------------------------------
async def _finish_lesson(
    query: CallbackQuery, lesson_id: int, audio: list[AudioExample], state: FSMContext
) -> None:
    # аудиопример (если есть file_id)
    for ex in audio:
        if ex.file_id:
            await query.message.answer_audio(ex.file_id, caption=ex.description or "🎧 Аудиопример")

    # начисляем XP + прогресс (idempotent: один урок — одна запись)
    async with SessionLocal() as session:
        user = await session.get(User, query.from_user.id)
        if user is None:
            # на всякий случай — если /start не было
            user = User(telegram_id=query.from_user.id, username=query.from_user.username)
            session.add(user)
            await session.flush()
            session.add(UserStats(user_id=user.id))

        existing = (
            await session.execute(
                UserProgress.__table__.select()
                .where(UserProgress.user_id == user.id)
                .where(UserProgress.lesson_id == lesson_id)
            )
        ).scalar_one_or_none()

        if existing is None:
            xp_gain = XP_PER_LESSON
            user.xp += xp_gain
            # простой пересчёт уровня
            while user.xp >= user.level * 100:
                user.xp -= user.level * 100
                user.level += 1
            session.add(UserProgress(user_id=user.id, lesson_id=lesson_id, score=1.0))
            await session.commit()
            msg = f"🎉 Урок пройден! +{xp_gain} XP · Уровень {user.level}"
        else:
            msg = "Урок уже пройден ранее — повторно XP не начисляем."

    await state.clear()
    await query.message.answer(msg, reply_markup=main_menu())
