"""Точка входа бота (aiogram 3.x, async)."""
from __future__ import annotations

import asyncio
import os
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BotCommand

from config import require_token
from db.session import init_db
from handlers import start, profile, lessons


def _start_health_server() -> None:
    """Railway/Render выдают $PORT и ждут, что web-сервис слушает его.

    Бот использует long polling (реального HTTP нет), поэтому поднимаем
    минимальный health-эндпоинт, чтобы деплой считался здоровым.
    Локально $PORT обычно не задан — сервер не стартует.
    """
    port = os.getenv("PORT")
    if not port:
        return

    class _H(BaseHTTPRequestHandler):
        def do_GET(self) -> None:  # noqa: N802
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write(b"Vocal Tamagotchi bot is alive")

        def log_message(self, *args) -> None:  # noqa: A002
            pass

    srv = ThreadingHTTPServer(("0.0.0.0", int(port)), _H)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    print(f"🩺 health server on :{port}")

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

    # health-сервер (только на хостинге, где задан $PORT)
    _start_health_server()

    print("🚀 Vocal Tamagotchi bot started")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
