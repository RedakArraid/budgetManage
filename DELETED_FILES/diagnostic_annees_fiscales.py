#!/usr/bin/env python3
"""
Script de diagnostic rapide pour les années fiscales
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.database import db

def diagnostic_annees_fiscales():
    """Diagnostic rapide des années fiscales"""
    print("🔍 DIAGNOSTIC ANNÉES FISCALES")
    print("=" * 40)
    
    try:
        db.init_database()
        
        # Vérifier les années existantes
        years = db.execute_query("""
            SELECT id, value, label, is_active 
            FROM dropdown_options 
            WHERE category = 'annee_fiscale'
            ORDER BY order_index
        """, fetch='all')
        
        if not years:
            print("❌ PROBLÈME: Aucune année fiscale trouvée")
            print("💡 SOLUTION: Exécutez python init_annees_fiscales.py")
            return False
        
        print(f"📊 {len(years)} années fiscales trouvées")
        
        # Analyser les formats
        by_format = 0
        full_year = 0
        problems = []
        
        for year in years:
            value = year['value']
            label = year['label']
            active = "🟢" if year['is_active'] else "🔴"
            
            print(f"   {active} {value} → {label}")
            
            if value.startswith('BY') and len(value) == 4:
                by_format += 1
            elif value.isdigit() and len(value) == 4:
                full_year += 1
                problems.append(f"Format incorrect: {value} devrait être BY{int(value) % 100:02d}")
            else:
                problems.append(f"Format inconnu: {value}")
        
        print(f"\n📋 ANALYSE:")
        print(f"   ✅ Format BYXX: {by_format}")
        print(f"   ⚠️ Format complet: {full_year}")
        
        if problems:
            print(f"\n❌ PROBLÈMES DÉTECTÉS:")
            for problem in problems:
                print(f"   • {problem}")
            
            print(f"\n💡 SOLUTION:")
            print(f"   Exécutez: python fix_annees_fiscales_byxx.py")
            return False
        else:
            print(f"\n✅ TOUT EST CORRECT!")
            print(f"   Format BYXX correctement configuré")
            return True
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

if __name__ == "__main__":
    success = diagnostic_annees_fiscales()
    if not success:
        print(f"\n🔧 Pour corriger automatiquement:")
        print(f"   python fix_annees_fiscales_byxx.py")
