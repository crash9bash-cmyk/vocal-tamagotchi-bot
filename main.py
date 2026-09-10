"""Точка входа бота (aiogram 3.x, async)."""
from __future__ import annotations

import asyncio

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BotCommand

from config import require_token
from db.session import init_db
from handlers import start, profile, lessons

BOT_COMMANDS = [
    BotCommand(command="start", description="Запустить бота / создать артиста"),
    BotCommand(command="profile", description="🎤 Твой артист (статы)"),
    BotCommand(command="lessons", description="📚 Уроки"),
]


async def main() -> None:
    token = require_token()
    bot = Bot(token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()

    # роутеры
    dp.include_router(start.router)
    dp.include_router(profile.router)
    dp.include_router(lessons.router)

    # БД
    await init_db()
    await bot.set_my_commands(BOT_COMMANDS)

    print("🚀 Vocal Tamagotchi bot started")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
