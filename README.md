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

## Наполнение контентом
`seed_content.py` заливает первые 5 юнитов (дыхание, слух/интервалы, ритм,
резонаторы, базовая теория), по 5 уроков, 3 квиз-вопроса и аудио-заглушке на урок.
Идемпотентно — повторный запуск не дублирует.
```bash
python seed_content.py
```

## Mini App «Твой артист» (визуал)
`mini_app/index.html` — самодостаточная веб-страница: персонаж рисуется
процедурно пиксель-пиксельно на canvas (ретро-тамагочи), панель статов,
уровень/XP/стрик, эмоции (радость/грусть/гордость). Читает данные из
URL query (`?level=..&xp=..&streak=..&tech=..&health=..&char=..&theory=..`)
либо из `Telegram.WebApp.initDataUnsafe.start_param`.

Локальный предпросмотр: открыть файл в браузере (передав query-параметры).
Для открытия из бота нужен публичный HTTPS — задай `MINI_APP_URL` в `.env`,
тогда в меню появится кнопка «🎨 Артист (Mini App)».

## Статус
Этап 0: окружение + схема БД + каркас бота + контент (5 юнитов / 25 уроков / 75 квизов)
+ Mini App визуал артиста. Дальше: запуск бота с токеном и публикация Mini App (HTTPS).
