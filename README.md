# Vocal Tamagotchi — Telegram-бот

Вокальный тамагочи-дуолинго: пользователь растит начинающего вокалиста в звезду.
Обучение пению через игровой цикл (юниты, квизы, аудио, XP, стрики).

## Стек
- Python 3.13
- aiogram 3.x (Telegram)
- SQLAlchemy 2.0 + aiosqlite (SQLite, v1)
- Telegram Mini App (позже, для визуала)

## Структура
```
bot/
├── main.py            # точка входа: bot + dispatcher
├── config.py          # настройки (токен из .env)
├── db/
│   ├── models.py      # SQLAlchemy-модели
│   └── session.py     # async engine + sessionmaker
├── handlers/
│   ├── start.py       # /start — регистрация
│   ├── profile.py     # /profile — «Твой артист»
│   └── lessons.py     # /lessons — «Уроки»
└── keyboards.py       # inline-кнопки
```

## Запуск (разработка)
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env   # вписать BOT_TOKEN
python main.py
```

## Статус
Этап 0: окружение + схема БД + каркас бота.
