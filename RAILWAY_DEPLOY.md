# Деплой бота на Railway (работает 24/7, вне твоего ПК)

Код бота уже в публичном репозитории:
**https://github.com/crash9bash-cmyk/vocal-tamagotchi-bot** (ветка `main`).

## Что уже настроено в коде
- `Procfile` → `web: python main.py` (Railway запускает именно так).
- `requirements.txt` → aiogram, SQLAlchemy, aiosqlite, asyncpg, python-dotenv.
- `db/session.py` → берёт переменную `DATABASE_URL` (Postgres на хостинге) либо
  фоллбэк на локальный SQLite. `postgres://` автоматически приводится к
  `postgresql+asyncpg://`.
- `main.py` → поднимает health-сервер на `$PORT` (Railway требует, чтобы web-сервис
  слушал порт, иначе деплой считается «упавшим») и авто-наполняет БД контентом
  через `seed()` (идемпотентно — дублей при рестартах нет).
- `runtime.txt` → `python-3.13.0` (версия совпадает с локальной).

> Секреты (.env, data/) в репозиторий не попадают — они в .gitignore.

## Шаги в дашборде Railway
1. Зайди на **railway.app** → **Login** → вход через GitHub (дай доступ к репозиториям).
2. **New Project** → **Deploy from GitHub repo** → выбери `vocal-tamagotchi-bot`.
3. Дождись, пока сервис появится, зайди в него → вкладка **Variables**.
4. Добавь переменные:
   - `BOT_TOKEN` = `<токен от @BotFather>` (например `8983…:AAE…`)
   - `MINI_APP_URL` = `https://crash9bash-cmyk.github.io/vocal-tamagotchi-web/`
5. В проекте **New → Database → Postgres**. Railway сам подставит переменную
   `DATABASE_URL` в сервис бота.
   - Если `DATABASE_URL` в сервисе бота не появился автоматически — добавь вручную:
     `DATABASE_URL` = `${{Postgres.DATABASE_URL}}`.
6. Нажми **Deploy** (или просто подожди — Railway соберётся сам после подключения репо).
   Каждый последующий пуш в `main` = авто-редеплой.

## Как понять, что всё завелось
В логах сервиса (вкладка Deploy → Logs) должно появиться примерно:
```
🩺 health server on :<PORT>
🚀 Vocal Tamagotchi bot started
✅ Seed готов: юнитов=N, уроков=M, квиз-вопросов=K
```
Бот в Telegram сразу отвечает на /start.

## Важные нюансы
- **Останови локального бота** (`run_bot.bat` / `python main.py` на Windows). Два
  экземпляра с одним `BOT_TOKEN` одновременно делают long polling → Telegram убивает
  одного с ошибкой `Conflict: terminated by other getUpdates`. Пока бот на Railway —
  локальный не запускай.
- **Контент** (уроки/квизы) правится в `seed_content.py`. После пуша в `main` Railway
  пересоберётся; новые юниты добавятся (старые не дублируются).
- **База** живёт в Railway Postgres (не на твоём диске) — при удалении Postgres-сервиса
  данные пропадут. Делай бэкап при необходимости.

## Если деплой «красный»
- `ModuleNotFoundError` при сборке → проверь, что `requirements.txt` на месте в корне
  репо (он там).
- Бот падает сразу после старта → сверь `BOT_TOKEN` и `MINI_APP_URL` в Variables.
- Health-check не проходит → убедись, что сервис типа `web` (Procfile `web: ...`),
  тогда `$PORT` задан и health-сервер стартует.
