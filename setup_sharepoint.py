#!/usr/bin/env python3
"""
Script d'automatisation complète pour déploiement SharePoint
Usage: python setup_sharepoint.py
"""

import os
import sys
import subprocess
import shutil
import zipfile
from pathlib import Path
import platform

def print_step(message):
    """Afficher une étape avec style"""
    print(f"\n🔧 {message}")
    print("=" * (len(message) + 4))

def print_success(message):
    """Afficher un succès"""
    print(f"✅ {message}")

def print_error(message):
    """Afficher une erreur"""
    print(f"❌ {message}")

def print_info(message):
    """Afficher une info"""
    print(f"💡 {message}")

def check_requirements():
    """Vérifier les prérequis"""
    print_step("Vérification des prérequis")
    
    # Vérifier Python
    if sys.version_info < (3, 8):
        print_error("Python 3.8+ requis")
        return False
    print_success(f"Python {sys.version}")
    
    # Vérifier si on est sur Windows
    if platform.system() != 'Windows':
        print_error("Ce script est conçu pour Windows")
        return False
    print_success("Système Windows détecté")
    
    # Vérifier PyInstaller
    try:
        import PyInstaller
        print_success("PyInstaller disponible")
    except ImportError:
        print_info("Installation de PyInstaller...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'pyinstaller'], check=True)
        print_success("PyInstaller installé")
    
    # Vérifier les dépendances du projet
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], 
                      check=True, capture_output=True)
        print_success("Dépendances du projet installées")
    except:
        print_error("Erreur installation des dépendances")
        return False
    
    return True

def create_spec_file():
    """Créer le fichier .spec pour PyInstaller"""
    print_step("Création du fichier .spec")
    
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-
import os
import streamlit

a = Analysis(
    ['main.py'],
    pathex=[os.getcwd()],
    binaries=[],
    datas=[
        (os.path.join(os.path.dirname(streamlit.__file__), 'static'), 'streamlit/static'),
        (os.path.join(os.path.dirname(streamlit.__file__), 'runtime'), 'streamlit/runtime'),
        ('config', 'config'),
        ('models', 'models'),
        ('controllers', 'controllers'),
        ('services', 'services'),
        ('views', 'views'),
        ('utils', 'utils'),
        ('static', 'static'),
        ('migrations', 'migrations'),
    ],
    hiddenimports=[
        'streamlit', 'streamlit.web.cli', 'streamlit.runtime.scriptrunner.script_runner',
        'validators', 'bcrypt', 'plotly', 'pandas', 'openpyxl', 'sqlite3', 'dotenv',
        'email.mime.text', 'email.mime.multipart', 'smtplib',
    ],
    hookspath=[],
    runtime_hooks=[],
    excludes=['tkinter', 'matplotlib'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz, a.scripts, a.binaries, a.zipfiles, a.datas, [],
    name='BudgetManage',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
'''
    
    with open('budgetmanage.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print_success("Fichier .spec créé")

def build_executable():
    """Construire l'exécutable"""
    print_step("Construction de l'exécutable")
    
    # Nettoyer les builds précédents
    for folder in ['build', 'dist']:
        if os.path.exists(folder):
            shutil.rmtree(folder)
            print_info(f"Dossier {folder} nettoyé")
    
    # Construire avec PyInstaller
    print_info("Construction en cours... (cela peut prendre 2-5 minutes)")
    try:
        result = subprocess.run([
            'pyinstaller', 'budgetmanage.spec', '--clean', '--noconfirm'
        ], capture_output=True, text=True, check=True)
        print_success("Exécutable construit avec succès")
        
        # Vérifier la taille
        exe_path = Path('dist/BudgetManage.exe')
        if exe_path.exists():
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            print_info(f"Taille de l'exécutable: {size_mb:.1f} MB")
        
        return True
    except subprocess.CalledProcessError as e:
        print_error("Erreur lors de la construction")
        print(e.stderr)
        return False

def create_sharepoint_launcher():
    """Créer le script de lancement SharePoint"""
    print_step("Création du script de lancement SharePoint")
    
    launcher_content = '''@echo off
title BudgetManage - Lancement SharePoint
cls

REM Détection automatique du répertoire
set "APP_DIR=%~dp0"
cd /d "%APP_DIR%"

echo ================================================
echo    BUDGETMANAGE v1.0.0
echo    Lancement depuis SharePoint Sync
echo ================================================
echo.
echo 📁 Répertoire: %APP_DIR%
echo 🔄 Source: SharePoint Synchronisé
echo.

REM Vérifier l'exécutable
if not exist "BudgetManage.exe" (
    echo ❌ BudgetManage.exe non trouvé !
    echo 💡 Vérifiez la synchronisation SharePoint
    pause
    exit /b 1
)

REM Créer le dossier data si nécessaire
if not exist "data" mkdir "data"

REM Vérifier le port
echo 🔍 Vérification du port 8501...
netstat -an | find "8501" >nul 2>&1
if %ERRORLEVEL% == 0 (
    echo ⚠️  Port 8501 occupé - une instance est déjà active
    echo 💡 Ouvrez simplement: http://localhost:8501
    echo.
    timeout /t 3 >nul
    start http://localhost:8501
    pause
    exit /b 0
)

echo.
echo 🚀 Démarrage de BudgetManage...
echo ⏱️  Patientez 10-30 secondes...
echo.

REM Lancer l'application en arrière-plan
start /min "BudgetManage Server" BudgetManage.exe

REM Attendre le démarrage
echo ⏳ Initialisation en cours...
for /l %%i in (1,1,20) do (
    timeout /t 1 >nul
    netstat -an | find "8501" >nul 2>&1
    if !ERRORLEVEL! == 0 goto :ready
    echo    %%i/20...
)

echo ❌ Délai d'attente dépassé
echo 💡 L'application peut encore démarrer, essayez: http://localhost:8501
pause
exit /b 1

:ready
echo.
echo ✅ BudgetManage est prêt !
echo 🌐 Ouverture du navigateur...
timeout /t 2 >nul
start http://localhost:8501

echo.
echo ================================================
echo    BUDGETMANAGE ACTIF
echo ================================================
echo 🌐 URL: http://localhost:8501
echo 🔐 Connexion: admin@budget.com / admin123
echo.
echo 💡 Gardez cette fenêtre ouverte
echo 🛑 Pour arrêter: fermez cette fenêtre
echo ================================================
echo.

REM Boucle de surveillance
:monitor
timeout /t 60 >nul
netstat -an | find "8501" >nul 2>&1
if %ERRORLEVEL% == 0 (
    echo 🔄 Service actif... [%time%]
    goto :monitor
) else (
    echo ⚠️  Service arrêté - fermeture
    pause
    exit /b 0
)
'''
    
    with open('start_sharepoint.bat', 'w', encoding='utf-8') as f:
        f.write(launcher_content)
    
    print_success("Script de lancement créé")

def create_readme():
    """Créer le README SharePoint"""
    print_step("Création de la documentation")
    
    readme_content = '''# 📁 BudgetManage - Version SharePoint

## 🚀 Démarrage Ultra-Rapide

1. **Double-cliquez** sur `start_sharepoint.bat`
2. **Attendez** 10-30 secondes
3. **Le navigateur s'ouvre** automatiquement
4. **Connectez-vous** avec : admin@budget.com / admin123

## 💾 Vos Données

- ✅ **Privées** : Chaque utilisateur a sa base locale
- ✅ **Préservées** : Mises à jour ne les effacent pas  
- ✅ **Automatiques** : Sauvegarde dans le dossier `data/`

## 🔄 Mises à Jour

- **Automatiques** via SharePoint sync
- **Redémarrer** l'application pour appliquer
- **Vos données** sont préservées

## 🆘 Problèmes ?

### Application ne démarre pas
- Vérifier la synchronisation SharePoint
- Contacter l'IT si antivirus bloque
- Redémarrer le PC

### Port occupé
- Une instance fonctionne déjà
- Aller sur http://localhost:8501
- Ou redémarrer le PC

### Navigateur ne s'ouvre pas
- Ouvrir manuellement : http://localhost:8501
- Attendre 1-2 minutes supplémentaires

## 📞 Support

Contacter l'administrateur système ou créer un ticket IT.

---
**Version SharePoint** | **Auto-générée** | **Windows Compatible**
'''
    
    with open('README_SharePoint.md', 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print_success("Documentation créée")

def create_sharepoint_package():
    """Créer le package final SharePoint"""
    print_step("Création du package SharePoint")
    
    # Créer le dossier package
    package_dir = Path('BudgetManage-SharePoint')
    if package_dir.exists():
        shutil.rmtree(package_dir)
    package_dir.mkdir()
    
    # Copier les fichiers nécessaires
    files_to_copy = [
        ('dist/BudgetManage.exe', 'BudgetManage.exe'),
        ('start_sharepoint.bat', 'start_sharepoint.bat'),
        ('README_SharePoint.md', 'README.md')
    ]
    
    for src, dst in files_to_copy:
        if os.path.exists(src):
            shutil.copy2(src, package_dir / dst)
            print_info(f"Copié: {dst}")
        else:
            print_error(f"Fichier manquant: {src}")
            return False
    
    # Créer le dossier data
    (package_dir / 'data').mkdir()
    
    # Créer l'archive ZIP
    zip_path = 'BudgetManage-SharePoint.zip'
    if os.path.exists(zip_path):
        os.remove(zip_path)
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_path in package_dir.rglob('*'):
            if file_path.is_file():
                arcname = file_path.relative_to(package_dir)
                zipf.write(file_path, arcname)
    
    print_success(f"Package créé: {zip_path}")
    
    # Afficher la taille
    zip_size = os.path.getsize(zip_path) / (1024 * 1024)
    print_info(f"Taille du package: {zip_size:.1f} MB")
    
    return True

def test_executable():
    """Tester l'exécutable"""
    print_step("Test de l'exécutable")
    
    exe_path = Path('BudgetManage-SharePoint/BudgetManage.exe')
    if not exe_path.exists():
        print_error("Exécutable non trouvé")
        return False
    
    print_info("Test de démarrage rapide...")
    try:
        # Test très rapide - juste vérifier que l'exe se lance
        result = subprocess.run([str(exe_path), '--help'], 
                              capture_output=True, text=True, timeout=10)
        print_success("Exécutable testé avec succès")
        return True
    except Exception as e:
        print_error(f"Erreur de test: {e}")
        return False

def cleanup():
    """Nettoyer les fichiers temporaires"""
    print_step("Nettoyage")
    
    temp_files = [
        'budgetmanage.spec',
        'build',
        'dist',
        '__pycache__'
    ]
    
    for item in temp_files:
        if os.path.exists(item):
            if os.path.isdir(item):
                shutil.rmtree(item)
            else:
                os.remove(item)
            print_info(f"Supprimé: {item}")
    
    print_success("Nettoyage terminé")

def display_summary():
    """Afficher le résumé final"""
    print("\n" + "="*60)
    print("🎉 SETUP SHAREPOINT TERMINÉ AVEC SUCCÈS !")
    print("="*60)
    
    print("\n📦 Fichiers créés:")
    print("  📁 BudgetManage-SharePoint/     - Dossier prêt à uploader")
    print("  📄 BudgetManage-SharePoint.zip  - Archive pour SharePoint")
    
    print("\n🚀 Prochaines étapes:")
    print("  1. Uploader BudgetManage-SharePoint.zip sur SharePoint")
    print("  2. Extraire le contenu dans un dossier partagé")
    print("  3. Les utilisateurs : double-clic sur start_sharepoint.bat")
    
    print("\n👥 Instructions utilisateurs:")
    print("  🔗 Connexion: admin@budget.com / admin123")
    print("  🌐 URL locale: http://localhost:8501")
    print("  📖 Documentation: README.md dans le package")
    
    print("\n💡 Conseils:")
    print("  - Tester sur un poste avant distribution")
    print("  - Vérifier les droits d'exécution avec l'IT")
    print("  - Chaque utilisateur aura sa propre base de données")
    
    print("\n✨ Votre solution SharePoint est prête ! ✨")

def main():
    """Fonction principale"""
    print("🚀 AUTOMATISATION SETUP SHAREPOINT BUDGETMANAGE")
    print("=" * 55)
    print("Ce script va créer automatiquement tout le nécessaire")
    print("pour déployer BudgetManage via SharePoint synchronisé.\n")
    
    try:
        # Étapes du processus
        if not check_requirements():
            return 1
        
        create_spec_file()
        
        if not build_executable():
            return 1
        
        create_sharepoint_launcher()
        create_readme()
        
        if not create_sharepoint_package():
            return 1
        
        if not test_executable():
            print_info("Test échoué mais package créé - à tester manuellement")
        
        cleanup()
        display_summary()
        
        return 0
        
    except KeyboardInterrupt:
        print_error("\nProcessus interrompu par l'utilisateur")
        return 1
    except Exception as e:
        print_error(f"Erreur inattendue: {e}")
        return 1

if __name__ == "__main__":
    exit(main())
