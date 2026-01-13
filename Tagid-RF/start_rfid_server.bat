@echo off
cd /d "%~dp0"
echo Activating virtual environment...
call .venv\Scripts\activate.bat

echo Installing/Verifying dependencies in venv...
python -m pip install websockets wsproto uvicorn[standard]

cd be
echo Starting RFID Server...
python run_server.py
pause
