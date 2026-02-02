@echo off
REM KisanSeva Startup Script for Windows

echo ========================================
echo    KisanSeva - ML Crop Detector
echo ========================================
echo.

REM Check if venv exists
if not exist "agri_ai_env" (
    echo ERROR: Virtual environment not found!
    echo Please ensure 'agri_ai_env' folder exists
    pause
    exit /b 1
)

REM Activate virtual environment
call agri_ai_env\Scripts\activate.bat

REM Check if dependencies are installed
python -c "import flask" >nul 2>&1
if errorlevel 1 (
    echo Installing required packages...
    pip install -r requirements.txt
)

REM Start backend
echo.
echo Starting Backend Server...
echo.
echo ✓ Backend: http://localhost:5000
echo ✓ Health Check: http://localhost:5000/health
echo.
echo Keep this window open while using the app.
echo Close to stop the backend.
echo.
echo NOTE: Open another terminal and run 'npm run dev' to start frontend
echo.

python backend.py
pause
