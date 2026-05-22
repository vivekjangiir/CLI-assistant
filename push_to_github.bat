@echo off
setlocal
cd /d "%~dp0"

echo.
echo  ================================================
echo    Pushing CLI Assistant to GitHub
echo  ================================================
echo.

:: Check git
git --version >nul 2>&1
if errorlevel 1 (
    echo  [ERROR] Git not found.
    echo  Download from: https://git-scm.com/download/win
    pause & exit /b 1
)

:: Init repo if not already one
if not exist ".git" (
    echo  [1/4] Initialising git repo...
    git init -b main
    git config user.email "vivekjangiid@gmail.com"
    git config user.name "vivekjangiir"
) else (
    echo  [1/4] Git repo already initialised.
)

:: Stage everything (except .env thanks to .gitignore)
echo  [2/4] Staging files...
git add .

:: Commit
echo  [3/4] Committing...
git commit -m "🤖 Personal CLI Assistant by @vivekjangiir" 2>nul || (
    echo         Nothing new to commit - already up to date.
)

:: Set remote and push
echo  [4/4] Pushing to GitHub...
git remote remove origin 2>nul
git remote add origin https://github.com/vivekjangiir/CLI-assistant.git
git branch -M main
git push -u origin main

if errorlevel 1 (
    echo.
    echo  [NOTE] If asked for credentials:
    echo    Username: vivekjangiir
    echo    Password: use a Personal Access Token
    echo    Create one at: https://github.com/settings/tokens
    echo    (select repo scope)
) else (
    echo.
    echo  ✓ Successfully pushed!
    echo  View: https://github.com/vivekjangiir/CLI-assistant
)

echo.
pause
