"""SQLAlchemy-модели (SQLAlchemy 2.0 style, async-ready).

Схема v1 из плана:
  users, units, lessons, quiz_questions, audio_examples,
  user_progress, user_stats
"""
from __future__ import annotations

import datetime as _dt

from sqlalchemy import (
    ForeignKey,
    Integer,
    String,
    DateTime,
    Date,
    Float,
    UniqueConstraint,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
)


class Base(DeclarativeBase):
    """Общий базовый класс для всех моделей."""


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    telegram_id: Mapped[int] = mapped_column(Integer, unique=True, index=True)
    username: Mapped[str | None] = mapped_column(String(64), nullable=True)
    created_at: Mapped[_dt.datetime] = mapped_column(
        DateTime, default=_dt.datetime.utcnow
    )
    current_streak: Mapped[int] = mapped_column(Integer, default=0)
    xp: Mapped[int] = mapped_column(Integer, default=0)
    level: Mapped[int] = mapped_column(Integer, default=1)
    # дата последней активности (для расчёта стрика); None = ещё не занимался
    last_active: Mapped[_dt.date | None] = mapped_column(Date, nullable=True)

    # relations
    progress: Mapped[list["UserProgress"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    stats: Mapped["UserStats | None"] = relationship(
        back_populates="user", cascade="all, delete-orphan", uselist=False
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<User telegram_id={self.telegram_id} lvl={self.level} xp={self.xp}>"


class Unit(Base):
    __tablename__ = "units"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(128))
    order: Mapped[int] = mapped_column(Integer, unique=True, index=True)
    description: Mapped[str | None] = mapped_column(String(512), nullable=True)

    lessons: Mapped[list["Lesson"]] = relationship(
        back_populates="unit", cascade="all, delete-orphan"
    )


class Lesson(Base):
    __tablename__ = "lessons"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    unit_id: Mapped[int] = mapped_column(ForeignKey("units.id"), index=True)
    title: Mapped[str] = mapped_column(String(128))
    order: Mapped[int] = mapped_column(Integer, index=True)
    theory_text: Mapped[str] = mapped_column(String(4000))

    unit: Mapped["Unit"] = relationship(back_populates="lessons")
    quiz: Mapped[list["QuizQuestion"]] = relationship(
        back_populates="lesson", cascade="all, delete-orphan"
    )
    audio: Mapped[list["AudioExample"]] = relationship(
        back_populates="lesson", cascade="all, delete-orphan"
    )


class QuizQuestion(Base):
    __tablename__ = "quiz_questions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    lesson_id: Mapped[int] = mapped_column(ForeignKey("lessons.id"), index=True)
    question_text: Mapped[str] = mapped_column(String(512))
    # JSON-список вариантов ответа, напр. ["A", "B", "C"]
    options: Mapped[str] = mapped_column(String(2000))
    # индекс правильного варианта в options (0-based)
    correct_option: Mapped[int] = mapped_column(Integer)

    lesson: Mapped["Lesson"] = relationship(back_populates="quiz")


class AudioExample(Base):
    __tablename__ = "audio_examples"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    lesson_id: Mapped[int] = mapped_column(ForeignKey("lessons.id"), index=True)
    # Telegram file_id — после первой загрузки переиспользуется без трафика
    file_id: Mapped[str] = mapped_column(String(256))
    description: Mapped[str | None] = mapped_column(String(256), nullable=True)

    lesson: Mapped["Lesson"] = relationship(back_populates="audio")


class UserProgress(Base):
    __tablename__ = "user_progress"
    __table_args__ = (UniqueConstraint("user_id", "lesson_id", name="uq_user_lesson"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    lesson_id: Mapped[int] = mapped_column(ForeignKey("lessons.id"), index=True)
    completed_at: Mapped[_dt.datetime] = mapped_column(
        DateTime, default=_dt.datetime.utcnow
    )
    score: Mapped[float] = mapped_column(Float, default=0.0)

    user: Mapped["User"] = relationship(back_populates="progress")


class UserStats(Base):
    """Числовые статы артиста. Растут при прохождении уроков."""

    __tablename__ = "user_stats"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), primary_key=True
    )
    vocal_technique: Mapped[float] = mapped_column(Float, default=0.0)
    voice_health: Mapped[float] = mapped_column(Float, default=0.0)
    charisma: Mapped[float] = mapped_column(Float, default=0.0)
    music_theory: Mapped[float] = mapped_column(Float, default=0.0)

    user: Mapped["User"] = relationship(back_populates="stats")
