#!/usr/bin/env python3
"""
Script d'initialisation des années fiscales
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.database import db

def init_annees_fiscales():
    """Initialiser les années fiscales dans les listes déroulantes"""
    try:
        print("🗓️ Initialisation des années fiscales...")
        
        # S'assurer que la base est initialisée
        db.init_database()
        
        # Vérifier si des années fiscales existent déjà
        existing_years = db.execute_query(
            "SELECT COUNT(*) as count FROM dropdown_options WHERE category = 'annee_fiscale'", 
            fetch='one'
        )
        
        if existing_years and existing_years['count'] > 0:
            print(f"✅ {existing_years['count']} années fiscales déjà présentes")
            return True
        
        # Années fiscales à ajouter (périodes 2019-2020 à 2029-2030) au format BYXX
        # LOGIQUE: BY25 = Mai 2024 à Avril 2025
        annees_fiscales = [
            ('annee_fiscale', 'BY20', 'BY20 (Mai 2019 - Avril 2020)', 1),
            ('annee_fiscale', 'BY21', 'BY21 (Mai 2020 - Avril 2021)', 2),
            ('annee_fiscale', 'BY22', 'BY22 (Mai 2021 - Avril 2022)', 3),
            ('annee_fiscale', 'BY23', 'BY23 (Mai 2022 - Avril 2023)', 4),
            ('annee_fiscale', 'BY24', 'BY24 (Mai 2023 - Avril 2024)', 5),
            ('annee_fiscale', 'BY25', 'BY25 (Mai 2024 - Avril 2025)', 6),
            ('annee_fiscale', 'BY26', 'BY26 (Mai 2025 - Avril 2026)', 7),
            ('annee_fiscale', 'BY27', 'BY27 (Mai 2026 - Avril 2027)', 8),
            ('annee_fiscale', 'BY28', 'BY28 (Mai 2027 - Avril 2028)', 9),
            ('annee_fiscale', 'BY29', 'BY29 (Mai 2028 - Avril 2029)', 10),
            ('annee_fiscale', 'BY30', 'BY30 (Mai 2029 - Avril 2030)', 11),
        ]
        
        success_count = 0
        for category, value, label, order_index in annees_fiscales:
            try:
                db.execute_query('''
                    INSERT OR IGNORE INTO dropdown_options (category, value, label, order_index, is_active)
                    VALUES (?, ?, ?, ?, ?)
                ''', (category, value, label, order_index, True))
                success_count += 1
            except Exception as e:
                print(f"Erreur insertion année {value}: {e}")
        
        print(f"✅ {success_count} années fiscales initialisées")
        return True
        
    except Exception as e:
        print(f"❌ Erreur initialisation années fiscales: {e}")
        return False

if __name__ == "__main__":
    print("🗓️ Initialisation des Années Fiscales - BudgetManage")
    print("=" * 55)
    
    success = init_annees_fiscales()
    
    if success:
        print("\n🎉 ANNÉES FISCALES INITIALISÉES AVEC SUCCÈS!")
        print("\n📋 Années ajoutées:")
        print("   • BY20 à BY30 (11 périodes fiscales)")
        print("   • Format: BY25 = Mai 2024 à Avril 2025")
        print("   • Période fiscale: Mai N-1 à Avril N")
        print("\n🚀 Prochaines étapes:")
        print("   1. Redémarrez votre application")
        print("   2. Allez dans 'Listes Déroulantes' pour voir les années")
        print("   3. Testez la création de demandes avec sélection d'année")
        print("   4. Accédez à 'Gestion Budgets' pour attribuer des budgets")
    else:
        print("\n❌ ÉCHEC DE L'INITIALISATION")
        print("   Vérifiez les erreurs ci-dessus")
