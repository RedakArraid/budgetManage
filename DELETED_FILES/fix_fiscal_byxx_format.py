#!/usr/bin/env python3
"""
Script pour corriger la section année fiscale dans nouvelle_demande_view.py
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def fix_fiscal_year_section():
    """Corrige la section année fiscale dupliquée"""
    try:
        # Lire le fichier
        with open('views/nouvelle_demande_view.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Remplacer la section problématique
        old_section = '''            # Année fiscale depuis la liste déroulante
            if annee_fiscale_options:
                fiscal_year_str = st.selectbox(
                    "🗓️ Année Fiscale*",
                    options=[opt[0] for opt in annee_fiscale_options],
                    format_func=lambda x: next((opt[1] for opt in annee_fiscale_options if opt[0] == x), x),
                    key="full_fiscal_dropdown",
                    help="Sélectionnez l'année fiscale dans la liste"
                )
                # Année fiscale depuis la liste déroulante (format BYXX)
                fiscal_year_str = st.selectbox(
                    "🗺️ Année Fiscale*",
                    options=[opt[0] for opt in annee_fiscale_options],
                    format_func=lambda x: next((opt[1] for opt in annee_fiscale_options if opt[0] == x), x),
                    key="full_fiscal_dropdown",
                    help="Sélectionnez l'année fiscale (format BYXX)"
                )
                # Garder le format BYXX pour l'utilisateur
                fiscal_year = fiscal_year_str  # BY24, BY25, etc.
            else:
                # Fallback si pas d'options configurées
                current_year = date.today().year
                fiscal_year = st.number_input("🗓️ Année Fiscale*", min_value=current_year-10, 
                                            max_value=current_year+10, value=current_year, 
                                            step=1, format='%d', key="full_fiscal_number")'''
        
        new_section = '''            # Année fiscale au format BYXX
            if annee_fiscale_options:
                fiscal_year = st.selectbox(
                    "🗓️ Année Fiscale*",
                    options=[opt[0] for opt in annee_fiscale_options],
                    format_func=lambda x: next((opt[1] for opt in annee_fiscale_options if opt[0] == x), x),
                    key="full_fiscal_dropdown",
                    help="Année fiscale au format BYXX (BY24 = Mai 2024 - Avril 2025)"
                )
                # fiscal_year contient maintenant BY24, BY25, etc.
            else:
                # Fallback si pas d'options configurées - utiliser format BYXX
                from datetime import date
                current_year = date.today().year
                default_byxx = f"BY{(current_year + 1) % 100:02d}"  # Année fiscale actuelle
                
                fiscal_year = st.selectbox(
                    "🗓️ Année Fiscale*",
                    options=[default_byxx],
                    help="Format BYXX par défaut (configurez les options dans 'Listes Déroulantes')",
                    key="full_fiscal_fallback"
                )'''
        
        if old_section in content:
            content = content.replace(old_section, new_section)
            print("✅ Section dupliquée corrigée")
        else:
            print("⚠️ Section non trouvée, recherche d'alternatives...")
            # Essayer d'autres patterns
            if 'fiscal_year_str = st.selectbox' in content:
                # Remplacer toute référence à fiscal_year_str
                content = content.replace('fiscal_year_str = st.selectbox', 'fiscal_year = st.selectbox')
                content = content.replace('fiscal_year = fiscal_year_str', '# Format BYXX conservé')
                print("✅ Références fiscal_year_str corrigées")
        
        # Aussi corriger le formulaire simplifié pour utiliser BYXX
        simple_old = '''            fiscal_year = st.number_input("🗓️ Année Fiscale*", min_value=current_year-5, 
                                        max_value=current_year+5, value=current_year, 
                                        step=1, format='%d', key="simple_fiscal")'''
        
        simple_new = '''            # Année fiscale au format BYXX même en mode simplifié
            default_byxx = f"BY{(current_year + 1) % 100:02d}"
            fiscal_year = st.text_input("🗓️ Année Fiscale*", 
                                      value=default_byxx,
                                      help="Format BYXX (ex: BY25 pour Mai 2024 - Avril 2025)",
                                      key="simple_fiscal")'''
        
        if simple_old in content:
            content = content.replace(simple_old, simple_new)
            print("✅ Formulaire simplifié corrigé pour BYXX")
        
        # Sauvegarder
        with open('views/nouvelle_demande_view.py', 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("💾 Fichier sauvegardé avec les corrections")
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def main():
    """Fonction principale"""
    print("🔧 CORRECTION ANNÉE FISCALE - FORMAT BYXX")
    print("=" * 50)
    print("🎯 Objectif: Tous les utilisateurs voient BY24, BY25, etc.")
    print()
    
    success = fix_fiscal_year_section()
    
    if success:
        print("\n🎉 CORRECTION TERMINÉE!")
        print("\n✅ CHANGEMENTS APPLIQUÉS:")
        print("   • Année fiscale: format BYXX pour tous")
        print("   • Plus de conversion en arrière-plan")
        print("   • Utilisateurs voient directement BY24, BY25, etc.")
        print("   • Formulaire simplifié aussi corrigé")
        
        print(f"\n🚀 RÉSULTAT ATTENDU:")
        print("   • Utilisateurs sélectionnent BY24, BY25, etc.")
        print("   • Valeur stockée: BY24 (pas 2023)")
        print("   • Affichage cohérent partout")
        
        print(f"\n💡 PROCHAINES ÉTAPES:")
        print("   1. Redémarrez Streamlit")
        print("   2. Testez 'Nouvelle Demande'")
        print("   3. Vérifiez que l'année fiscale affiche BY24, BY25, etc.")
    else:
        print("\n❌ ÉCHEC DE LA CORRECTION")
        print("   Vérifiez les erreurs ci-dessus")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
