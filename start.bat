@echo off
setlocal

cd /d "%~dp0"

where uv >nul 2>&1

if %errorlevel% equ 0 (
    if not exist ".venv\Scripts\python.exe" (
        uv venv .venv
        if errorlevel 1 exit /b 1
    )

    uv sync
    if errorlevel 1 exit /b 1
) else (
    if not exist ".venv\Scripts\python.exe" (
        python -m venv .venv
        if errorlevel 1 exit /b 1
    )

    ".venv\Scripts\python.exe" -m pip install --upgrade pip
    if errorlevel 1 exit /b 1

    if exist "requirements.txt" (
        ".venv\Scripts\python.exe" -m pip install -r requirements.txt
        if errorlevel 1 exit /b 1
    )
)

powershell.exe -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -Command "Start-Process -FilePath '.venv\Scripts\python.exe' -ArgumentList 'source\gui\main.py' -WorkingDirectory '%~dp0' -WindowStyle Hidden"

exit /b 0