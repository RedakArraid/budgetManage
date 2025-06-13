#!/usr/bin/env python3
"""
Script de nettoyage du modèle Demande pour éliminer fiscal_year
Supprime les vestiges fiscal_year et simplifie calculate_cy_by()
"""
import sys
import os
import shutil
from datetime import datetime

# Ajouter le répertoire du projet au path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def create_cleaned_demande_model():
    """Créer version nettoyée du modèle Demande"""
    print("🧹 NETTOYAGE DEMANDE MODEL - Suppression fiscal_year")
    print("=" * 55)
    
    try:
        # Chemins
        migration_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(migration_dir)
        
        original_file = os.path.join(project_root, "models", "demande.py")
        backup_file = os.path.join(migration_dir, f"demande_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py")
        cleaned_file = os.path.join(migration_dir, "demande_cleaned.py")
        
        print(f"📂 Fichier original: {original_file}")
        print(f"📂 Backup: {backup_file}")
        print(f"📂 Version nettoyée: {cleaned_file}")
        
        # 1. Backup du fichier original
        print(f"\n📋 1. BACKUP FICHIER ORIGINAL")
        print("-" * 30)
        
        if not os.path.exists(original_file):
            print(f"❌ Fichier original introuvable: {original_file}")
            return False
        
        shutil.copy2(original_file, backup_file)
        print(f"✅ Backup créé: {backup_file}")
        
        # 2. Lire et analyser le fichier original
        print(f"\n📋 2. ANALYSE FICHIER ORIGINAL")
        print("-" * 30)
        
        with open(original_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"📊 Taille originale: {len(content)} caractères")
        
        # Compter les occurrences fiscal_year
        fiscal_year_count = content.count('fiscal_year')
        print(f"📊 Occurrences 'fiscal_year': {fiscal_year_count}")
        
        # 3. Nettoyer le contenu
        print(f"\n📋 3. NETTOYAGE CONTENU")
        print("-" * 30)
        
        cleaned_content = clean_demande_model_content(content)
        
        print(f"📊 Taille nettoyée: {len(cleaned_content)} caractères")
        print(f"📊 Réduction: {len(content) - len(cleaned_content)} caractères")
        
        # Vérifier que fiscal_year a été supprimé
        remaining_fiscal_year = cleaned_content.count('fiscal_year')
        print(f"📊 Occurrences 'fiscal_year' restantes: {remaining_fiscal_year}")
        
        # 4. Sauvegarder version nettoyée
        print(f"\n📋 4. SAUVEGARDE VERSION NETTOYÉE")
        print("-" * 30)
        
        with open(cleaned_file, 'w', encoding='utf-8') as f:
            f.write(cleaned_content)
        
        print(f"✅ Version nettoyée sauvegardée: {cleaned_file}")
        
        # 5. Valider la syntaxe Python
        print(f"\n📋 5. VALIDATION SYNTAXE")
        print("-" * 30)
        
        try:
            compile(cleaned_content, cleaned_file, 'exec')
            print("✅ Syntaxe Python valide")
        except SyntaxError as e:
            print(f"❌ Erreur syntaxe: {e}")
            return False
        
        # 6. Test d'import simulé
        print(f"\n📋 6. TEST IMPORT SIMULÉ")
        print("-" * 30)
        
        # Vérifier les imports et définitions principales
        required_elements = [
            'class DemandeModel:',
            'def calculate_cy_by(',
            '@dataclass',
            'class Demande:'
        ]
        
        for element in required_elements:
            if element in cleaned_content:
                print(f"✅ {element}")
            else:
                print(f"❌ Manquant: {element}")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur nettoyage: {e}")
        import traceback
        traceback.print_exc()
        return False

def clean_demande_model_content(content: str) -> str:
    """Nettoyer le contenu du modèle Demande"""
    lines = content.split('\n')
    cleaned_lines = []
    
    for line in lines:
        # Nettoyer la fonction calculate_cy_by()
        if 'def calculate_cy_by(' in line:
            # Simplifier la docstring
            cleaned_lines.append(line)
            continue
        
        # Simplifier la docstring de calculate_cy_by
        if 'Calculer cy (année civile), by (année fiscale string YY/YY), et fiscal_year (année fiscale int)' in line:
            cleaned_lines.append(line.replace(
                ', by (année fiscale string YY/YY), et fiscal_year (année fiscale int)',
                ' et by (année fiscale string)'
            ))
            continue
        
        # Simplifier le return de calculate_cy_by
        if 'return cy, by_string, fiscal_year_start_year' in line:
            cleaned_lines.append('    return cy, by_string  # Simplifié: plus besoin de fiscal_year_start_year')
            continue
        
        # Supprimer fy du dataclass Demande
        if 'fy: Optional[int] = None' in line:
            cleaned_lines.append('    # fy: Optional[int] = None  # ← SUPPRIMÉ: utiliser by uniquement')
            continue
        
        # Nettoyer allowed_fields dans update_demande
        if "'demandeur_participe', 'participants_libres', 'cy', 'by', 'fiscal_year'" in line:
            cleaned_lines.append(line.replace(", 'fiscal_year'", ""))
            continue
        
        # Supprimer les commentaires obsolètes
        if "Note: 'by' and 'fy' are NOT recalculated here" in line:
            cleaned_lines.append("                    # Note: 'by' est maintenant géré manuellement via les dropdowns admin")
            continue
        
        # Nettoyer les commentaires dans calculate_cy_by
        if 'Return calendar year, BY string, and fiscal year start year (integer)' in line:
            cleaned_lines.append('    # Return calendar year et BY string')
            continue
        
        # Conserver le reste
        cleaned_lines.append(line)
    
    return '\n'.join(cleaned_lines)

def apply_cleaned_model():
    """Appliquer la version nettoyée"""
    print(f"\n📋 APPLICATION VERSION NETTOYÉE")
    print("-" * 35)
    
    try:
        migration_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(migration_dir)
        
        cleaned_file = os.path.join(migration_dir, "demande_cleaned.py")
        target_file = os.path.join(project_root, "models", "demande.py")
        
        if not os.path.exists(cleaned_file):
            print(f"❌ Fichier nettoyé introuvable: {cleaned_file}")
            return False
        
        # Copier la version nettoyée
        shutil.copy2(cleaned_file, target_file)
        print(f"✅ Version nettoyée appliquée: {target_file}")
        
        # Test d'import
        print(f"\n🧪 Test d'import...")
        try:
            import importlib
            import models.demande
            importlib.reload(models.demande)
            
            from models.demande import DemandeModel, calculate_cy_by, Demande
            print("✅ Import DemandeModel OK")
            print("✅ Import calculate_cy_by OK")
            print("✅ Import Demande OK")
            
            # Test calculate_cy_by simplifié
            from datetime import date
            test_date = date(2025, 6, 15)
            result = calculate_cy_by(test_date)
            
            if len(result) == 2:  # Maintenant retourne seulement 2 valeurs
                cy, by = result
                print(f"✅ calculate_cy_by({test_date}) = cy:{cy}, by:{by}")
            else:
                print(f"⚠️ calculate_cy_by retourne {len(result)} valeurs: {result}")
            
            return True
            
        except Exception as e:
            print(f"❌ Erreur test import: {e}")
            return False
        
    except Exception as e:
        print(f"❌ Erreur application: {e}")
        return False

def validate_cleaned_model():
    """Valider que le nettoyage est correct"""
    print(f"\n📋 VALIDATION VERSION NETTOYÉE")
    print("-" * 35)
    
    try:
        from models.demande import DemandeModel
        
        # 1. Vérifier allowed_fields
        print("🔍 Test allowed_fields...")
        
        # Simuler update_demande pour vérifier allowed_fields
        if hasattr(DemandeModel, 'update_demande'):
            import inspect
            source = inspect.getsource(DemandeModel.update_demande)
            
            if 'fiscal_year' in source:
                print("⚠️ 'fiscal_year' encore présent dans allowed_fields")
                return False
            else:
                print("✅ 'fiscal_year' supprimé de allowed_fields")
        
        # 2. Vérifier dataclass Demande
        print("🔍 Test dataclass Demande...")
        from models.demande import Demande
        
        # Créer instance test
        test_demande = Demande()
        
        if hasattr(test_demande, 'fy'):
            print("⚠️ Attribut 'fy' encore présent dans dataclass")
            return False
        else:
            print("✅ Attribut 'fy' supprimé de dataclass")
        
        # Vérifier que by est présent
        if hasattr(test_demande, 'by'):
            print("✅ Attribut 'by' présent dans dataclass")
        else:
            print("❌ Attribut 'by' manquant dans dataclass")
            return False
        
        # 3. Vérifier calculate_cy_by
        print("🔍 Test calculate_cy_by...")
        from models.demande import calculate_cy_by
        from datetime import date
        
        result = calculate_cy_by(date(2025, 8, 15))
        
        if len(result) == 2:
            cy, by = result
            print(f"✅ calculate_cy_by retourne 2 valeurs: cy={cy}, by={by}")
        else:
            print(f"❌ calculate_cy_by retourne {len(result)} valeurs (attendu: 2)")
            return False
        
        print("✅ Validation réussie")
        return True
        
    except Exception as e:
        print(f"❌ Erreur validation: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🧹 CLEAN DEMANDE MODEL")
    print("=" * 55)
    
    # 1. Créer version nettoyée
    success = create_cleaned_demande_model()
    
    if success:
        # 2. Appliquer la version nettoyée
        apply_success = apply_cleaned_model()
        
        if apply_success:
            # 3. Valider le nettoyage
            validation_success = validate_cleaned_model()
            
            print(f"\n{'='*55}")
            if validation_success:
                print("🎉 Nettoyage DemandeModel réussi!")
                print("Modifications apportées:")
                print("  ✅ 'fiscal_year' supprimé de allowed_fields")
                print("  ✅ 'fy' supprimé de dataclass Demande")
                print("  ✅ calculate_cy_by() simplifié (2 valeurs au lieu de 3)")
                print("  ✅ Commentaires mis à jour")
                print("Prochaine étape: python migration_by_only/06_clean_database_init.py")
            else:
                print("⚠️ Nettoyage appliqué mais validation échouée")
                print("Vérifiez les erreurs avant de continuer")
        else:
            print(f"\n{'='*55}")
            print("💥 Application version nettoyée échouée!")
    else:
        print(f"\n{'='*55}")
        print("💥 Création version nettoyée échouée!")
    
    exit(0 if success and (not 'validation_success' in locals() or validation_success) else 1)
