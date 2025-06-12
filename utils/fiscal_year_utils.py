"""
Utilitaires pour la validation et gestion des années fiscales
"""
from typing import List, Tuple, Optional
from models.dropdown_options import DropdownOptionsModel

def validate_fiscal_year(by_value: str) -> bool:
    """
    Valide qu'une année fiscale est autorisée selon les options configurées par l'admin
    
    Args:
        by_value: Valeur année fiscale format BYXX (ex: BY25)
        
    Returns:
        bool: True si l'année est autorisée, False sinon
    """
    try:
        if not by_value or not isinstance(by_value, str):
            return False
            
        # Récupérer les années fiscales valides depuis la base directement
        from models.database import db
        
        result = db.execute_query('''
            SELECT COUNT(*) as count
            FROM dropdown_options 
            WHERE category = 'annee_fiscale' 
            AND value = ? 
            AND is_active = TRUE
        ''', (by_value,), fetch='one')
        
        return result['count'] > 0 if result else False
        
    except Exception as e:
        print(f"Erreur validation année fiscale: {e}")
        return False

def get_valid_fiscal_years() -> List[Tuple[str, str]]:
    """
    Récupère les années fiscales valides pour les dropdowns depuis la configuration admin
    
    Returns:
        List[Tuple[str, str]]: Liste de tuples (value, label) des années fiscales actives
    """
    try:
        from models.database import db
        
        options = db.execute_query('''
            SELECT value, label, order_index 
            FROM dropdown_options 
            WHERE category = 'annee_fiscale' AND is_active = TRUE
            ORDER BY order_index ASC, value ASC
        ''', fetch='all')
        
        if options:
            # Convertir les Row objects en tuples
            active_options = [(row['value'], row['label']) for row in options]
            return active_options
        else:
            # Fallback avec années par défaut
            from datetime import datetime
            current_year = datetime.now().year
            default_by = f"BY{str(current_year)[2:]}"
            return [(default_by, f"{default_by} ({current_year})")]
            
    except Exception as e:
        print(f"Erreur récupération années fiscales: {e}")
        # Fallback avec années par défaut
        from datetime import datetime
        current_year = datetime.now().year
        default_by = f"BY{str(current_year)[2:]}"
        return [(default_by, f"{default_by} ({current_year})")]

def get_default_fiscal_year() -> str:
    """
    Récupère l'année fiscale par défaut (première dans la liste ou année courante)
    
    Returns:
        str: Code année fiscale par défaut (format BYXX)
    """
    try:
        valid_years = get_valid_fiscal_years()
        if valid_years:
            return valid_years[0][0]  # Première année dans la liste
        else:
            # Fallback sur année courante
            from datetime import datetime
            current_year = datetime.now().year
            return f"BY{str(current_year)[2:]}"
    except Exception:
        return "BY25"  # Fallback absolu

def format_fiscal_year_label(by_value: str) -> str:
    """
    Formate un code année fiscale en libellé lisible
    
    Args:
        by_value: Code année fiscale (ex: BY25)
        
    Returns:
        str: Libellé formaté (ex: BY25 - simple, sans parenthèses)
    """
    try:
        if not by_value or len(by_value) != 4 or not by_value.startswith('BY'):
            return by_value
        
        # Format simple : BY25 (pas de parenthèses)
        return by_value
    except Exception:
        return by_value

def get_fiscal_year_from_date(date_evenement) -> Optional[str]:
    """
    FONCTION DÉPRÉCIÉE - Ne plus utiliser
    Les années fiscales doivent être saisies manuellement depuis les dropdowns admin
    
    Cette fonction est conservée pour compatibilité mais retourne None
    """
    print("⚠️ ATTENTION: get_fiscal_year_from_date est déprécié. Utilisez les dropdowns admin.")
    return None

def validate_fiscal_year_format(by_value: str) -> bool:
    """
    Valide le format d'une année fiscale (BYXX)
    
    Args:
        by_value: Valeur à valider
        
    Returns:
        bool: True si le format est correct
    """
    try:
        if not by_value or not isinstance(by_value, str):
            return False
            
        # Format BYXX où XX sont 2 chiffres
        if len(by_value) != 4:
            return False
            
        if not by_value.startswith('BY'):
            return False
            
        suffix = by_value[2:]
        if not suffix.isdigit():
            return False
            
        # Vérifier que l'année est dans une plage raisonnable (20xx)
        year_num = int(suffix)
        if year_num < 20 or year_num > 99:
            return False
            
        return True
    except Exception:
        return False

def create_fiscal_year_option(year: int) -> Tuple[str, str]:
    """
    Crée une option d'année fiscale à partir d'une année
    
    Args:
        year: Année (ex: 2025)
        
    Returns:
        Tuple[str, str]: (value, label) pour l'option - format simple
    """
    try:
        if year < 2020 or year > 2099:
            raise ValueError(f"Année {year} hors de la plage autorisée (2020-2099)")
            
        by_value = f"BY{str(year)[2:]}"
        by_label = by_value  # Label simple : BY25
        
        return by_value, by_label
    except Exception as e:
        print(f"Erreur création option année fiscale: {e}")
        return "", ""

def byxx_to_year(by_value: str) -> Optional[int]:
    """
    Convertit un code année fiscale BYXX en année entière
    
    Args:
        by_value: Code année fiscale (ex: BY25)
        
    Returns:
        Optional[int]: Année entière (ex: 2025) ou None si invalide
    """
    try:
        if not by_value or not isinstance(by_value, str):
            return None
            
        if not validate_fiscal_year_format(by_value):
            return None
            
        # Extraire les 2 derniers chiffres et convertir en année complète
        year_suffix = by_value[2:]
        year_int = int(year_suffix)
        
        # Assumer que 00-99 correspondent à 2000-2099
        full_year = 2000 + year_int
        
        return full_year
        
    except Exception:
        return None

def year_to_byxx(year: int) -> Optional[str]:
    """
    Convertit une année entière en code année fiscale BYXX
    
    Args:
        year: Année entière (ex: 2025)
        
    Returns:
        Optional[str]: Code année fiscale (ex: BY25) ou None si invalide
    """
    try:
        if year < 2000 or year > 2099:
            return None
            
        year_suffix = str(year)[2:]  # 2025 → 25
        by_code = f"BY{year_suffix}"
        
        return by_code
        
    except Exception:
        return None
def ensure_fiscal_years_exist():
    """
    S'assure que des années fiscales par défaut existent dans les dropdowns
    Utilisé lors des migrations ou de l'initialisation
    """
    try:
        from models.database import db
        from datetime import datetime
        
        # Vérifier si des années fiscales existent déjà
        existing_count = db.execute_query("""
            SELECT COUNT(*) as count
            FROM dropdown_options 
            WHERE category = 'annee_fiscale' AND is_active = TRUE
        """, fetch='one')
        
        if existing_count and existing_count['count'] > 0:
            return True  # Des années existent déjà
        
        # Créer des années par défaut autour de l'année courante
        current_year = datetime.now().year
        years_to_create = range(current_year - 2, current_year + 5)  # 7 années
        
        for i, year in enumerate(years_to_create):
            by_value, by_label = create_fiscal_year_option(year)
            if by_value:
                db.execute_query("""
                    INSERT OR IGNORE INTO dropdown_options 
                    (category, value, label, order_index, is_active)
                    VALUES (?, ?, ?, ?, TRUE)
                """, ('annee_fiscale', by_value, by_label, i + 1))
        
        print(f"✅ {len(years_to_create)} années fiscales par défaut créées")
        return True
        
    except Exception as e:
        print(f"❌ Erreur création années fiscales par défaut: {e}")
        return False
