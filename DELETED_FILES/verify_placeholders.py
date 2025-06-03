#!/usr/bin/env python3
"""
Script de vérification des placeholders dans BudgetManage
Vérifie que tous les placeholders ont bien été supprimés
"""

import os
import re
from pathlib import Path
from datetime import datetime

def verify_placeholders():
    """Vérifier l'état des placeholders dans le projet"""
    
    project_path = Path(__file__).parent
    
    print("🔍 VÉRIFICATION DES PLACEHOLDERS")
    print("=" * 50)
    print(f"📁 Projet: {project_path}")
    
    # Fichiers à vérifier en priorité
    priority_files = [
        'views/nouvelle_demande_view.py',
        'views/gestion_utilisateurs_view.py',
        'views/login_view.py',
        'views/admin_create_demande_view.py',
        'views/admin_dropdown_options_view.py'
    ]
    
    # Statistiques
    total_files_checked = 0
    files_with_placeholders = 0
    total_placeholders = 0
    clean_files = 0
    
    # Vérifier les fichiers prioritaires
    print("\n📋 FICHIERS PRIORITAIRES:")
    print("-" * 30)
    
    for file_path in priority_files:
        full_path = project_path / file_path
        
        if full_path.exists():
            placeholders = check_file_placeholders(full_path, project_path)
            total_files_checked += 1
            
            if placeholders:
                files_with_placeholders += 1
                total_placeholders += len(placeholders)
                print(f"⚠️ {file_path}: {len(placeholders)} placeholder(s)")
                for ph in placeholders:
                    print(f"   Ligne {ph['line']}: '{ph['text']}'")
            else:
                clean_files += 1
                print(f"✅ {file_path}: Propre")
        else:
            print(f"❌ {file_path}: Fichier non trouvé")
    
    # Scan complet du projet
    print(f"\n🔍 SCAN COMPLET DU PROJET:")
    print("-" * 30)
    
    exclude_dirs = {'.git', '__pycache__', 'venv', '.github', 'backup_20250527_120707', 'DELETED_FILES'}
    all_placeholders = []
    
    for root, dirs, files in os.walk(project_path):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        
        for file in files:
            if file.endswith('.py') and not file.startswith(('remove_', 'clean_', 'verify_')):
                file_path = Path(root) / file
                placeholders = check_file_placeholders(file_path, project_path)
                
                if placeholders:
                    relative_path = file_path.relative_to(project_path)
                    if str(relative_path) not in [f for f in priority_files]:
                        print(f"⚠️ {relative_path}: {len(placeholders)} placeholder(s)")
                        for ph in placeholders:
                            print(f"   Ligne {ph['line']}: '{ph['text']}'")
                    
                    all_placeholders.extend(placeholders)
    
    # Résumé final
    print(f"\n📊 RÉSUMÉ DE VÉRIFICATION:")
    print("=" * 50)
    print(f"📄 Fichiers vérifiés: {total_files_checked}")
    print(f"✅ Fichiers propres: {clean_files}")
    print(f"⚠️ Fichiers avec placeholders: {files_with_placeholders}")
    print(f"💬 Total placeholders trouvés: {len(all_placeholders)}")
    
    if all_placeholders:
        print(f"\n❌ PROJET NON PROPRE - {len(all_placeholders)} placeholders restants")
        print("💡 Utilisez clean_placeholders.py pour les supprimer")
        return False
    else:
        print(f"\n✅ PROJET PROPRE - Aucun placeholder trouvé")
        print("🎉 Tous les formulaires ont des champs vides par défaut")
        return True

def check_file_placeholders(file_path, project_path):
    """Vérifier les placeholders dans un fichier"""
    placeholders = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.split('\n')
            
            for line_num, line in enumerate(lines, 1):
                # Chercher les placeholders non vides
                if 'placeholder=' in line:
                    # Pattern pour capturer le contenu du placeholder
                    pattern = r'placeholder=["\']([^"\']*)["\']'
                    match = re.search(pattern, line)
                    
                    if match:
                        placeholder_text = match.group(1)
                        # Seulement les placeholders non vides
                        if placeholder_text.strip():
                            placeholders.append({
                                'line': line_num,
                                'text': placeholder_text,
                                'context': line.strip()
                            })
    
    except Exception as e:
        print(f"❌ Erreur lecture {file_path.relative_to(project_path)}: {e}")
    
    return placeholders

def generate_report():
    """Générer un rapport détaillé de l'état des placeholders"""
    
    project_path = Path(__file__).parent
    
    print("📊 GÉNÉRATION DU RAPPORT DÉTAILLÉ")
    print("=" * 50)
    
    # Créer le rapport
    report_lines = []
    report_lines.append("# Rapport de Vérification des Placeholders - BudgetManage")
    report_lines.append(f"Date: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    report_lines.append("")
    
    # Analyser chaque fichier
    exclude_dirs = {'.git', '__pycache__', 'venv', '.github', 'backup_20250527_120707', 'DELETED_FILES'}
    
    files_analyzed = 0
    total_placeholders = 0
    
    for root, dirs, files in os.walk(project_path):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        
        for file in files:
            if file.endswith('.py') and not file.startswith(('remove_', 'clean_', 'verify_')):
                file_path = Path(root) / file
                relative_path = file_path.relative_to(project_path)
                
                placeholders = check_file_placeholders(file_path, project_path)
                files_analyzed += 1
                
                if placeholders:
                    total_placeholders += len(placeholders)
                    report_lines.append(f"## ⚠️ {relative_path}")
                    report_lines.append(f"Placeholders trouvés: {len(placeholders)}")
                    report_lines.append("")
                    
                    for i, ph in enumerate(placeholders, 1):
                        report_lines.append(f"{i}. **Ligne {ph['line']}**: `{ph['text']}`")
                        report_lines.append(f"   - Contexte: `{ph['context']}`")
                    
                    report_lines.append("")
                else:
                    report_lines.append(f"## ✅ {relative_path}")
                    report_lines.append("Aucun placeholder trouvé")
                    report_lines.append("")
    
    # Résumé
    report_lines.append("## 📊 Résumé")
    report_lines.append(f"- **Fichiers analysés**: {files_analyzed}")
    report_lines.append(f"- **Total placeholders**: {total_placeholders}")
    
    if total_placeholders == 0:
        report_lines.append("- **Statut**: ✅ PROJET PROPRE")
    else:
        report_lines.append("- **Statut**: ⚠️ NETTOYAGE REQUIS")
    
    # Sauvegarder le rapport
    report_path = project_path / "rapport_placeholders.md"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report_lines))
    
    print(f"📄 Rapport sauvegardé: {report_path}")
    return report_path, total_placeholders

def main():
    print("🔍 BUDGETMANAGE - VÉRIFICATION DES PLACEHOLDERS")
    print("=" * 60)
    
    while True:
        print("\n🎯 OPTIONS DISPONIBLES:")
        print("1. Vérification rapide")
        print("2. Rapport détaillé")
        print("3. Les deux")
        print("0. Quitter")
        
        choice = input("\nVotre choix (0-3): ").strip()
        
        if choice == '1':
            is_clean = verify_placeholders()
            if is_clean:
                print("\n🎉 Félicitations ! Le projet est propre.")
            else:
                print("\n💡 Utilisez clean_placeholders.py pour nettoyer")
        
        elif choice == '2':
            report_path, total = generate_report()
            print(f"\n📊 {total} placeholders trouvés au total")
            
        elif choice == '3':
            print("\n🔍 Étape 1: Vérification rapide")
            is_clean = verify_placeholders()
            
            print("\n📊 Étape 2: Génération du rapport")
            report_path, total = generate_report()
            
            if is_clean:
                print("\n🎉 Le projet est parfaitement propre !")
            else:
                print(f"\n💡 {total} placeholders à nettoyer")
        
        elif choice == '0':
            print("👋 Au revoir !")
            break
        
        else:
            print("❌ Choix invalide. Veuillez sélectionner 0-3.")

if __name__ == "__main__":
    main()
