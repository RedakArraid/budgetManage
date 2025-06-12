#!/usr/bin/env python3
"""
Test de debug pour identifier le problème avec l'année par défaut
"""
import sys
import os

# Ajouter le répertoire du projet au path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def debug_fiscal_year():
    print("🔍 Debug année fiscale par défaut...")
    
    try:
        from utils.fiscal_year_utils import get_valid_fiscal_years, get_default_fiscal_year
        
        # Test récupération années
        print("\n1. Test get_valid_fiscal_years():")
        valid_years = get_valid_fiscal_years()
        print(f"   Résultat: {valid_years}")
        print(f"   Type: {type(valid_years)}")
        print(f"   Longueur: {len(valid_years)}")
        
        if valid_years:
            print(f"   Premier élément: {valid_years[0]}")
            print(f"   Type premier: {type(valid_years[0])}")
            if len(valid_years[0]) >= 2:
                print(f"   Value: {repr(valid_years[0][0])}")
                print(f"   Label: {repr(valid_years[0][1])}")
        
        # Test année par défaut
        print("\n2. Test get_default_fiscal_year():")
        default_year = get_default_fiscal_year()
        print(f"   Résultat: {repr(default_year)}")
        print(f"   Type: {type(default_year)}")
        print(f"   Longueur: {len(default_year)}")
        print(f"   Commence par BY: {default_year.startswith('BY') if default_year else False}")
        
        # Test validation
        print("\n3. Test validate_fiscal_year():")
        from utils.fiscal_year_utils import validate_fiscal_year
        
        if default_year:
            is_valid = validate_fiscal_year(default_year)
            print(f"   Validation de '{default_year}': {is_valid}")
        
        # Vérifier base de données directement
        print("\n4. Vérification base de données:")
        from models.database import db
        
        options = db.execute_query('''
            SELECT value, label, is_active 
            FROM dropdown_options 
            WHERE category = 'annee_fiscale'
            ORDER BY order_index ASC
        ''', fetch='all')
        
        print(f"   Options trouvées: {len(options)}")
        for i, opt in enumerate(options):
            print(f"   [{i}] value='{opt['value']}', label='{opt['label']}', active={opt['is_active']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur debug: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    debug_fiscal_year()
