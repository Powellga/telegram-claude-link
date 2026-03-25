@echo off
cd /d "%~dp0"
echo.
echo Starting Telegram Authentication...
echo.
call .venv\Scripts\activate.bat
python auth_telegram.py
echo.
echo ========================================
echo If you see errors above, please screenshot them.
echo ========================================
echo.
pause
