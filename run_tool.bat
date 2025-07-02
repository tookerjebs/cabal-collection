@echo off
cd /d "%~dp0"
call venv\Scripts\activate
python auto-collection\main.py
pause