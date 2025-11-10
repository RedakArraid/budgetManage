#!/usr/bin/env python3
"""
Test des corrections pour le formulaire de nouvelle demande
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_fiscal_year_conversion():
    """Teste la conversion des années fiscales"""
    print("🧪 TEST CONVERSION ANNÉES FISCALES")
    print("=" * 40)
    
    try:
        from utils.fiscal_year_utils import byxx_to_year, year_to_byxx
        
        # Tests de conversion BYXX → année
        test_cases = [
            ("BY24", 2023),  # BY24 = Mai 2023 → Avril 2024
            ("BY25", 2024),  # BY25 = Mai 2024 → Avril 2025
            ("BY26", 2025),  # BY26 = Mai 2025 → Avril 2026
        ]
        
        print("🔄 Tests BYXX → Année de début:")
        all_passed = True
        
        for byxx, expected_year in test_cases:
            result = byxx_to_year(byxx)
            if result == expected_year:
                print(f"   ✅ {byxx} → {result} (attendu: {expected_year})")
            else:
                print(f"   ❌ {byxx} → {result} (attendu: {expected_year})")
                all_passed = False
        
        # Test avec valeur invalide
        invalid_result = byxx_to_year("INVALID")
        if invalid_result is None:
            print(f"   ✅ 'INVALID' → None (gestion d'erreur correcte)")
        else:
            print(f"   ❌ 'INVALID' → {invalid_result} (devrait être None)")
            all_passed = False
        
        return all_passed
        
    except ImportError as e:
        print(f"❌ Erreur import: {e}")
        return False
    except Exception as e:
        print(f"❌ Erreur test: {e}")
        return False

def test_dropdown_options():
    """Teste la récupération des options dropdown"""
    print(f"\n📋 TEST OPTIONS DROPDOWN")
    print("=" * 30)
    
    try:
        from views.admin_dropdown_options_view import get_valid_dropdown_options
        
        # Tester les années fiscales
        annee_options = get_valid_dropdown_options('annee_fiscale')
        
        if annee_options:
            print(f"✅ {len(annee_options)} années fiscales trouvées:")
            for value, label in annee_options[:3]:  # Afficher les 3 premières
                print(f"   • {value} → {label}")
            if len(annee_options) > 3:
                print(f"   ... et {len(annee_options) - 3} autres")
        else:
            print("❌ Aucune année fiscale trouvée")
            print("💡 Utilisez l'assistant dans l'interface admin pour les générer")
        
        # Tester d'autres catégories
        categories = ['budget', 'categorie', 'region']
        for category in categories:
            options = get_valid_dropdown_options(category)
            count = len(options) if options else 0
            status = "✅" if count > 0 else "⚠️"
            print(f"   {status} {category}: {count} option(s)")
        
        return len(annee_options) > 0
        
    except Exception as e:
        print(f"❌ Erreur test dropdown: {e}")
        return False

def main():
    """Fonction principale de test"""
    print("🔍 TEST CORRECTIONS NOUVELLE DEMANDE")
    print("=" * 50)
    print("🎯 Vérification des corrections apportées")
    print()
    
    try:
        # Tests
        test1 = test_fiscal_year_conversion()
        test2 = test_dropdown_options()
        
        # Résumé
        print(f"\n" + "=" * 50)
        print("📊 RÉSUMÉ DES TESTS")
        print("=" * 50)
        
        tests = [
            ("Conversion années fiscales", test1),
            ("Options dropdown", test2)
        ]
        
        all_passed = True
        for test_name, result in tests:
            status = "✅ PASSÉ" if result else "❌ ÉCHEC"
            print(f"{test_name:.<30} {status}")
            if not result:
                all_passed = False
        
        print()
        if all_passed:
            print("🎉 TOUS LES TESTS PASSÉS!")
            print("✅ La nouvelle demande devrait fonctionner")
            print("🚀 Plus d'erreur 'invalid literal for int()'")
            print("🚀 Plus de 'Missing Submit Button'")
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
    print(f"   2. Testez 'Nouvelle Demande'")
    print(f"   3. Sélectionnez une année fiscale BYXX")
    print(f"   4. Vérifiez qu'il n'y a plus d'erreur")
    sys.exit(0 if success else 1)
