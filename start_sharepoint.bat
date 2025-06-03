@echo off
title BudgetManage - Lancement depuis SharePoint
cls

REM Détection du répertoire SharePoint sync
set "CURRENT_DIR=%~dp0"
cd /d "%CURRENT_DIR%"

echo ================================================
echo    BUDGETMANAGE v1.0.0
echo    Lancement depuis SharePoint Sync
echo ================================================
echo.
echo 📁 Répertoire: %CURRENT_DIR%
echo 🔄 Statut SharePoint: Synchronisé
echo.

REM Vérifier si l'exécutable existe
if not exist "BudgetManage.exe" (
    echo ❌ Erreur: BudgetManage.exe non trouvé
    echo 💡 Vérifiez que SharePoint est bien synchronisé
    echo.
    pause
    exit /b 1
)

REM Créer le dossier data local si besoin
if not exist "data" (
    echo 📁 Création du dossier data local...
    mkdir "data"
)

REM Vérifier si le port 8501 est libre
echo 🔍 Vérification du port 8501...
netstat -an | find "8501" > nul
if %ERRORLEVEL% == 0 (
    echo ⚠️  Le port 8501 est déjà utilisé
    echo 💡 Une autre instance de BudgetManage est peut-être déjà lancée
    echo.
    set /p "CONTINUE=Continuer quand même ? (y/N): "
    if not "!CONTINUE!"=="y" if not "!CONTINUE!"=="Y" (
        echo ❌ Lancement annulé
        pause
        exit /b 1
    )
)

echo.
echo 🚀 Démarrage de BudgetManage...
echo.
echo ⏱️  Cela peut prendre 10-30 secondes...
echo 💡 Une fois démarré, votre navigateur s'ouvrira automatiquement
echo.
echo 🌐 URL d'accès: http://localhost:8501
echo 🔐 Connexion par défaut:
echo    Email: admin@budget.com
echo    Mot de passe: admin123
echo.
echo ⚠️  IMPORTANT: Changez le mot de passe après la première connexion !
echo.
echo 🛑 Pour arrêter l'application: Fermez cette fenêtre ou appuyez Ctrl+C
echo.
echo ================================================

REM Lancer l'application
echo ⏳ Lancement en cours...
start /min "BudgetManage" BudgetManage.exe

REM Attendre un peu puis ouvrir le navigateur
timeout /t 8 /nobreak > nul
echo 🌐 Ouverture du navigateur...
start http://localhost:8501

echo.
echo ✅ BudgetManage est maintenant accessible !
echo 📱 Si le navigateur ne s'est pas ouvert, allez sur: http://localhost:8501
echo.
echo 💡 Cette fenêtre peut rester ouverte (l'application tourne en arrière-plan)
echo 🛑 Pour arrêter complètement: fermez cette fenêtre
echo.

REM Garder la fenêtre ouverte
:loop
timeout /t 30 /nobreak > nul
echo 🔄 BudgetManage fonctionne... (Ctrl+C pour arrêter)
goto loop
