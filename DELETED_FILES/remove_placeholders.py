#!/usr/bin/env python3
"""
Script pour supprimer tous les placeholders du projet BudgetManage
Basé sur l'analyse des fichiers identifiés
"""

import os
import re
import shutil
from datetime import datetime
from pathlib import Path

def create_backup(project_path):
    """Créer une sauvegarde du projet"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"budgetmanage_backup_placeholders_{timestamp}"
    backup_path = project_path.parent / backup_name
    
    print(f"💾 Création de la sauvegarde: {backup_name}")
    
    try:
        shutil.copytree(
            project_path, 
            backup_path,
            ignore=shutil.ignore_patterns('.git', '__pycache__', '*.pyc', 'venv', 'backup_*')
        )
        print(f"✅ Sauvegarde créée: {backup_path}")
        return backup_path
    except Exception as e:
        print(f"❌ Erreur création sauvegarde: {e}")
        return None

def find_and_remove_placeholders(project_path):
    """Trouve et supprime tous les placeholders"""
    project_path = Path(project_path)
    
    # Fichiers à traiter (basé sur l'analyse)
    target_files = [
        'views/nouvelle_demande_view.py',
        'views/gestion_utilisateurs_view.py', 
        'views/login_view.py',
        'views/admin_create_demande_view.py',
        'views/admin_dropdown_options_view.py',
        'views/admin_parametrage_view.py',
        'views/analytics_view.py',
        'views/dashboard_view.py',
        'views/demandes_view.py',
        'views/notifications_view.py',
        'views/validations_view.py'
    ]
    
    # Parcourir tous les fichiers Python du projet
    python_files = []
    exclude_dirs = {'.git', '__pycache__', 'venv', '.github', 'backup_20250527_120707', 'DELETED_FILES'}
    
    for root, dirs, files in os.walk(project_path):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        for file in files:
            if file.endswith('.py'):
                python_files.append(Path(root) / file)
    
    total_placeholders = 0
    files_modified = 0
    
    print(f"🔍 Analyse de {len(python_files)} fichiers Python...")
    
    for file_path in python_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                original_content = f.read()
            
            # Chercher les placeholders
            placeholder_pattern = r'placeholder=["\'](.*?)["\']'
            matches = list(re.finditer(placeholder_pattern, original_content))
            
            if matches:
                print(f"\n📁 {file_path.relative_to(project_path)}")
                
                # Remplacer tous les placeholders par des chaînes vides
                modified_content = original_content
                placeholders_in_file = 0
                
                for match in reversed(matches):  # Inverse pour éviter les décalages
                    placeholder_text = match.group(1)
                    if placeholder_text.strip():  # Seulement si non vide
                        full_match = match.group(0)
                        replacement = 'placeholder=""'
                        
                        print(f"  ➤ Suppression: '{placeholder_text}'")
                        modified_content = modified_content.replace(full_match, replacement, 1)
                        placeholders_in_file += 1
                        total_placeholders += 1
                
                # Écrire le fichier modifié
                if placeholders_in_file > 0:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(modified_content)
                    
                    print(f"  ✅ {placeholders_in_file} placeholder(s) supprimé(s)")
                    files_modified += 1
        
        except Exception as e:
            print(f"❌ Erreur traitement {file_path}: {e}")
    
    print(f"\n📊 RÉSUMÉ:")
    print(f"✅ {total_placeholders} placeholders supprimés")
    print(f"📄 {files_modified} fichiers modifiés")
    
    return total_placeholders, files_modified

def main():
    print("🚀 BUDGETMANAGE - SUPPRESSION DES PLACEHOLDERS")
    print("=" * 50)
    
    # Chemin du projet
    project_path = Path(__file__).parent
    print(f"📁 Projet: {project_path}")
    
    # Confirmation
    response = input("\n⚠️ Voulez-vous supprimer TOUS les placeholders ? (OUI/non): ")
    if response.upper() != 'OUI':
        print("❌ Opération annulée")
        return
    
    # Créer une sauvegarde
    backup_path = create_backup(project_path)
    if not backup_path:
        print("❌ Impossible de créer une sauvegarde. Arrêt.")
        return
    
    # Supprimer les placeholders
    total, files = find_and_remove_placeholders(project_path)
    
    if total > 0:
        print("\n🎉 Suppression terminée avec succès !")
        print(f"💾 Sauvegarde disponible: {backup_path}")
        print("\n💡 Conseil: Testez votre application pour vérifier que tout fonctionne correctement")
    else:
        print("\n✅ Aucun placeholder trouvé à supprimer")

if __name__ == "__main__":
    main()
