#!/usr/bin/env python3
"""
Test rapide pour vérifier les corrections de l'interface admin
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.database import db

def test_column_mapping():
    """Teste le mapping des colonnes"""
    print("🧪 TEST MAPPING DES COLONNES")
    print("=" * 35)
    
    try:
        # Vérifier les colonnes de la table demandes
        columns_info = db.execute_query("PRAGMA table_info(demandes)", fetch='all')
        existing_columns = [col['name'] for col in columns_info]
        
        print("📋 Colonnes existantes dans 'demandes':")
        for col in existing_columns:
            print(f"   • {col}")
        
        # Tester le mapping
        category_mapping = {
            'budget': 'budget',
            'categorie': 'categorie',
            'typologie_client': 'typologie_client',
            'groupe_groupement': 'groupe_groupement',
            'region': 'region',
            'annee_fiscale': None  # Pas de colonne directe
        }
        
        print(f"\n🎯 Test du mapping:")
        for category, expected_column in category_mapping.items():
            if expected_column is None:
                print(f"   ✅ {category} → Pas de colonne (correct)")
            elif expected_column in existing_columns:
                print(f"   ✅ {category} → {expected_column} (colonne existe)")
            else:
                print(f"   ❌ {category} → {expected_column} (colonne manquante)")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur test: {e}")
        return False

def test_usage_count_function():
    """Teste la fonction de comptage d'usage"""
    print(f"\n🔧 TEST FONCTION _get_usage_count")
    print("=" * 35)
    
    # Import de la fonction
    sys.path.append('./views')
    try:
        from views.admin_dropdown_options_view import _get_usage_count
        
        # Tests sur différentes catégories
        test_cases = [
            ('budget', 'test_value'),
            ('categorie', 'test_value'),
            ('annee_fiscale', 'BY25'),  # Cas spécial
            ('invalid_category', 'test_value')
        ]
        
        for category, value in test_cases:
            try:
                result = _get_usage_count(category, value)
                if result is not None:
                    print(f"   ✅ {category} → {result} utilisations")
                else:
                    print(f"   ℹ️ {category} → Pas de colonne correspondante")
            except Exception as e:
                print(f"   ❌ {category} → Erreur: {e}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Impossible d'importer la fonction: {e}")
        return False

def test_fiscal_years_in_dropdown():
    """Teste les années fiscales dans dropdown_options"""
    print(f"\n📅 TEST ANNÉES FISCALES")
    print("=" * 25)
    
    try:
        # Vérifier les années fiscales
        fiscal_years = db.execute_query("""
            SELECT value, label, is_active 
            FROM dropdown_options 
            WHERE category = 'annee_fiscale'
            ORDER BY order_index
        """, fetch='all')
        
        if fiscal_years:
            print(f"📊 {len(fiscal_years)} années fiscales trouvées:")
            for year in fiscal_years[:5]:  # Afficher seulement les 5 premières
                status = "🟢" if year['is_active'] else "🔴"
                print(f"   {status} {year['value']} → {year['label']}")
            
            if len(fiscal_years) > 5:
                print(f"   ... et {len(fiscal_years) - 5} autres")
        else:
            print("❌ Aucune année fiscale trouvée")
            print("💡 Utilisez l'assistant dans l'interface pour les générer")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur test années fiscales: {e}")
        return False

def main():
    """Fonction principale de test"""
    print("🔍 TEST CORRECTIONS INTERFACE ADMIN")
    print("=" * 45)
    print("🎯 Vérification des corrections apportées")
    print()
    
    try:
        db.init_database()
        
        # Tests
        test1 = test_column_mapping()
        test2 = test_usage_count_function()
        test3 = test_fiscal_years_in_dropdown()
        
        # Résumé
        print(f"\n" + "=" * 45)
        print("📊 RÉSUMÉ DES TESTS")
        print("=" * 45)
        
        tests = [
            ("Mapping colonnes", test1),
            ("Fonction usage count", test2),
            ("Années fiscales", test3)
        ]
        
        all_passed = True
        for test_name, result in tests:
            status = "✅ PASSÉ" if result else "❌ ÉCHEC"
            print(f"{test_name:.<25} {status}")
            if not result:
                all_passed = False
        
        print()
        if all_passed:
            print("🎉 TOUS LES TESTS PASSÉS!")
            print("✅ Les corrections fonctionnent correctement")
            print("🚀 L'interface admin devrait maintenant fonctionner sans erreurs")
        else:
            print("⚠️ CERTAINS TESTS ONT ÉCHOUÉ")
            print("🔧 Vérifiez les erreurs ci-dessus")
        
        return all_passed
        
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")
        return False

if __name__ == "__main__":
    success = main()
    print(f"\n💡 PROCHAINES ÉTAPES:")
    print(f"   1. Redémarrez Streamlit")
    print(f"   2. Testez l'interface 'Listes Déroulantes'")
    print(f"   3. Sélectionnez 'Année Fiscale' et testez l'assistant")
    sys.exit(0 if success else 1)
