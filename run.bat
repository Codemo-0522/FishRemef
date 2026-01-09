@echo off
chcp 65001 >nul
echo ================================================
echo  Modern Batch File Renamer
echo ================================================
echo.

REM Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo [INFO] Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment. Please ensure Python is installed and in your PATH.
        pause
        exit /b
    )
    echo [DONE] Virtual environment created.
    echo.
)

REM Activate virtual environment
echo [INFO] Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies from requirements.txt
echo [INFO] Checking and installing dependencies from requirements.txt...
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple --default-timeout=300
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies.
    pause
    exit /b
)

echo [DONE] All dependencies are ready.
echo.
echo [INFO] Starting the application...
echo.

REM Start the application
python main.py

pause
