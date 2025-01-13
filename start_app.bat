@echo off
REM Navigate to your project directory
cd /d "C:\Users\Researcher\Downloads\Hardware_seesaw\ServerPC"

REM Activate the virtual environment
call myenv\Scripts\activate

REM Run your Python script
python hardware_server.py

REM Keep the window open to show messages
pause
