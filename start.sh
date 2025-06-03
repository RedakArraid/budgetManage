#!/bin/bash

echo "🚀 DÉMARRAGE BUDGETMANAGE - ARCHITECTURE MVC"
echo "============================================="

# Vérifier si Python est installé
if ! command -v python &> /dev/null; then
    echo "❌ Python n'est pas installé ou pas dans le PATH"
    echo "💡 Installez Python 3.8+ puis relancez ce script"
    exit 1
fi

echo "✅ Python détecté: $(python --version)"

# Vérifier si les dépendances sont installées
echo "🔍 Vérification des dépendances..."

if python -c "import streamlit" 2>/dev/null; then
    echo "✅ Streamlit installé"
else
    echo "📦 Installation des dépendances..."
    pip install -r requirements.txt
fi

# Vérifier les autres dépendances importantes
echo "🔍 Vérification dépendances complètes..."
python -c "
try:
    import pandas, bcrypt, plotly, openpyxl
    print('✅ Toutes les dépendances sont installées')
except ImportError as e:
    print(f'❌ Dépendance manquante: {e}')
    print('📦 Installation en cours...')
    import subprocess
    subprocess.run(['pip', 'install', '-r', 'requirements.txt'])
"

# Menu principal
echo ""
echo "🎯 CHOISISSEZ VOTRE ACTION:"
echo "1. 🚀 Démarrer l'application (RECOMMANDÉ)"
echo "2. 🔧 Configurer l'environnement"
echo "3. 🗄️ Initialiser la base de données"
echo "4. 📊 Vérifier l'installation"
echo "5. 🧹 Nettoyer les fichiers temporaires"
echo ""

read -p "Votre choix (1-5): " choice

case $choice in
    1)
        echo "🚀 Démarrage de BudgetManage..."
        echo "📍 URL: http://localhost:8501"
        echo "👤 Admin par défaut: admin@budget.com / admin123"
        echo ""
        streamlit run main.py
        ;;
    2)
        echo "🔧 Configuration de l'environnement..."
        if [ ! -f .env ]; then
            echo "📝 Création du fichier .env..."
            cp .env.template .env
            echo "✅ Fichier .env créé. Éditez-le avec vos paramètres."
        else
            echo "✅ Fichier .env déjà existant"
        fi
        echo "💡 Éditez le fichier .env pour configurer l'email"
        ;;
    3)
        echo "🗄️ Initialisation de la base de données..."
        python -c "
from models.database import db
db.init_database()
print('✅ Base de données initialisée')
"
        ;;
    4)
        echo "📊 Vérification de l'installation..."
        python -c "
import sys
import os
print('🐍 Python:', sys.version)
print('📁 Répertoire:', os.getcwd())

# Vérifier la structure
required_dirs = ['config', 'models', 'views', 'controllers', 'services', 'utils', 'static']
for dir_name in required_dirs:
    if os.path.exists(dir_name):
        print(f'✅ {dir_name}/')
    else:
        print(f'❌ {dir_name}/ manquant')

# Vérifier les fichiers principaux
required_files = ['main.py', 'requirements.txt', '.env.template']
for file_name in required_files:
    if os.path.exists(file_name):
        print(f'✅ {file_name}')
    else:
        print(f'❌ {file_name} manquant')

print('✅ Vérification terminée')
"
        ;;
    5)
        echo "🧹 Nettoyage des fichiers temporaires..."
        # Supprimer les fichiers __pycache__
        find . -name '__pycache__' -type d -exec rm -rf {} + 2>/dev/null || true
        # Supprimer les fichiers .pyc
        find . -name '*.pyc' -delete 2>/dev/null || true
        # Supprimer les .DS_Store
        find . -name '.DS_Store' -delete 2>/dev/null || true
        echo "✅ Nettoyage terminé"
        ;;
    *)
        echo "❌ Choix invalide"
        echo "💡 Relancez le script et choisissez 1-5"
        ;;
esac

echo ""
echo "📚 Pour plus d'aide, consultez README.md"
echo "🌟 Version 2.0 - Architecture MVC"
