@echo off
title RehabQuest Dashboard
cd /d "%~dp0"
if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
    python app\main.py
) else (
    python app\main.py
)
pause
