#!/usr/bin/env python3
"""
Script pour corriger les valeurs des années fiscales existantes
Enlève les valeurs trop verbeuses et garde le format BYXX simple
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.database import db

def fix_fiscal_year_values():
    """Corrige les valeurs des années fiscales pour garder le format BYXX simple"""
    try:
        print("🔧 CORRECTION VALEURS ANNÉES FISCALES")
        print("=" * 45)
        print("🎯 Objectif: Garder uniquement le format BYXX (ex: BY24)")
        print()
        
        # Récupérer toutes les années fiscales
        fiscal_years = db.execute_query("""
            SELECT id, value, label 
            FROM dropdown_options 
            WHERE category = 'annee_fiscale'
            ORDER BY order_index
        """, fetch='all')
        
        if not fiscal_years:
            print("❌ Aucune année fiscale trouvée")
            return False
        
        print(f"📊 {len(fiscal_years)} années fiscales trouvées")
        
        corrections = []
        
        for year in fiscal_years:
            current_value = year['value']
            label = year['label']
            
            # Extraire le code BYXX du label si nécessaire
            if current_value.startswith('BY') and len(current_value) == 4:
                # Déjà au bon format
                print(f"   ✅ {current_value} → Déjà correct")
                continue
            
            # Chercher BY dans le label ou la valeur
            byxx_code = None
            
            # Essayer d'extraire BYXX du label
            if 'BY' in label:
                parts = label.split()
                for part in parts:
                    if part.startswith('BY') and len(part) == 4:
                        byxx_code = part
                        break
            
            # Si pas trouvé, essayer de construire depuis l'ancienne valeur
            if not byxx_code and current_value:
                if 'by' in current_value.lower():
                    # Extraire les chiffres après 'by'
                    import re
                    match = re.search(r'by(\d{2})', current_value.lower())
                    if match:
                        byxx_code = f"BY{match.group(1)}"
            
            if byxx_code:
                corrections.append({
                    'id': year['id'],
                    'old_value': current_value,
                    'new_value': byxx_code,
                    'label': label
                })
                print(f"   🔄 {current_value} → {byxx_code}")
            else:
                print(f"   ⚠️ {current_value} → Impossible de déterminer le code BY")
        
        if not corrections:
            print("\n✅ Toutes les années sont déjà au bon format!")
            return True
        
        print(f"\n🔧 Application de {len(corrections)} corrections...")
        
        success_count = 0
        for correction in corrections:
            try:
                db.execute_query("""
                    UPDATE dropdown_options 
                    SET value = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (correction['new_value'], correction['id']))
                
                success_count += 1
                print(f"   ✅ Corrigé: {correction['old_value']} → {correction['new_value']}")
                
            except Exception as e:
                print(f"   ❌ Erreur pour ID {correction['id']}: {e}")
        
        print(f"\n📊 Résultats: {success_count}/{len(corrections)} corrections appliquées")
        
        # Vérification finale
        if success_count > 0:
            print(f"\n🔍 Vérification finale...")
            final_years = db.execute_query("""
                SELECT value, label 
                FROM dropdown_options 
                WHERE category = 'annee_fiscale'
                ORDER BY order_index
            """, fetch='all')
            
            print("📋 État final:")
            for year in final_years:
                if year['value'].startswith('BY') and len(year['value']) == 4:
                    print(f"   ✅ {year['value']} → {year['label']}")
                else:
                    print(f"   ⚠️ {year['value']} → {year['label']} (format incorrect)")
        
        return success_count > 0
        
    except Exception as e:
        print(f"❌ Erreur lors de la correction: {e}")
        return False

def main():
    """Fonction principale"""
    print("🎯 CORRECTION FORMAT SIMPLE ANNÉES FISCALES")
    print("=" * 50)
    print("📝 Logique: BY24 = format simple, pas de détails verbeux")
    print()
    
    try:
        db.init_database()
        
        success = fix_fiscal_year_values()
        
        print(f"\n" + "=" * 50)
        if success:
            print("🎉 CORRECTION TERMINÉE AVEC SUCCÈS!")
            print("\n✅ RÉSULTAT:")
            print("   • Format BYXX simple conservé")
            print("   • Plus de warning sur les valeurs")
            print("   • Interface clean et professionnelle")
            
            print(f"\n🚀 PROCHAINES ÉTAPES:")
            print("   1. Redémarrez Streamlit")
            print("   2. Allez dans 'Listes Déroulantes'")
            print("   3. Sélectionnez 'Année Fiscale'")
            print("   4. Vérifiez que BY24 s'affiche en vert ✅")
        else:
            print("ℹ️ AUCUNE CORRECTION NÉCESSAIRE")
            print("   Les années fiscales sont déjà au bon format")
        
        return success
        
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")
        return False

if __name__ == "__main__":
    success = main()
    print(f"\n💡 RAPPEL:")
    print(f"   Le métier connaît déjà la signification de BYXX")
    print(f"   Pas besoin de détails verbeux dans les valeurs")
    sys.exit(0 if success else 1)
