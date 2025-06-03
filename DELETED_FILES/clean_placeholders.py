#!/usr/bin/env python3
"""
Script spécialisé pour supprimer les placeholders identifiés dans BudgetManage
Basé sur l'analyse manuelle des fichiers principaux
"""

import os
import shutil
from datetime import datetime
from pathlib import Path

def create_specific_backup(project_path):
    """Créer une sauvegarde des fichiers spécifiques"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = project_path / f"backup_placeholders_{timestamp}"
    backup_dir.mkdir(exist_ok=True)
    
    print(f"💾 Création sauvegarde spécifique: {backup_dir.name}")
    return backup_dir

def remove_placeholders_specific():
    """Supprimer les placeholders identifiés spécifiquement"""
    
    # Définir le chemin du projet
    project_path = Path(__file__).parent
    
    # Fichiers et leurs placeholders spécifiques identifiés
    placeholder_modifications = {
        'views/nouvelle_demande_view.py': [
            ('placeholder="Ex: Agence Paris Centre"', 'placeholder=""'),
            ('placeholder="Ex: Salon du Marketing 2024"', 'placeholder=""'),
            ('placeholder="Ex: Entreprise ABC"', 'placeholder=""'),
            ('placeholder="Ex: Paris, France"', 'placeholder=""'),
            ('placeholder="Nom de l\'enseigne ou client"', 'placeholder=""'),
            ('placeholder="Nom du contact"', 'placeholder=""'),
            ('placeholder="contact@email.com"', 'placeholder=""'),
            ('placeholder="Informations complémentaires, justifications..."', 'placeholder=""'),
        ],
        'views/gestion_utilisateurs_view.py': [
            ('placeholder="Nom, prénom, email..."', 'placeholder=""'),
            ('placeholder="utilisateur@entreprise.com"', 'placeholder=""'),
            ('placeholder="Dupont"', 'placeholder=""'),
            ('placeholder="Jean"', 'placeholder=""'),
        ],
        'views/login_view.py': [
            ('placeholder="votre@email.com"', 'placeholder=""'),
        ]
    }
    
    print("🎯 SUPPRESSION CIBLÉE DES PLACEHOLDERS")
    print("=" * 50)
    
    # Créer une sauvegarde
    backup_dir = create_specific_backup(project_path)
    
    total_modifications = 0
    files_modified = 0
    
    for file_path, modifications in placeholder_modifications.items():
        full_path = project_path / file_path
        
        if not full_path.exists():
            print(f"⚠️ Fichier non trouvé: {file_path}")
            continue
        
        print(f"\n📁 Traitement: {file_path}")
        
        try:
            # Lire le contenu original
            with open(full_path, 'r', encoding='utf-8') as f:
                original_content = f.read()
            
            # Sauvegarder l'original
            backup_file = backup_dir / full_path.name
            with open(backup_file, 'w', encoding='utf-8') as f:
                f.write(original_content)
            
            # Appliquer les modifications
            modified_content = original_content
            file_modifications = 0
            
            for old_placeholder, new_placeholder in modifications:
                if old_placeholder in modified_content:
                    modified_content = modified_content.replace(old_placeholder, new_placeholder)
                    print(f"  ✅ Modifié: {old_placeholder}")
                    file_modifications += 1
                    total_modifications += 1
                else:
                    print(f"  ⚠️ Non trouvé: {old_placeholder}")
            
            # Écrire le fichier modifié si des changements ont été faits
            if file_modifications > 0:
                with open(full_path, 'w', encoding='utf-8') as f:
                    f.write(modified_content)
                
                print(f"  📊 {file_modifications} modification(s) appliquée(s)")
                files_modified += 1
            else:
                print(f"  ℹ️ Aucune modification nécessaire")
        
        except Exception as e:
            print(f"❌ Erreur traitement {file_path}: {e}")
    
    print(f"\n📊 RÉSUMÉ FINAL:")
    print(f"✅ {total_modifications} placeholders supprimés")
    print(f"📄 {files_modified} fichiers modifiés")
    print(f"💾 Sauvegarde: {backup_dir}")
    
    return total_modifications > 0

def scan_all_placeholders():
    """Scanner tous les fichiers pour identifier d'autres placeholders"""
    project_path = Path(__file__).parent
    
    print("🔍 SCAN COMPLET DES PLACEHOLDERS")
    print("=" * 50)
    
    exclude_dirs = {'.git', '__pycache__', 'venv', '.github', 'backup_20250527_120707', 'DELETED_FILES'}
    found_placeholders = []
    
    for root, dirs, files in os.walk(project_path):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        
        for file in files:
            if file.endswith('.py'):
                file_path = Path(root) / file
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        lines = content.split('\n')
                        
                        for line_num, line in enumerate(lines, 1):
                            if 'placeholder=' in line and '""' not in line:
                                # Extraire le placeholder
                                import re
                                match = re.search(r'placeholder=["\'](.*?)["\']', line)
                                if match and match.group(1).strip():
                                    found_placeholders.append({
                                        'file': str(file_path.relative_to(project_path)),
                                        'line': line_num,
                                        'placeholder': match.group(1),
                                        'context': line.strip()
                                    })
                
                except Exception as e:
                    pass
    
    if found_placeholders:
        print(f"📋 {len(found_placeholders)} placeholder(s) trouvé(s):")
        
        current_file = None
        for ph in found_placeholders:
            if ph['file'] != current_file:
                current_file = ph['file']
                print(f"\n📁 {current_file}")
                print("-" * 40)
            
            print(f"  Ligne {ph['line']}: '{ph['placeholder']}'")
            print(f"    └─ {ph['context']}")
    else:
        print("✅ Aucun placeholder trouvé dans le projet")
    
    return found_placeholders

def main():
    print("🚀 BUDGETMANAGE - NETTOYAGE DES PLACEHOLDERS")
    print("=" * 60)
    
    while True:
        print("\n🎯 OPTIONS DISPONIBLES:")
        print("1. Supprimer les placeholders identifiés")
        print("2. Scanner tous les placeholders du projet") 
        print("3. Les deux (scan + suppression)")
        print("0. Quitter")
        
        choice = input("\nVotre choix (0-3): ").strip()
        
        if choice == '1':
            # Confirmation
            response = input("\n⚠️ Confirmer la suppression des placeholders ? (OUI/non): ")
            if response.upper() == 'OUI':
                success = remove_placeholders_specific()
                if success:
                    print("\n🎉 Placeholders supprimés avec succès !")
                    print("💡 Testez votre application pour vérifier le bon fonctionnement")
                else:
                    print("\n⚠️ Aucune modification effectuée")
            else:
                print("❌ Opération annulée")
        
        elif choice == '2':
            placeholders = scan_all_placeholders()
            if placeholders:
                print(f"\n💡 Utilisez l'option 1 pour supprimer les placeholders identifiés")
        
        elif choice == '3':
            print("\n🔍 Étape 1: Scan complet")
            placeholders = scan_all_placeholders()
            
            if placeholders:
                response = input(f"\n⚠️ {len(placeholders)} placeholder(s) trouvé(s). Les supprimer ? (OUI/non): ")
                if response.upper() == 'OUI':
                    success = remove_placeholders_specific()
                    if success:
                        print("\n🎉 Nettoyage terminé !")
                    
                    # Re-scanner pour vérifier
                    print("\n🔍 Vérification post-suppression:")
                    remaining = scan_all_placeholders()
                    if not remaining:
                        print("✅ Tous les placeholders ont été supprimés !")
                else:
                    print("❌ Suppression annulée")
            else:
                print("✅ Projet déjà propre, aucun placeholder trouvé")
        
        elif choice == '0':
            print("👋 Au revoir !")
            break
        
        else:
            print("❌ Choix invalide. Veuillez sélectionner 0-3.")

if __name__ == "__main__":
    main()
