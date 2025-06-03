"""
Système d'affichage final simplifié
Maintenant que les options sont cohérentes : valeur stockée = valeur affichée
"""

def get_display_value(stored_value: str) -> str:
    """
    Nouvelle fonction ultra-simple : 
    la valeur stockée EST la valeur à afficher
    """
    return stored_value if stored_value else "Non spécifié"

def get_all_display_values(demande_data: dict) -> dict:
    """
    Récupère toutes les valeurs d'affichage pour une demande
    Version simplifiée post-correction
    """
    return {
        'budget': get_display_value(demande_data.get('budget')),
        'categorie': get_display_value(demande_data.get('categorie')),
        'typologie_client': get_display_value(demande_data.get('typologie_client')),
        'groupe_groupement': get_display_value(demande_data.get('groupe_groupement')),
        'region': get_display_value(demande_data.get('region'))
    }

# Test du nouveau système
def test_new_system():
    """Test du système simplifié"""
    
    # Exemple de données comme elles apparaissent maintenant
    test_demande = {
        'budget': 'SALES',
        'categorie': 'ANIMATION CLIENT',
        'typologie_client': 'INDEPENDANT',
        'groupe_groupement': 'REXEL',
        'region': 'NORD EST'
    }
    
    display_values = get_all_display_values(test_demande)
    
    print("🧪 TEST DU NOUVEAU SYSTÈME:")
    for field, value in display_values.items():
        print(f"   {field}: {value}")
    
    print("\n✅ Plus besoin de mapping complexe !")
    print("✅ Valeur stockée = Valeur affichée")

if __name__ == "__main__":
    test_new_system()
