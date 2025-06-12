#!/usr/bin/env python3
"""
Script pour simplifier les labels des années fiscales
Supprime les parenthèses inutiles : BY25 (2025) → BY25
"""
import sys
import os

# Ajouter le répertoire du projet au path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def simplify_fiscal_year_labels():
    """Simplifie les labels des années fiscales"""
    print("🎨 Simplification des labels années fiscales...")
    
    try:
        from models.database import db
        
        # 1. Récupérer toutes les années fiscales
        years = db.execute_query("""
            SELECT id, value, label
            FROM dropdown_options 
            WHERE category = 'annee_fiscale'
            ORDER BY order_index
        """, fetch='all')
        
        if not years:
            print("⚠️ Aucune année fiscale trouvée")
            return True
        
        print(f"📋 {len(years)} année(s) fiscale(s) trouvée(s):")
        
        simplifications = []
        
        for year in years:
            old_label = year['label']
            value = year['value']
            
            # Si le label contient des parenthèses, le simplifier
            if '(' in old_label and ')' in old_label:
                new_label = value  # BY25 au lieu de BY25 (2025)
                simplifications.append((year['id'], old_label, new_label))
                print(f"  📝 {old_label} → {new_label}")
            else:
                print(f"  ✅ {old_label} (déjà simple)")
        
        if not simplifications:
            print("✅ Aucune simplification nécessaire")
            return True
        
        # 2. Appliquer les simplifications
        print(f"\n🔄 Application de {len(simplifications)} simplification(s)...")
        
        for year_id, old_label, new_label in simplifications:
            db.execute_query("""
                UPDATE dropdown_options 
                SET label = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (new_label, year_id))
            print(f"  ✅ Mis à jour: {old_label} → {new_label}")
        
        # 3. Vérification finale
        print("\n🔍 Vérification finale...")
        
        final_years = db.execute_query("""
            SELECT value, label, is_active
            FROM dropdown_options 
            WHERE category = 'annee_fiscale'
            ORDER BY order_index
        """, fetch='all')
        
        print(f"📋 Labels finaux ({len(final_years)}):")
        for year in final_years:
            status = "✅" if year['is_active'] else "❌"
            simple = "✅" if '(' not in year['label'] else "❌"
            print(f"  {status} {simple} {year['value']} → '{year['label']}'")
        
        # 4. Test des utilitaires
        print("\n🧪 Test des utilitaires après simplification...")
        from utils.fiscal_year_utils import get_valid_fiscal_years, get_default_fiscal_year
        
        valid_years = get_valid_fiscal_years()
        print(f"get_valid_fiscal_years(): {valid_years}")
        
        # Vérifier qu'il n'y a plus de parenthèses
        has_parentheses = any('(' in label for _, label in valid_years)
        print(f"Contient des parenthèses: {has_parentheses}")
        
        if not has_parentheses:
            print("✅ Tous les labels sont maintenant simples!")
        else:
            print("⚠️ Certains labels contiennent encore des parenthèses")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur simplification: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = simplify_fiscal_year_labels()
    if success:
        print("\n🎉 Simplification terminée!")
        print("Les années fiscales ont maintenant des labels simples:")
        print("  BY23, BY24, BY25, BY26, BY27")
        print("\nVous pouvez relancer l'application:")
        print("  streamlit run main.py")
    else:
        print("\n💥 Simplification échouée!")
    
    exit(0 if success else 1)
