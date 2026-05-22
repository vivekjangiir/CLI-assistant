@echo off
setlocal

echo.
echo  ================================================
echo    Personal CLI Assistant  ^|  One-time Setup
echo  ================================================
echo.

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo  [ERROR] Python not found. Install it from https://python.org
    pause & exit /b 1
)

:: Install dependencies
echo  [1/3] Installing Python packages...
pip install -r "%~dp0requirements.txt" --quiet
if errorlevel 1 (
    echo  [ERROR] pip install failed. Try running this script as Administrator.
    pause & exit /b 1
)
echo         Done.

:: Create a wrapper batch file so you can type  "ai"  from anywhere
set WRAPPER=%USERPROFILE%\AppData\Local\Microsoft\WindowsApps\ai.bat
echo  [2/3] Creating global command "ai" ...
(
    echo @echo off
    echo python "%~dp0assistant.py" %%*
) > "%WRAPPER%"
echo         Created: %WRAPPER%

:: Done
echo.
echo  [3/3] Almost there! Set your free Groq API key:
echo.
echo    ai config --api-key YOUR_GROQ_KEY
echo.
echo  Then try:
echo    ai ask "What's the latest in AI?"
echo    ai chat
echo    ai todo add "Buy groceries"
echo    ai --help
echo.
echo  Get a free key at: https://console.groq.com
echo.
pause
