#!/usr/bin/env python3
"""
Script de setup développement pour BudgetManage
Configure l'environnement de développement local
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def check_python_version():
    """Vérifier la version de Python"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ requis")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
    return True

def install_dependencies():
    """Installer les dépendances"""
    print("📦 Installation des dépendances...")
    
    try:
        # Mise à jour pip
        subprocess.run([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'], 
                      check=True, capture_output=True)
        
        # Installation des requirements
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], 
                      check=True, capture_output=True)
        
        # Dépendances de développement
        dev_packages = [
            'pytest>=7.0.0',
            'pytest-cov>=4.0.0',
            'pytest-mock>=3.10.0',
            'black>=23.0.0',
            'flake8>=6.0.0',
            'mypy>=1.0.0',
            'pre-commit>=3.0.0'
        ]
        
        subprocess.run([sys.executable, '-m', 'pip', 'install'] + dev_packages, 
                      check=True, capture_output=True)
        
        print("✅ Dépendances installées")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur installation: {e}")
        return False

def setup_environment():
    """Configurer l'environnement"""
    print("⚙️ Configuration de l'environnement...")
    
    # Créer .env s'il n'existe pas
    env_file = Path('.env')
    env_template = Path('.env.template')
    
    if not env_file.exists() and env_template.exists():
        print("📄 Création du fichier .env...")
        with open(env_template, 'r') as template:
            with open(env_file, 'w') as env:
                env.write(template.read())
        print("✅ Fichier .env créé depuis le template")
        print("⚠️ Pensez à configurer vos paramètres email dans .env")
    
    # Créer les dossiers nécessaires
    dirs_to_create = ['logs', 'uploads', 'backup', 'data']
    for dir_name in dirs_to_create:
        dir_path = Path(dir_name)
        if not dir_path.exists():
            dir_path.mkdir(exist_ok=True)
            print(f"📁 Dossier {dir_name}/ créé")
    
    return True

def setup_database():
    """Initialiser la base de données"""
    print("💾 Initialisation de la base de données...")
    
    try:
        # Importer et initialiser la base
        sys.path.append(os.getcwd())
        from models.database import db
        
        db.init_database()
        print("✅ Base de données initialisée")
        return True
        
    except Exception as e:
        print(f"❌ Erreur base de données: {e}")
        return False

def setup_git_hooks():
    """Configurer les hooks Git (pre-commit)"""
    print("🔧 Configuration des hooks Git...")
    
    try:
        # Initialiser pre-commit si .pre-commit-config.yaml existe
        if Path('.pre-commit-config.yaml').exists():
            subprocess.run(['pre-commit', 'install'], check=True, capture_output=True)
            print("✅ Hooks pre-commit configurés")
        else:
            print("ℹ️ Pas de configuration pre-commit trouvée")
        return True
        
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("⚠️ pre-commit non disponible (optionnel)")
        return True

def test_installation():
    """Tester l'installation"""
    print("🧪 Test de l'installation...")
    
    try:
        # Test d'import des modules principaux
        sys.path.append(os.getcwd())
        
        from config.settings import app_config
        from models.database import db
        from controllers.auth_controller import AuthController
        
        print("✅ Imports principaux OK")
        
        # Test de démarrage Streamlit (mode test)
        result = subprocess.run([
            sys.executable, '-c', 
            "import streamlit; print('Streamlit OK')"
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✅ Streamlit OK")
        else:
            print("⚠️ Problème avec Streamlit")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        return False

def show_next_steps():
    """Afficher les prochaines étapes"""
    print("\n" + "="*50)
    print("🎉 Setup terminé avec succès !")
    print("="*50)
    
    print("\n📋 Prochaines étapes :")
    print("1. 📝 Configurer .env avec vos paramètres email")
    print("2. 🚀 Démarrer l'app: streamlit run main.py")
    print("3. 🌐 Ouvrir: http://localhost:8501")
    print("4. 🔐 Connexion: admin@budget.com / admin123")
    
    print("\n🛠️ Commandes utiles :")
    print("- Tests: python -m pytest")
    print("- Linting: black . && flake8 .")
    print("- Build Windows: python scripts/build_windows.py")
    print("- Docker: docker-compose up")
    
    print("\n📚 Documentation :")
    print("- README.md : Guide complet")
    print("- GitHub : https://github.com/RedakArraid/budgetManage")

def main():
    """Fonction principale"""
    print("🔧 Setup Développement BudgetManage")
    print("=" * 40)
    print(f"🖥️ OS: {platform.system()} {platform.release()}")
    
    # Étapes de setup
    steps = [
        ("Vérification Python", check_python_version),
        ("Installation dépendances", install_dependencies),
        ("Configuration environnement", setup_environment),
        ("Initialisation base de données", setup_database),
        ("Configuration Git hooks", setup_git_hooks),
        ("Test de l'installation", test_installation),
    ]
    
    for step_name, step_func in steps:
        print(f"\n📋 {step_name}...")
        if not step_func():
            print(f"❌ Échec: {step_name}")
            print("🛑 Setup interrompu")
            return 1
    
    show_next_steps()
    return 0

if __name__ == '__main__':
    exit(main())
