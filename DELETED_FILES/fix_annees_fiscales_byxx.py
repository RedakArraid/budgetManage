#!/usr/bin/env python3
"""
Script de correction pour les années fiscales - Format BYXX
Résout le problème où les années fiscales ne sont pas au format BY + 2 derniers chiffres
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.database import db

def fix_annees_fiscales_format():
    """
    Corrige le format des années fiscales pour utiliser BYXX
    où XX sont les deux derniers chiffres de l'année
    """
    try:
        print("🔧 Correction du format des années fiscales...")
        print("📋 Passage du format '2024' vers 'BY24'")
        
        # S'assurer que la base est initialisée
        db.init_database()
        
        # Vérifier les années fiscales existantes
        existing_years = db.execute_query("""
            SELECT id, value, label, order_index 
            FROM dropdown_options 
            WHERE category = 'annee_fiscale'
            ORDER BY order_index
        """, fetch='all')
        
        if not existing_years:
            print("❌ Aucune année fiscale trouvée. Exécutez d'abord init_annees_fiscales.py")
            return False
        
        print(f"📊 {len(existing_years)} années fiscales trouvées")
        
        # Analyser le format actuel
        needs_correction = []
        already_correct = []
        
        for year in existing_years:
            value = year['value']
            label = year['label']
            
            # Vérifier si c'est déjà au format BYXX
            if value.startswith('BY') and len(value) == 4:
                already_correct.append(year)
            elif value.isdigit() and len(value) == 4:
                # Format année complète (ex: "2024")
                # Conversion vers BYXX (ex: "BY24")
                year_num = int(value)
                by_format = f"BY{year_num % 100:02d}"
                needs_correction.append({
                    'id': year['id'],
                    'old_value': value,
                    'old_label': label,
                    'new_value': by_format,
                    'new_label': f"{by_format} ({value})",
                    'order_index': year['order_index']
                })
            else:
                print(f"⚠️ Format non reconnu pour l'année: {value}")
        
        print(f"✅ {len(already_correct)} années déjà au bon format")
        print(f"🔧 {len(needs_correction)} années à corriger")
        
        if not needs_correction:
            print("🎉 Toutes les années sont déjà au bon format!")
            return True
        
        # Afficher les corrections prévues
        print("\n📋 Corrections prévues:")
        for correction in needs_correction:
            print(f"   {correction['old_value']} → {correction['new_value']}")
            print(f"   '{correction['old_label']}' → '{correction['new_label']}'")
        
        # Appliquer les corrections automatiquement
        success_count = 0
        error_count = 0
        
        for correction in needs_correction:
            try:
                # Mise à jour de l'enregistrement
                rows_affected = db.execute_query("""
                    UPDATE dropdown_options 
                    SET value = ?, label = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (
                    correction['new_value'],
                    correction['new_label'], 
                    correction['id']
                ))
                
                if rows_affected > 0:
                    success_count += 1
                    print(f"✅ Corrigé: {correction['old_value']} → {correction['new_value']}")
                else:
                    error_count += 1
                    print(f"❌ Échec: {correction['old_value']}")
                    
            except Exception as e:
                error_count += 1
                print(f"❌ Erreur pour {correction['old_value']}: {e}")
        
        print(f"\n📊 Résultats: {success_count} succès, {error_count} erreurs")
        return success_count > 0
        
    except Exception as e:
        print(f"❌ Erreur lors de la correction: {e}")
        return False

def add_missing_by_years():
    """
    Ajoute les années manquantes au format BYXX si nécessaire
    """
    try:
        print("\n🆕 Vérification des années manquantes...")
        
        # Années à avoir (2020-2030)
        required_years = list(range(2020, 2031))
        
        # Récupérer les années existantes
        existing = db.execute_query("""
            SELECT value FROM dropdown_options 
            WHERE category = 'annee_fiscale'
        """, fetch='all')
        
        existing_values = [row['value'] for row in existing] if existing else []
        
        # Identifier les années manquantes
        missing_years = []
        for year in required_years:
            by_format = f"BY{year % 100:02d}"
            if by_format not in existing_values and str(year) not in existing_values:
                missing_years.append(year)
        
        if not missing_years:
            print("✅ Toutes les années requises sont présentes")
            return True
        
        print(f"📊 {len(missing_years)} années manquantes à ajouter")
        
        # Ajouter les années manquantes
        success_count = 0
        for year in missing_years:
            try:
                by_format = f"BY{year % 100:02d}"
                label = f"{by_format} ({year})"
                
                # Calculer l'ordre (basé sur l'année)
                order_index = year - 2019  # 2020 = 1, 2021 = 2, etc.
                
                db.execute_query("""
                    INSERT INTO dropdown_options (category, value, label, order_index, is_active)
                    VALUES (?, ?, ?, ?, ?)
                """, ('annee_fiscale', by_format, label, order_index, True))
                
                success_count += 1
                print(f"✅ Ajouté: {by_format} ({year})")
                
            except Exception as e:
                print(f"❌ Erreur ajout {year}: {e}")
        
        print(f"📊 {success_count} années ajoutées")
        return success_count > 0
        
    except Exception as e:
        print(f"❌ Erreur ajout années: {e}")
        return False

def update_existing_demandes():
    """
    Met à jour les demandes existantes pour utiliser le nouveau format BYXX
    """
    try:
        print("\n🔄 Mise à jour des demandes existantes...")
        
        # Mapping des anciens formats vers les nouveaux
        year_mapping = {}
        for year in range(2020, 2031):
            old_format = str(year)
            new_format = f"BY{year % 100:02d}"
            year_mapping[old_format] = new_format
        
        # Vérifier s'il y a des demandes à mettre à jour
        demandes_to_update = db.execute_query("""
            SELECT COUNT(*) as count, annee_fiscale
            FROM demandes 
            WHERE annee_fiscale IN ('2020', '2021', '2022', '2023', '2024', '2025', '2026', '2027', '2028', '2029', '2030')
            GROUP BY annee_fiscale
        """, fetch='all')
        
        if not demandes_to_update:
            print("✅ Aucune demande à mettre à jour")
            return True
        
        total_demandes = sum(row['count'] for row in demandes_to_update)
        print(f"📊 {total_demandes} demandes à mettre à jour")
        
        # Mettre à jour chaque format d'année
        updated_count = 0
        for row in demandes_to_update:
            old_value = row['annee_fiscale']
            count = row['count']
            
            if old_value in year_mapping:
                new_value = year_mapping[old_value]
                
                try:
                    rows_affected = db.execute_query("""
                        UPDATE demandes 
                        SET annee_fiscale = ?
                        WHERE annee_fiscale = ?
                    """, (new_value, old_value))
                    
                    updated_count += rows_affected
                    print(f"✅ {rows_affected} demandes: {old_value} → {new_value}")
                    
                except Exception as e:
                    print(f"❌ Erreur mise à jour {old_value}: {e}")
        
        print(f"📊 {updated_count} demandes mises à jour")
        return updated_count >= 0
        
    except Exception as e:
        print(f"❌ Erreur mise à jour demandes: {e}")
        return False

def main():
    """Fonction principale de correction"""
    print("🔧 CORRECTION FORMAT ANNÉES FISCALES - BYXX")
    print("=" * 55)
    print("🎯 Objectif: Passer du format '2024' vers 'BY24'")
    print("📋 Inclut la mise à jour des demandes existantes")
    print()
    
    steps_results = []
    
    # Étape 1: Corriger le format des années existantes
    print("🔧 ÉTAPE 1: Correction format années fiscales")
    print("-" * 45)
    result1 = fix_annees_fiscales_format()
    steps_results.append(("Format années", result1))
    
    # Étape 2: Ajouter les années manquantes
    print("\n🆕 ÉTAPE 2: Ajout années manquantes")
    print("-" * 35)
    result2 = add_missing_by_years()
    steps_results.append(("Années manquantes", result2))
    
    # Étape 3: Mettre à jour les demandes existantes
    print("\n🔄 ÉTAPE 3: Mise à jour demandes existantes")
    print("-" * 40)
    result3 = update_existing_demandes()
    steps_results.append(("Demandes existantes", result3))
    
    # Vérification finale
    print("\n🔍 VÉRIFICATION FINALE")
    print("-" * 25)
    final_check = db.execute_query("""
        SELECT value, label 
        FROM dropdown_options 
        WHERE category = 'annee_fiscale'
        ORDER BY order_index
    """, fetch='all')
    
    if final_check:
        print("📋 Années fiscales configurées:")
        for year in final_check:
            print(f"   • {year['value']} - {year['label']}")
    
    # Résumé final
    print("\n" + "=" * 55)
    print("📊 RÉSUMÉ DE LA CORRECTION")
    print("=" * 55)
    
    all_success = True
    for step_name, success in steps_results:
        status = "✅ SUCCÈS" if success else "❌ ÉCHEC"
        print(f"{step_name:.<30} {status}")
        if not success:
            all_success = False
    
    print()
    if all_success:
        print("🎉 CORRECTION TERMINÉE AVEC SUCCÈS!")
        print("\n🚀 Prochaines étapes:")
        print("   1. Redémarrez votre application Streamlit")
        print("   2. Testez la page 'Gestion Budgets'")
        print("   3. Vérifiez que les années s'affichent au format BY24, BY25, etc.")
        print("   4. Testez la création de nouvelles demandes")
    else:
        print("⚠️ CORRECTION PARTIELLE")
        print("   Vérifiez les erreurs ci-dessus")
        print("   Vous pouvez réexécuter ce script")
    
    return all_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
