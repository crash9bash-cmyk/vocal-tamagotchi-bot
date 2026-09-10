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
`mini_app/index.html` — самодостаточная веб-страница в стиле **Game Boy / Tamagotchi**:
- **Game Boy DMG-палитра** (4 оттенка). Строго серую — замени массив `PAL` в `<script>`.
- **Персонаж в полный рост**, нарисован процедурно пиксель-пиксельно на canvas.
- **Сцена «студия»**: микрофон на стойке, зеркало, постер, растение.
- **Выбор пола** (♂ мальчик / ♀ девочка) — переключатель прямо в Mini App,
  хранится в `localStorage` (без привязки к БД).
- **Интерактив**: артист поёт (от микрофона летят ноты); за урок — звёзды;
  при новом уровне — прыжок от радости; при пропуске стрика — слёзы.
- Читает данные из URL query (`?level=..&xp=..&streak=..&tech=..&health=..&char=..&theory=..`)
  либо `Telegram.WebApp.initDataUnsafe.start_param`. Событие реакции — `?event=lesson_done|level_up|streak_lost`.

Локальный предпросмотр: открыть файл в браузере (можно передать query, напр.
`?level=5&xp=320&streak=4&event=level_up&gender=girl`). Для открытия из бота нужен
публичный HTTPS — задай `MINI_APP_URL` в `.env`, тогда в меню появится кнопка «🎨 Артист (Mini App)».

## Статус
Этап 0: окружение + схема БД + каркас бота + контент (5 юнитов / 25 уроков / 75 квизов)
+ Mini App визуал артиста (GB-стиль, полный рост, студия, выбор пола, интерактив).
Дальше: запуск бота с токеном и публикация Mini App (HTTPS).
