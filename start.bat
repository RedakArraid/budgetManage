@echo off
echo 🚀 DÉMARRAGE BUDGETMANAGE - ARCHITECTURE MVC
echo =============================================

REM Vérifier si Python est installé
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python n'est pas installé ou pas dans le PATH
    echo 💡 Installez Python 3.8+ puis relancez ce script
    pause
    exit /b 1
)

echo ✅ Python détecté
python --version

REM Vérifier si les dépendances sont installées
echo 🔍 Vérification des dépendances...

python -c "import streamlit" >nul 2>&1
if errorlevel 1 (
    echo 📦 Installation des dépendances...
    pip install -r requirements.txt
) else (
    echo ✅ Streamlit installé
)

REM Vérifier les autres dépendances
echo 🔍 Vérification dépendances complètes...
python -c "try: import pandas, bcrypt, plotly, openpyxl; print('✅ Toutes les dépendances sont installées'); except ImportError as e: print(f'❌ Dépendance manquante: {e}'); import subprocess; subprocess.run(['pip', 'install', '-r', 'requirements.txt'])"

echo.
echo 🎯 CHOISISSEZ VOTRE ACTION:
echo 1. 🚀 Démarrer l'application (RECOMMANDÉ)
echo 2. 🔧 Configurer l'environnement
echo 3. 🗄️ Initialiser la base de données
echo 4. 📊 Vérifier l'installation
echo 5. 🧹 Nettoyer les fichiers temporaires
echo.

set /p choice=Votre choix (1-5): 

if "%choice%"=="1" (
    echo 🚀 Démarrage de BudgetManage...
    echo 📍 URL: http://localhost:8501
    echo 👤 Admin par défaut: admin@budget.com / admin123
    echo.
    streamlit run main.py
    goto end
)

if "%choice%"=="2" (
    echo 🔧 Configuration de l'environnement...
    if not exist .env (
        echo 📝 Création du fichier .env...
        copy .env.template .env
        echo ✅ Fichier .env créé. Éditez-le avec vos paramètres.
    ) else (
        echo ✅ Fichier .env déjà existant
    )
    echo 💡 Éditez le fichier .env pour configurer l'email
    goto end
)

if "%choice%"=="3" (
    echo 🗄️ Initialisation de la base de données...
    python -c "from models.database import db; db.init_database(); print('✅ Base de données initialisée')"
    goto end
)

if "%choice%"=="4" (
    echo 📊 Vérification de l'installation...
    python -c "import sys; import os; print('🐍 Python:', sys.version); print('📁 Répertoire:', os.getcwd()); required_dirs = ['config', 'models', 'views', 'controllers', 'services', 'utils', 'static']; [print(f'✅ {d}/') if os.path.exists(d) else print(f'❌ {d}/ manquant') for d in required_dirs]; required_files = ['main.py', 'requirements.txt', '.env.template']; [print(f'✅ {f}') if os.path.exists(f) else print(f'❌ {f} manquant') for f in required_files]; print('✅ Vérification terminée')"
    goto end
)

if "%choice%"=="5" (
    echo 🧹 Nettoyage des fichiers temporaires...
    REM Supprimer les fichiers __pycache__
    for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"
    REM Supprimer les fichiers .pyc
    del /s /q *.pyc >nul 2>&1
    echo ✅ Nettoyage terminé
    goto end
)

echo ❌ Choix invalide
echo 💡 Relancez le script et choisissez 1-5

:end
echo.
echo 📚 Pour plus d'aide, consultez README.md
echo 🌟 Version 2.0 - Architecture MVC
pause
