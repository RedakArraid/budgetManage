"""
Utilitaires pour la conversion des années fiscales format BYXX
LOGIQUE MÉTIER: Année fiscale = Mai N-1 à Avril N
Exemple: BY25 = Mai 2024 à Avril 2025
"""

def byxx_to_year(byxx_value):
    """
    Convertit le format BYXX en année de début de période fiscale
    ATTENTION: BY25 = période Mai 2024 → Avril 2025, donc année de début = 2024
    
    Args:
        byxx_value (str): Valeur au format BYXX (ex: 'BY25')
        
    Returns:
        int: Année de début de la période fiscale (ex: BY25 → 2024)
    """
    if not byxx_value or not isinstance(byxx_value, str):
        return None
    
    # Si c'est déjà un nombre (rétrocompatibilité)
    if byxx_value.isdigit():
        return int(byxx_value)
    
    # Si c'est le format BYXX
    if byxx_value.startswith('BY') and len(byxx_value) == 4:
        try:
            year_suffix = byxx_value[2:]  # Récupérer 'XX' de 'BYXX'
            year_num = int(year_suffix)
            
            # LOGIQUE ANNÉE FISCALE: BYXX commence en mai de l'année (XX-1)
            # BY25 = Mai 2024 → Avril 2025, donc on retourne 2024
            # BY24 = Mai 2023 → Avril 2024, donc on retourne 2023
            
            if year_num <= 50:  # 00-50 → 2000-2050
                fiscal_start_year = 2000 + year_num - 1
            else:  # 51-99 → 1950-1999
                fiscal_start_year = 1900 + year_num - 1
                
            return fiscal_start_year
                
        except ValueError:
            return None
    
    return None

def year_to_byxx(start_year):
    """
    Convertit une année de début de période fiscale en format BYXX
    Exemple: 2024 (début) → BY25 (car période 2024-2025)
    
    Args:
        start_year (int): Année de début de période fiscale (ex: 2024)
        
    Returns:
        str: Valeur au format BYXX (ex: 'BY25')
    """
    if not start_year or not isinstance(start_year, int):
        return None
    
    # LOGIQUE ANNÉE FISCALE: 
    # Si l'année fiscale commence en 2024, elle se termine en 2025
    # donc BY25 (car on nomme par l'année de fin)
    end_year = start_year + 1
    year_suffix = end_year % 100
    return f"BY{year_suffix:02d}"

def get_fiscal_year_display(byxx_value):
    """
    Retourne l'affichage complet d'une année fiscale
    Exemple: BY25 → "BY25 (Mai 2024 - Avril 2025)"
    
    Args:
        byxx_value (str): Valeur au format BYXX
        
    Returns:
        str: Affichage complet avec période
    """
    start_year = byxx_to_year(byxx_value)
    if start_year:
        end_year = start_year + 1
        return f"{byxx_value} (Mai {start_year} - Avril {end_year})"
    return str(byxx_value)

def get_fiscal_year_from_date(date_obj):
    """
    Détermine l'année fiscale BYXX à partir d'une date
    
    Args:
        date_obj: Date (datetime.date ou string)
        
    Returns:
        str: Code BYXX correspondant (ex: 'BY25')
    """
    from datetime import datetime
    
    if isinstance(date_obj, str):
        try:
            date_obj = datetime.strptime(date_obj, '%Y-%m-%d').date()
        except ValueError:
            try:
                date_obj = datetime.strptime(date_obj, '%d/%m/%Y').date()
            except ValueError:
                return None
    
    # L'année fiscale commence en mai
    if date_obj.month >= 5:  # Mai à décembre
        # On est dans l'année fiscale qui commence cette année
        start_year = date_obj.year
    else:  # Janvier à avril
        # On est dans l'année fiscale qui a commencé l'année précédente
        start_year = date_obj.year - 1
    
    return year_to_byxx(start_year)

def validate_fiscal_year_format(value):
    """
    Valide qu'une valeur est au bon format d'année fiscale
    
    Args:
        value (str): Valeur à valider
        
    Returns:
        tuple: (is_valid, converted_year, error_message)
    """
    if not value:
        return False, None, "Valeur vide"
    
    # Tenter la conversion
    start_year = byxx_to_year(value)
    
    if start_year is None:
        return False, None, f"Format invalide: {value}"
    
    # Vérifier que l'année est dans une plage raisonnable
    if start_year < 2000 or start_year > 2050:
        return False, start_year, f"Année hors plage acceptable: {start_year}"
    
    return True, start_year, None

def get_current_fiscal_year():
    """
    Retourne l'année fiscale actuelle basée sur la date d'aujourd'hui
    
    Returns:
        str: Code BYXX de l'année fiscale actuelle
    """
    from datetime import date
    return get_fiscal_year_from_date(date.today())

def list_fiscal_years(start_year, end_year):
    """
    Génère une liste d'années fiscales entre deux années de début
    
    Args:
        start_year (int): Année de début de la première période
        end_year (int): Année de début de la dernière période
        
    Returns:
        list: Liste de tuples (byxx_code, display_name, start_year, end_year)
    """
    fiscal_years = []
    
    for year in range(start_year, end_year + 1):
        byxx_code = year_to_byxx(year)
        display_name = get_fiscal_year_display(byxx_code)
        fiscal_years.append((byxx_code, display_name, year, year + 1))
    
    return fiscal_years

# Tests unitaires
if __name__ == "__main__":
    print("🧪 Tests des utilitaires d'années fiscales")
    print("=" * 50)
    print("📋 LOGIQUE: BY25 = Mai 2024 → Avril 2025")
    print()
    
    # Tests de conversion BYXX → année de début
    print("🔄 Tests BYXX → Année de début:")
    test_cases_byxx = [
        ("BY25", 2024),  # BY25 = Mai 2024 → Avril 2025
        ("BY24", 2023),  # BY24 = Mai 2023 → Avril 2024
        ("BY26", 2025),  # BY26 = Mai 2025 → Avril 2026
        ("BY20", 2019),  # BY20 = Mai 2019 → Avril 2020
    ]
    
    for byxx, expected_start in test_cases_byxx:
        result = byxx_to_year(byxx)
        status = "✅" if result == expected_start else "❌"
        print(f"   {status} {byxx} → {result} (attendu: {expected_start})")
    
    # Tests de conversion année de début → BYXX
    print(f"\n🔄 Tests Année de début → BYXX:")
    test_cases_year = [
        (2024, "BY25"),  # 2024-2025 → BY25
        (2023, "BY24"),  # 2023-2024 → BY24
        (2025, "BY26"),  # 2025-2026 → BY26
    ]
    
    for start_year, expected_byxx in test_cases_year:
        result = year_to_byxx(start_year)
        status = "✅" if result == expected_byxx else "❌"
        print(f"   {status} {start_year} → {result} (attendu: {expected_byxx})")
    
    # Tests d'affichage
    print(f"\n📋 Tests d'affichage:")
    display_tests = ["BY25", "BY24", "BY26"]
    for byxx in display_tests:
        display = get_fiscal_year_display(byxx)
        print(f"   • {byxx} → {display}")
    
    # Tests de dates
    print(f"\n📅 Tests de dates:")
    from datetime import date
    date_tests = [
        ("2024-06-15", "BY25"),  # Juin 2024 → BY25 (Mai 2024 - Avril 2025)
        ("2024-03-15", "BY24"),  # Mars 2024 → BY24 (Mai 2023 - Avril 2024)
        ("2024-05-01", "BY25"),  # Mai 2024 → BY25 (Mai 2024 - Avril 2025)
        ("2025-04-30", "BY25"),  # Avril 2025 → BY25 (Mai 2024 - Avril 2025)
    ]
    
    for date_str, expected_byxx in date_tests:
        result = get_fiscal_year_from_date(date_str)
        status = "✅" if result == expected_byxx else "❌"
        print(f"   {status} {date_str} → {result} (attendu: {expected_byxx})")
    
    print(f"\n✅ Tests terminés")
    print(f"\n📋 RAPPEL DE LA LOGIQUE:")
    print(f"   BY25 = Période fiscale Mai 2024 → Avril 2025")
    print(f"   BY24 = Période fiscale Mai 2023 → Avril 2024")
    print(f"   BY26 = Période fiscale Mai 2025 → Avril 2026")
