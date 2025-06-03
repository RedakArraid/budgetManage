#!/usr/bin/env python3
"""
🚀 BudgetManage - Déploiement Automatique SharePoint
Script d'automatisation complète pour déploiement SharePoint Sync
"""

import os
import sys
import subprocess
import platform
import shutil
import zipfile
from pathlib import Path
from datetime import datetime

class SharePointDeployer:
    def __init__(self):
        self.root_dir = Path(__file__).parent.absolute()
        self.is_windows = platform.system() == "Windows"
        self.sharepoint_dir = self.root_dir / "BudgetManage-SharePoint"
        
        print(f"🖥️  Plateforme: {platform.system()}")
        print(f"📁 Répertoire: {self.root_dir}")
    
    def check_dependencies(self):
        """Vérifier et installer les dépendances"""
        print("\n🔍 Vérification des dépendances...")
        
        required_packages = [
            "streamlit>=1.28.0", "pandas>=2.0.0", "bcrypt>=4.0.0",
            "plotly>=5.15.0", "openpyxl>=3.1.0", "python-dotenv>=1.0.0"
        ]
        
        if self.is_windows:
            required_packages.append("pyinstaller>=5.0.0")
        
        try:
            subprocess.run([
                sys.executable, "-m", "pip", "install", "--upgrade"
            ] + required_packages, check=True, capture_output=True)
            print("✅ Dépendances installées")
            return True
        except subprocess.CalledProcessError:
            print("❌ Erreur installation dépendances")
            return False
    
    def create_sharepoint_launcher(self):
        """Créer le script de lancement SharePoint"""
        print("📝 Création script de lancement...")
        
        launcher_content = '''@echo off
title BudgetManage - SharePoint Sync
cls

set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

echo ================================================
echo    BUDGETMANAGE v1.0.0
echo    Lancement depuis SharePoint Sync
echo ================================================
echo.

if not exist "BudgetManage.exe" (
    echo ❌ BudgetManage.exe introuvable
    echo 💡 Vérifiez que SharePoint est synchronisé
    pause
    exit /b 1
)

if not exist "data" mkdir "data"
if not exist "logs" mkdir "logs"

echo 🚀 Démarrage BudgetManage...
echo ⏱️  Patientez 15-30 secondes...
echo.

start /min "" BudgetManage.exe

timeout /t 8 /nobreak > nul
start http://localhost:8501

echo ✅ BudgetManage actif !
echo 🌐 URL: http://localhost:8501
echo 🔐 Connexion: admin@budget.com / admin123
echo.
echo 🛑 Pour arrêter: fermez cette fenêtre
echo.

:loop
timeout /t 30 /nobreak > nul
echo 🔄 Application active...
goto loop
'''
        
        launcher_path = self.sharepoint_dir / "start.bat"
        with open(launcher_path, 'w', encoding='utf-8') as f:
            f.write(launcher_content)
        
        print(f"✅ Script créé: {launcher_path}")
    
    def create_sharepoint_readme(self):
        """Créer la documentation SharePoint"""
        print("📝 Création documentation...")
        
        readme_content = f'''# 📁 BudgetManage - SharePoint Ready

## 🚀 Démarrage Ultra-Simple

1. **Double-cliquer** sur `start.bat`
2. **Attendre** 15-30 secondes  
3. **Le navigateur s'ouvre** automatiquement
4. **Se connecter** : admin@budget.com / admin123

## 📁 Contenu

```
📁 BudgetManage-SharePoint/
├── 🚀 start.bat              ← CLIQUER ICI
├── 💻 BudgetManage.exe        ← Application
├── 📖 README.md               ← Ce guide
├── 📁 data/                   ← Vos données (auto)
└── 📁 logs/                   ← Logs (auto)
```

## 🔄 SharePoint Sync

- ✅ **Mise à jour automatique** de l'application
- 💾 **Données locales** préservées
- 🔒 **Base privée** par utilisateur

## 🆘 Aide

- **Démarrage** : Double-clic `start.bat`
- **URL manuelle** : http://localhost:8501
- **Problème** : Fermer et relancer
- **Mot de passe oublié** : Supprimer dossier `data`

## 💡 Conseils

- Laissez `start.bat` ouvert pendant utilisation
- Changez le mot de passe admin après connexion
- Utilisez export Excel pour partager données

---
**Version** : {datetime.now().strftime("%Y.%m.%d")}  
**Prêt à utiliser !** 🎉
'''
        
        readme_path = self.sharepoint_dir / "README.md"
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        
        print(f"✅ Documentation créée: {readme_path}")
    
    def build_windows_executable(self):
        """Construire l'exécutable Windows"""
        if not self.is_windows:
            print("ℹ️  Pas sur Windows - Skip build exécutable")
            return None
        
        print("\n🏗️ Construction exécutable Windows...")
        
        # Nettoyer
        dist_dir = self.root_dir / "dist"
        build_dir = self.root_dir / "build"
        
        if dist_dir.exists():
            shutil.rmtree(dist_dir)
        if build_dir.exists():
            shutil.rmtree(build_dir)
        
        # Spec file simplifié
        spec_content = '''
import os, streamlit

a = Analysis(['main.py'], pathex=[os.getcwd()], binaries=[], 
    datas=[(os.path.join(os.path.dirname(streamlit.__file__), 'static'), 'streamlit/static'),
           (os.path.join(os.path.dirname(streamlit.__file__), 'runtime'), 'streamlit/runtime'),
           ('config', 'config'), ('models', 'models'), ('controllers', 'controllers'),
           ('services', 'services'), ('views', 'views'), ('utils', 'utils'),
           ('static', 'static'), ('migrations', 'migrations')],
    hiddenimports=['streamlit', 'streamlit.web.cli', 'validators', 'bcrypt', 
                  'plotly', 'pandas', 'openpyxl', 'sqlite3', 'dotenv'],
    excludes=['tkinter', 'matplotlib'])

exe = EXE(PYZ(a.pure, a.zipped_data), a.scripts, a.binaries, a.zipfiles, a.datas, [],
    name='BudgetManage', debug=False, strip=False, upx=True, console=True)
'''
        
        spec_path = self.root_dir / "auto.spec"
        with open(spec_path, 'w') as f:
            f.write(spec_content)
        
        try:
            subprocess.run(["pyinstaller", str(spec_path), "--clean", "--noconfirm"], 
                         check=True, cwd=self.root_dir)
            
            exe_path = dist_dir / "BudgetManage.exe"
            if exe_path.exists():
                size_mb = exe_path.stat().st_size / (1024 * 1024)
                print(f"✅ Exécutable créé: {size_mb:.1f} MB")
                return exe_path
        except subprocess.CalledProcessError:
            print("❌ Erreur build PyInstaller")
        finally:
            if spec_path.exists():
                spec_path.unlink()
        
        return None
    
    def create_sharepoint_package(self):
        """Créer le package SharePoint complet"""
        print("\n📦 Création package SharePoint...")
        
        # Nettoyer et créer dossier
        if self.sharepoint_dir.exists():
            shutil.rmtree(self.sharepoint_dir)
        self.sharepoint_dir.mkdir()
        
        # Construire exécutable Windows si possible
        if self.is_windows:
            exe_path = self.build_windows_executable()
            if exe_path:
                shutil.copy2(exe_path, self.sharepoint_dir / "BudgetManage.exe")
                print("✅ Exécutable copié")
            else:
                print("❌ Impossible de créer l'exécutable")
                return False
        else:
            # Placeholder pour build Windows
            placeholder = self.sharepoint_dir / "BUILD_ON_WINDOWS.txt"
            with open(placeholder, 'w') as f:
                f.write("""🪟 CONSTRUCTION WINDOWS REQUISE

Ce package a été préparé sur Mac/Linux.
Pour générer l'exécutable :

1. Git pull sur Windows
2. python deploy_sharepoint.py
3. L'exe sera créé automatiquement
""")
            print("ℹ️  Placeholder créé")
        
        # Créer scripts et docs
        self.create_sharepoint_launcher()
        self.create_sharepoint_readme()
        
        # Créer ZIP final
        zip_path = self.root_dir / "BudgetManage-SharePoint-Ready.zip"
        if zip_path.exists():
            zip_path.unlink()
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in self.sharepoint_dir.rglob('*'):
                if file_path.is_file():
                    arcname = file_path.relative_to(self.sharepoint_dir)
                    zipf.write(file_path, arcname)
        
        print(f"✅ Package créé: {zip_path}")
        return True
    
    def display_summary(self):
        """Afficher le résumé final"""
        print("\n" + "="*50)
        print("🎉 DÉPLOIEMENT SHAREPOINT TERMINÉ !")
        print("="*50)
        
        print("\n📁 Fichiers créés:")
        print("   📦 BudgetManage-SharePoint-Ready.zip")
        print("   📁 BudgetManage-SharePoint/")
        print("      ├── start.bat")
        print("      ├── README.md")
        
        if self.is_windows:
            print("      └── BudgetManage.exe")
        else:
            print("      └── BUILD_ON_WINDOWS.txt")
        
        print("\n🚀 Prochaines étapes:")
        print("   1. git add . && git commit -m 'SharePoint ready' && git push")
        print("   2. Uploader dossier BudgetManage-SharePoint/ sur SharePoint")
        print("   3. Utilisateurs: double-clic sur start.bat")
        
        if not self.is_windows:
            print("\n⚠️  Répéter sur Windows pour créer l'exécutable")
        
        print("\n✅ SharePoint Sync Ready! 🚀")

def main():
    """Fonction principale"""
    print("🚀 BudgetManage - Déploiement SharePoint Automatique")
    print("="*55)
    
    deployer = SharePointDeployer()
    
    try:
        # Vérifier dépendances
        if not deployer.check_dependencies():
            return 1
        
        # Créer package SharePoint
        if not deployer.create_sharepoint_package():
            return 1
        
        # Afficher résumé
        deployer.display_summary()
        return 0
        
    except KeyboardInterrupt:
        print("\n❌ Déploiement interrompu")
        return 1
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        return 1

if __name__ == "__main__":
    exit(main())
