@echo off
:: Запуск Telegram-бота Vocal Tamagotchi (Windows).
:: Двойной клик по файлу — бот стартует в venv.
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo [!] venv не найден. Создай: python -m venv .venv && .venv\Scripts\pip install -r requirements.txt
  pause
  exit /b 1
)
call .venv\Scripts\activate.bat
python main.py
pause
