@echo off
title BudgetManage - Déploiement SharePoint Automatique
cls

echo ================================================
echo    BUDGETMANAGE - DÉPLOIEMENT SHAREPOINT
echo ================================================
echo.
echo 🚀 Déploiement automatique pour SharePoint Sync
echo 📦 Création package complet avec exécutable
echo.

REM Vérifier Python
python --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo ❌ Python non trouvé
    echo 💡 Installez Python depuis python.org
    pause
    exit /b 1
)

echo ✅ Python détecté
echo.

REM Lancer le script Python
echo 🔄 Lancement du déploiement automatique...
echo.
python deploy_sharepoint.py

if %ERRORLEVEL% equ 0 (
    echo.
    echo 🎉 DÉPLOIEMENT TERMINÉ AVEC SUCCÈS !
    echo.
    echo 📁 Fichiers créés:
    echo    - BudgetManage-SharePoint/ (dossier à uploader)
    echo    - BudgetManage-SharePoint-Ready.zip (package complet)
    echo.
    echo 🚀 Prochaines étapes:
    echo    1. Uploader BudgetManage-SharePoint/ sur SharePoint
    echo    2. Les utilisateurs double-cliquent sur start.bat
    echo.
    echo 💡 Le package est prêt pour SharePoint Sync !
) else (
    echo.
    echo ❌ ERREUR DURANT LE DÉPLOIEMENT
    echo 💡 Vérifiez les messages d'erreur ci-dessus
)

echo.
pause
