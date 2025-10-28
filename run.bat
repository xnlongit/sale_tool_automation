@echo off
title ER Sports Automation Tool - Python GUI
echo.
echo ========================================
echo   ER Sports Automation Tool - Python GUI
echo ========================================
echo.
echo Kiem tra Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python khong duoc cai dat hoac khong co trong PATH
    echo Vui long cai dat Python tu https://python.org/
    pause
    exit /b 1
)

echo Python da duoc cai dat:
python --version

echo.
echo Kiem tra cac thu vien can thiet...
python -c "import selenium, webdriver_manager" >nul 2>&1
if %errorlevel% neq 0 (
    echo Cai dat cac thu vien can thiet...
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo ERROR: Khong the cai dat cac thu vien
        pause
        exit /b 1
    )
)

echo.
echo Khoi chay chuong trinh...
python src/main.py

if %errorlevel% neq 0 (
    echo.
    echo ERROR: Chuong trinh bi loi
    pause
)
