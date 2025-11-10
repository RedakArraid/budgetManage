@echo off
title Installation BudgetManage
echo ================================================
echo    BUDGETMANAGE - Installation Automatique
echo ================================================
echo.

REM Créer le dossier temporaire
set TEMP_DIR=%USERPROFILE%\BudgetManageTemp
if not exist "%TEMP_DIR%" mkdir "%TEMP_DIR%"

echo 📥 Téléchargement de BudgetManage...
powershell -Command "& {Invoke-WebRequest -Uri 'https://github.com/RedakArraid/budgetManage/releases/latest/download/BudgetManage-Windows-Portable.zip' -OutFile '%TEMP_DIR%\BudgetManage.zip'}"

if not exist "%TEMP_DIR%\BudgetManage.zip" (
    echo ❌ Erreur de téléchargement
    pause
    exit /b 1
)

echo 📂 Extraction en cours...
powershell -Command "& {Expand-Archive -Path '%TEMP_DIR%\BudgetManage.zip' -DestinationPath '%TEMP_DIR%\BudgetManage' -Force}"

echo 🚀 Lancement de BudgetManage...
cd /d "%TEMP_DIR%\BudgetManage"
start BudgetManage.exe

echo ✅ BudgetManage démarré !
echo 🌐 Ouvrez votre navigateur sur: http://localhost:8501
echo 🔐 Connexion: admin@budget.com / admin123
echo.
echo 💡 Cette fenêtre peut être fermée
pause
