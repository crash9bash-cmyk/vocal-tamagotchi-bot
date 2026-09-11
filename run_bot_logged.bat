@echo off
:: Запуск бота с логом (для автозапуска/диагностики). Пишет всё в bot_run.log.
cd /d "%~dp0"
echo [%date% %time%] START >> bot_run.log
".venv\Scripts\python.exe" main.py >> bot_run.log 2>&1
echo [%date% %time%] EXIT code=%errorlevel% >> bot_run.log
