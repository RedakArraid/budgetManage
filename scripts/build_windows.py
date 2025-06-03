#!/usr/bin/env python3
"""
Script de build Windows pour BudgetManage
Crée un exécutable Windows portable avec PyInstaller
"""

import os
import sys
import subprocess
import shutil
import platform
from pathlib import Path

def check_requirements():
    """Vérifier que les dépendances sont installées"""
    try:
        import streamlit
        import PyInstaller
        print("✅ Streamlit et PyInstaller sont installés")
        return True
    except ImportError as e:
        print(f"❌ Dépendance manquante: {e}")
        print("Installation: pip install streamlit pyinstaller")
        return False

def create_spec_file():
    """Créer le fichier .spec pour PyInstaller"""
    
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-
import os
import streamlit
from pathlib import Path

# Chemins
streamlit_path = os.path.dirname(streamlit.__file__)
project_path = os.getcwd()

a = Analysis(
    ['main.py'],
    pathex=[project_path],
    binaries=[],
    datas=[
        (os.path.join(streamlit_path, 'static'), 'streamlit/static'),
        (os.path.join(streamlit_path, 'runtime'), 'streamlit/runtime'),
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
        'streamlit',
        'streamlit.web.cli',
        'streamlit.runtime.scriptrunner.script_runner',
        'streamlit.runtime.state',
        'streamlit.runtime.caching',
        'validators',
        'bcrypt',
        'plotly',
        'pandas',
        'openpyxl',
        'sqlite3',
        'python-dotenv',
        'email.mime.text',
        'email.mime.multipart',
        'smtplib',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter', 'matplotlib'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
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
    icon='docs/icon.ico' if os.path.exists('docs/icon.ico') else None,
)
'''
    
    with open('budgetmanage.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print("✅ Fichier .spec créé")

def build_executable():
    """Construire l'exécutable avec PyInstaller"""
    print("🏗️ Construction de l'exécutable...")
    
    try:
        # Nettoyer les builds précédents
        if os.path.exists('build'):
            shutil.rmtree('build')
        if os.path.exists('dist'):
            shutil.rmtree('dist')
        
        # Construire
        result = subprocess.run([
            'pyinstaller', 'budgetmanage.spec', '--clean', '--noconfirm'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Exécutable créé avec succès")
            return True
        else:
            print(f"❌ Erreur lors de la construction: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def create_portable_package():
    """Créer le package portable"""
    print("📦 Création du package portable...")
    
    # Créer le dossier portable
    portable_dir = Path('BudgetManage-Portable')
    if portable_dir.exists():
        shutil.rmtree(portable_dir)
    
    portable_dir.mkdir()
    
    # Copier l'exécutable
    exe_path = Path('dist/BudgetManage.exe')
    if exe_path.exists():
        shutil.copy2(exe_path, portable_dir / 'BudgetManage.exe')
        print("✅ Exécutable copié")
    else:
        print("❌ Exécutable non trouvé")
        return False
    
    # Créer le script de démarrage
    start_script = portable_dir / 'start.bat'
    with open(start_script, 'w', encoding='utf-8') as f:
        f.write('''@echo off
title BudgetManage - Système de Gestion Budget
echo.
echo ==================================
echo    BUDGETMANAGE v2.0
echo    Système de Gestion Budget
echo ==================================
echo.
echo Démarrage en cours...
echo.
echo Après démarrage, ouvrez votre navigateur sur:
echo.
echo    http://localhost:8501
echo.
echo Connexion par défaut:
echo   Email: admin@budget.com
echo   Mot de passe: admin123
echo.
echo Appuyez sur Ctrl+C pour arrêter l'application
echo.
BudgetManage.exe
pause
''')
    
    # Créer le README
    readme_path = portable_dir / 'README.md'
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write('''# BudgetManage - Version Portable

## 🚀 Démarrage Rapide

1. Double-cliquez sur `start.bat`
2. Attendez que l'application démarre
3. Ouvrez votre navigateur sur http://localhost:8501

## 🔐 Connexion par Défaut

- **Email**: admin@budget.com
- **Mot de passe**: admin123

⚠️ **Important**: Changez le mot de passe après la première connexion !

## 📋 Fonctionnalités

- Gestion des demandes budgétaires
- Workflow de validation hiérarchique
- Notifications automatiques
- Analytics et rapports
- Gestion des utilisateurs

## 🆘 Support

- Documentation: https://github.com/RedakArraid/budgetManage
- Issues: https://github.com/RedakArraid/budgetManage/issues
''')
    
    print("✅ Package portable créé")
    return True

def get_exe_info():
    """Afficher les informations sur l'exécutable"""
    exe_path = Path('dist/BudgetManage.exe')
    if exe_path.exists():
        size_mb = exe_path.stat().st_size / (1024 * 1024)
        print(f"📊 Taille de l'exécutable: {size_mb:.1f} MB")
        
        # Test rapide
        print("🧪 Test de l'exécutable...")
        try:
            result = subprocess.run(
                [str(exe_path), '--help'], 
                capture_output=True, 
                text=True, 
                timeout=10
            )
            if result.returncode == 0:
                print("✅ Exécutable testé avec succès")
            else:
                print("⚠️ Test de l'exécutable avec avertissement")
        except Exception as e:
            print(f"⚠️ Impossible de tester l'exécutable: {e}")
    else:
        print("❌ Exécutable non trouvé")

def main():
    """Fonction principale"""
    print("🪟 Build Windows BudgetManage")
    print("=" * 40)
    
    # Vérifications
    if platform.system() != 'Windows':
        print("⚠️ Ce script est optimisé pour Windows")
        print("Vous pouvez continuer, mais certaines fonctionnalités peuvent ne pas marcher")
    
    if not check_requirements():
        return 1
    
    # Étapes de build
    steps = [
        ("Création du fichier .spec", create_spec_file),
        ("Construction de l'exécutable", build_executable),
        ("Création du package portable", create_portable_package),
        ("Informations sur l'exécutable", get_exe_info),
    ]
    
    for step_name, step_func in steps:
        print(f"\n📋 {step_name}...")
        if not step_func():
            print(f"❌ Échec de l'étape: {step_name}")
            return 1
    
    print("\n🎉 Build terminé avec succès !")
    print("📁 Fichiers créés:")
    print("  - dist/BudgetManage.exe")
    print("  - BudgetManage-Portable/ (dossier complet)")
    print("\n💡 Pour distribuer: compressez le dossier BudgetManage-Portable")
    
    return 0

if __name__ == '__main__':
    exit(main())
