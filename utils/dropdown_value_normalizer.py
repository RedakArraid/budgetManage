"""
Utilitaire pour la normalisation des valeurs des listes déroulantes
Gère la normalisation avec règles spéciales pour les années fiscales
"""
import re
from typing import Dict, Any

def normalize_dropdown_value(label: str) -> str:
    """
    Normalise un label en valeur pour les dropdowns
    
    Règles :
    - Minuscules
    - Espaces → underscores  
    - Caractères spéciaux → underscores
    - Suppression accents
    - Pas de underscores multiples
    
    Exception : Les années fiscales gardent le format BYXX
    """
    if not label or not isinstance(label, str):
        return ""
    
    # Cas spécial : années fiscales (format BYXX)
    if is_fiscal_year_label(label):
        return extract_fiscal_year_code(label)
    
    # Normalisation standard
    value = label.lower()
    
    # Supprimer les accents
    value = remove_accents(value)
    
    # Remplacer espaces et caractères spéciaux par underscore
    value = re.sub(r'[^a-z0-9]+', '_', value)
    
    # Supprimer underscores multiples
    value = re.sub(r'_+', '_', value)
    
    # Nettoyer début/fin
    value = value.strip('_')
    
    return value

def is_fiscal_year_label(label: str) -> bool:
    """Détecte si un label représente une année fiscale"""
    if not label:
        return False
    
    # Patterns pour années fiscales
    patterns = [
        r'^BY\d{2}$',           # BY25
        r'^BY\d{2}\s*\(.*\)$',  # BY25 (2025)
        r'^\d{4}$',             # 2025
        r'^20\d{2}$'            # 2025 (plus spécifique)
    ]
    
    for pattern in patterns:
        if re.match(pattern, label.strip()):
            return True
    
    return False

def extract_fiscal_year_code(label: str) -> str:
    """Extrait le code BYXX d'un label d'année fiscale"""
    if not label:
        return ""
    
    label = label.strip()
    
    # Pattern BY25 direct
    match = re.match(r'^(BY\d{2})(?:\s*\(.*\))?$', label)
    if match:
        return match.group(1)
    
    # Pattern année complète (2025 → BY25)
    match = re.match(r'^(20)?(\d{2})$', label)
    if match:
        year_suffix = match.group(2)
        return f"BY{year_suffix}"
    
    # Fallback : utiliser la normalisation standard
    return normalize_dropdown_value_standard(label)

def normalize_dropdown_value_standard(label: str) -> str:
    """Normalisation standard sans cas spéciaux"""
    if not label:
        return ""
    
    value = label.lower()
    value = remove_accents(value)
    value = re.sub(r'[^a-z0-9]+', '_', value)
    value = re.sub(r'_+', '_', value)
    value = value.strip('_')
    
    return value

def remove_accents(text: str) -> str:
    """Supprime les accents d'un texte"""
    accent_map = {
        'à': 'a', 'á': 'a', 'â': 'a', 'ã': 'a', 'ä': 'a', 'å': 'a',
        'è': 'e', 'é': 'e', 'ê': 'e', 'ë': 'e',
        'ì': 'i', 'í': 'i', 'î': 'i', 'ï': 'i',
        'ò': 'o', 'ó': 'o', 'ô': 'o', 'õ': 'o', 'ö': 'o',
        'ù': 'u', 'ú': 'u', 'û': 'u', 'ü': 'u',
        'ç': 'c', 'ñ': 'n',
        'À': 'A', 'Á': 'A', 'Â': 'A', 'Ã': 'A', 'Ä': 'A', 'Å': 'A',
        'È': 'E', 'É': 'E', 'Ê': 'E', 'Ë': 'E',
        'Ì': 'I', 'Í': 'I', 'Î': 'I', 'Ï': 'I',
        'Ò': 'O', 'Ó': 'O', 'Ô': 'O', 'Õ': 'O', 'Ö': 'O',
        'Ù': 'U', 'Ú': 'U', 'Û': 'U', 'Ü': 'U',
        'Ç': 'C', 'Ñ': 'N'
    }
    
    for accented, unaccented in accent_map.items():
        text = text.replace(accented, unaccented)
    
    return text

def preview_normalization(label: str) -> Dict[str, Any]:
    """
    Prévisualise la normalisation d'un label
    
    Returns:
        dict: {
            'original': str,
            'normalized': str,
            'is_fiscal_year': bool,
            'valid': bool,
            'warnings': List[str]
        }
    """
    result = {
        'original': label,
        'normalized': '',
        'is_fiscal_year': False,
        'valid': False,
        'warnings': []
    }
    
    if not label or not label.strip():
        result['warnings'].append("Label vide")
        return result
    
    # Détecter si c'est une année fiscale
    result['is_fiscal_year'] = is_fiscal_year_label(label)
    
    # Normaliser
    result['normalized'] = normalize_dropdown_value(label)
    
    # Validations
    if len(result['normalized']) < 2:
        result['warnings'].append("Valeur trop courte (< 2 caractères)")
    
    if len(result['normalized']) > 50:
        result['warnings'].append("Valeur trop longue (> 50 caractères)")
    
    if not re.match(r'^[a-z0-9_]+$', result['normalized']):
        result['warnings'].append("Caractères invalides dans la valeur normalisée")
    
    if result['normalized'].startswith('_') or result['normalized'].endswith('_'):
        result['warnings'].append("La valeur ne devrait pas commencer/finir par _")
    
    if '__' in result['normalized']:
        result['warnings'].append("Underscores multiples détectés")
    
    # Validation spéciale pour années fiscales
    if result['is_fiscal_year']:
        if not re.match(r'^BY\d{2}$', result['normalized']):
            result['warnings'].append("Format année fiscale incorrect (attendu: BYXX)")
    
    result['valid'] = len(result['warnings']) == 0
    
    return result

def validate_normalized_value(value: str, category: str = None) -> Dict[str, Any]:
    """
    Valide une valeur normalisée
    
    Args:
        value: Valeur à valider
        category: Catégorie optionnelle pour validations spécifiques
        
    Returns:
        dict: {
            'valid': bool,
            'errors': List[str],
            'suggestions': List[str]
        }
    """
    result = {
        'valid': True,
        'errors': [],
        'suggestions': []
    }
    
    if not value:
        result['valid'] = False
        result['errors'].append("Valeur vide")
        return result
    
    # Validations générales
    if not re.match(r'^[a-z0-9_]+$', value):
        result['valid'] = False
        result['errors'].append("Seuls les caractères a-z, 0-9 et _ sont autorisés")
    
    if len(value) < 2:
        result['valid'] = False
        result['errors'].append("Valeur trop courte (minimum 2 caractères)")
    
    if len(value) > 50:
        result['valid'] = False
        result['errors'].append("Valeur trop longue (maximum 50 caractères)")
    
    if value.startswith('_') or value.endswith('_'):
        result['valid'] = False
        result['errors'].append("Ne doit pas commencer/finir par _")
        result['suggestions'].append(f"Suggestion: {value.strip('_')}")
    
    if '__' in value:
        result['valid'] = False
        result['errors'].append("Underscores multiples non autorisés")
        result['suggestions'].append(f"Suggestion: {re.sub(r'_+', '_', value)}")
    
    # Validations spécifiques par catégorie
    if category == 'annee_fiscale':
        if not re.match(r'^BY\d{2}$', value):
            result['valid'] = False
            result['errors'].append("Format année fiscale incorrect (attendu: BYXX)")
    
    return result

# Tests unitaires
def test_normalization():
    """Tests pour valider la normalisation"""
    test_cases = [
        # (input, expected, is_fiscal_year)
        ("Budget Marketing", "budget_marketing", False),
        ("NORD-EST", "nord_est", False),
        ("Île-de-France", "ile_de_france", False),
        ("BY25", "BY25", True),
        ("BY25 (2025)", "BY25", True),
        ("2025", "BY25", True),
        ("Test   Multiple    Spaces", "test_multiple_spaces", False),
        ("Caractères @#$% Spéciaux", "caracteres_speciaux", False),
    ]
    
    print("🧪 Tests de normalisation...")
    
    for i, (input_val, expected, is_fiscal) in enumerate(test_cases, 1):
        result = normalize_dropdown_value(input_val)
        fiscal_detected = is_fiscal_year_label(input_val)
        
        print(f"Test {i}: '{input_val}'")
        print(f"  Attendu: '{expected}' (fiscal: {is_fiscal})")
        print(f"  Obtenu:  '{result}' (fiscal: {fiscal_detected})")
        
        if result == expected and fiscal_detected == is_fiscal:
            print("  ✅ PASS")
        else:
            print("  ❌ FAIL")
        print()

if __name__ == "__main__":
    test_normalization()
