"""
Fonction utilitaire pour la normalisation automatique des valeurs de listes déroulantes
Applique la logique : value = replace(lower(label), espaces par _)
"""
import re

def normalize_dropdown_value(label: str) -> str:
    """
    Normalise un label en valeur stockée selon la règle :
    value = replace(lower(label), espaces par _)
    + nettoyage caractères spéciaux
    
    Args:
        label (str): Le label saisi par l'utilisateur
        
    Returns:
        str: La valeur normalisée pour stockage en base
    """
    if not label or not isinstance(label, str):
        return ""
    
    # 1. Supprimer les espaces en début/fin
    value = label.strip()
    
    if not value:
        return ""
    
    # 2. Mettre en minuscules
    value = value.lower()
    
    # 3. Remplacer les espaces par des underscores
    value = value.replace(' ', '_')
    
    # 4. Remplacer d'autres caractères problématiques par des underscores
    value = value.replace('-', '_')
    value = value.replace('/', '_')
    value = value.replace('\\', '_')
    value = value.replace('.', '_')
    value = value.replace(',', '_')
    value = value.replace(';', '_')
    value = value.replace(':', '_')
    
    # 5. Supprimer les caractères de ponctuation
    value = value.replace('(', '')
    value = value.replace(')', '')
    value = value.replace('[', '')
    value = value.replace(']', '')
    value = value.replace('{', '')
    value = value.replace('}', '')
    value = value.replace("'", '')
    value = value.replace('"', '')
    value = value.replace('!', '')
    value = value.replace('?', '')
    value = value.replace('&', '_et_')
    value = value.replace('+', '_plus_')
    value = value.replace('=', '_egal_')
    value = value.replace('%', '_pourcent')
    value = value.replace('€', '_euro')
    value = value.replace('$', '_dollar')
    
    # 6. Remplacer les caractères accentués
    replacements = {
        'à': 'a', 'á': 'a', 'â': 'a', 'ã': 'a', 'ä': 'a', 'å': 'a', 'æ': 'ae',
        'ç': 'c',
        'è': 'e', 'é': 'e', 'ê': 'e', 'ë': 'e',
        'ì': 'i', 'í': 'i', 'î': 'i', 'ï': 'i',
        'ð': 'd', 'ñ': 'n',
        'ò': 'o', 'ó': 'o', 'ô': 'o', 'õ': 'o', 'ö': 'o', 'ø': 'o',
        'ù': 'u', 'ú': 'u', 'û': 'u', 'ü': 'u',
        'ý': 'y', 'þ': 'th', 'ÿ': 'y'
    }
    
    for accented, replacement in replacements.items():
        value = value.replace(accented, replacement)
    
    # 7. Supprimer tous les caractères qui ne sont pas alphanumériques ou underscores
    value = re.sub(r'[^a-z0-9_]', '', value)
    
    # 8. Supprimer les underscores multiples et en début/fin
    value = re.sub(r'_+', '_', value)
    value = value.strip('_')
    
    # 9. S'assurer qu'on a au moins quelque chose de valide
    if not value:
        value = "option_vide"
    
    # 10. Limiter la longueur (optionnel)
    if len(value) > 50:
        value = value[:50].rstrip('_')
    
    return value

def validate_normalized_value(value: str) -> bool:
    """
    Valide qu'une valeur normalisée respecte les règles
    
    Args:
        value (str): La valeur à valider
        
    Returns:
        bool: True si la valeur est valide
    """
    if not value or not isinstance(value, str):
        return False
    
    # Vérifier la longueur
    if len(value) < 1 or len(value) > 50:
        return False
    
    # Vérifier le format (uniquement lettres, chiffres, underscores)
    if not re.match(r'^[a-z0-9_]+$', value):
        return False
    
    # Vérifier qu'elle ne commence ou ne finit pas par un underscore
    if value.startswith('_') or value.endswith('_'):
        return False
    
    # Vérifier qu'elle ne contient pas d'underscores doubles
    if '__' in value:
        return False
    
    return True

def preview_normalization(label: str) -> dict:
    """
    Aperçu de la normalisation d'un label
    
    Args:
        label (str): Le label à normaliser
        
    Returns:
        dict: Informations sur la normalisation
    """
    if not label:
        return {
            'original': '',
            'normalized': '',
            'valid': False,
            'warnings': ['Le label est vide']
        }
    
    normalized = normalize_dropdown_value(label)
    valid = validate_normalized_value(normalized)
    
    warnings = []
    if not valid:
        warnings.append('La valeur normalisée n\'est pas valide')
    
    if len(label) != len(normalized):
        warnings.append('Des caractères ont été supprimés ou modifiés')
    
    if label.lower() != normalized.replace('_', ' '):
        warnings.append('La structure du texte a été modifiée')
    
    return {
        'original': label,
        'normalized': normalized,
        'valid': valid,
        'warnings': warnings,
        'length_original': len(label),
        'length_normalized': len(normalized)
    }

# Tests unitaires pour la fonction
if __name__ == "__main__":
    print("🧪 Tests de normalisation des valeurs dropdown")
    print("=" * 50)
    
    test_cases = [
        # Cas simples
        "Budget Marketing",
        "NORD EST", 
        "Sud-Ouest",
        
        # Cas avec caractères spéciaux
        "Île-de-France",
        "Salon/Foire",
        "Client (VIP)",
        "Budget Comm'",
        "Animation: Client Premium",
        
        # Cas avec ponctuation
        "Grande Distribution & Retail",
        "Coût = 50% du budget",
        "Revenue + 10€",
        
        # Cas limites
        "",
        "   ",
        "a",
        "A" * 60,  # Très long
        "éàùçñ",   # Accents
        "123-ABC",
        "Test___Multiple___Underscores",
    ]
    
    for test_case in test_cases:
        result = preview_normalization(test_case)
        
        print(f"\n📝 Test: '{test_case}'")
        print(f"   -> '{result['normalized']}'")
        print(f"   Valide: {'✅' if result['valid'] else '❌'}")
        
        if result['warnings']:
            for warning in result['warnings']:
                print(f"   ⚠️ {warning}")
    
    print(f"\n✅ Tests terminés")
