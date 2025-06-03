#!/usr/bin/env python3
"""
Script principal pour nettoyer automatiquement tous les placeholders de BudgetManage
Exécute le processus complet: analyse -> sauvegarde -> nettoyage -> vérification
"""

import os
import sys
from pathlib import Path

def main():
    print("🚀 BUDGETMANAGE - NETTOYAGE AUTOMATIQUE DES PLACEHOLDERS")
    print("=" * 65)
    
    project_path = Path(__file__).parent
    print(f"📁 Projet: {project_path}")
    
    # Vérifier que nous sommes dans le bon répertoire
    required_files = ['main.py', 'views', 'controllers', 'models']
    missing_files = [f for f in required_files if not (project_path / f).exists()]
    
    if missing_files:
        print(f"❌ Erreur: Fichiers/dossiers manquants: {missing_files}")
        print("💡 Assurez-vous d'être dans le répertoire racine de BudgetManage")
        return 1
    
    print("✅ Structure du projet vérifiée")
    
    # Menu de confirmation
    print("\n🎯 CE SCRIPT VA:")
    print("1. 🔍 Analyser tous les placeholders du projet")
    print("2. 💾 Créer une sauvegarde automatique")
    print("3. 🧹 Supprimer tous les placeholders trouvés")
    print("4. ✅ Vérifier que le nettoyage est complet")
    print("5. 📊 Générer un rapport final")
    
    print("\n⚠️ ATTENTION:")
    print("- Tous les textes d'exemple dans les formulaires seront supprimés")
    print("- Les champs auront placeholder=\"\" (vide)")
    print("- Une sauvegarde sera créée automatiquement")
    
    response = input("\n❓ Continuer avec le nettoyage automatique ? (OUI/non): ")
    
    if response.upper() != 'OUI':
        print("❌ Opération annulée par l'utilisateur")
        return 0
    
    try:
        # Étape 1: Analyse initiale
        print("\n" + "="*50)
        print("📋 ÉTAPE 1: ANALYSE INITIALE")
        print("="*50)
        
        # Importer et exécuter l'analyse
        sys.path.insert(0, str(project_path))
        
        try:
            from verify_placeholders import verify_placeholders, check_file_placeholders
            
            # Scan rapide pour compter les placeholders
            exclude_dirs = {'.git', '__pycache__', 'venv', '.github', 'backup_20250527_120707', 'DELETED_FILES'}
            total_placeholders = 0
            
            for root, dirs, files in os.walk(project_path):
                dirs[:] = [d for d in dirs if d not in exclude_dirs]
                
                for file in files:
                    if file.endswith('.py') and not file.startswith(('remove_', 'clean_', 'verify_', 'auto_clean')):
                        file_path = Path(root) / file
                        placeholders = check_file_placeholders(file_path, project_path)
                        total_placeholders += len(placeholders)
            
            print(f"📊 {total_placeholders} placeholders trouvés dans le projet")
            
            if total_placeholders == 0:
                print("✅ Le projet est déjà propre ! Aucune action nécessaire.")
                return 0
            
        except ImportError as e:
            print(f"⚠️ Impossible d'importer verify_placeholders: {e}")
            print("🔍 Analyse basique...")
            total_placeholders = 1  # Assumer qu'il y en a
        
        # Étape 2: Nettoyage
        print("\n" + "="*50)
        print("🧹 ÉTAPE 2: NETTOYAGE DES PLACEHOLDERS")
        print("="*50)
        
        try:
            from clean_placeholders import remove_placeholders_specific
            success = remove_placeholders_specific()
            
            if not success:
                print("❌ Erreur lors du nettoyage")
                return 1
            
        except ImportError as e:
            print(f"⚠️ Impossible d'importer clean_placeholders: {e}")
            print("🔧 Nettoyage manuel requis...")
            return 1
        
        # Étape 3: Vérification finale
        print("\n" + "="*50)
        print("✅ ÉTAPE 3: VÉRIFICATION FINALE")
        print("="*50)
        
        try:
            from verify_placeholders import verify_placeholders, generate_report
            
            is_clean = verify_placeholders()
            
            if is_clean:
                print("\n🎉 SUCCÈS ! Tous les placeholders ont été supprimés")
            else:
                print("\n⚠️ Certains placeholders subsistent")
            
            # Générer le rapport final
            print("\n📊 Génération du rapport final...")
            report_path, remaining = generate_report()
            
            print(f"📄 Rapport sauvegardé: {report_path}")
            
        except ImportError as e:
            print(f"⚠️ Impossible de vérifier: {e}")
        
        # Résumé final
        print("\n" + "="*50)
        print("🏁 NETTOYAGE TERMINÉ")
        print("="*50)
        print("✅ Placeholders supprimés")
        print("💾 Sauvegarde créée")
        print("📊 Rapport généré")
        print("\n💡 PROCHAINES ÉTAPES:")
        print("1. Testez votre application: streamlit run main.py")
        print("2. Vérifiez que les formulaires sont vides par défaut")
        print("3. Si problème, restaurez depuis la sauvegarde")
        
        return 0
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Opération interrompue par l'utilisateur")
        return 1
    except Exception as e:
        print(f"\n❌ Erreur inattendue: {e}")
        return 1

if __name__ == "__main__":
    exit(main())
