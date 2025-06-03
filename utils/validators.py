"""
Validation utilities for user input
"""
import re
from typing import Tuple, Any
from datetime import datetime, date

def validate_email(email: str) -> bool:
    """Validate email format"""
    if not email or not isinstance(email, str):
        return False
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email.strip()) is not None

def validate_password(password: str) -> Tuple[bool, str]:
    """Validate password requirements"""
    from utils.security import validate_password_strength, check_password_common
    
    if not password or not isinstance(password, str):
        return False, "Mot de passe requis"
    
    # Check strength
    is_strong, message = validate_password_strength(password)
    if not is_strong:
        return False, message
    
    # Check if password is too common
    if check_password_common(password):
        return False, "Ce mot de passe est trop commun, veuillez en choisir un autre"
    
    return True, "Mot de passe valide"

def validate_name(name: str, field_name: str = "nom") -> Tuple[bool, str]:
    """Validate name fields"""
    if not name or not isinstance(name, str):
        return False, f"{field_name.capitalize()} requis"
    
    name = name.strip()
    if len(name) < 2:
        return False, f"{field_name.capitalize()} doit contenir au moins 2 caractères"
    
    if len(name) > 50:
        return False, f"{field_name.capitalize()} ne peut pas dépasser 50 caractères"
    
    # Check for valid characters (letters, spaces, hyphens, apostrophes)
    if not re.match(r"^[a-zA-ZÀ-ÿ\s\-']+$", name):
        return False, f"{field_name.capitalize()} contient des caractères non valides"
    
    return True, f"{field_name.capitalize()} valide"

def validate_amount(amount: Any) -> Tuple[bool, str]:
    """Validate monetary amount"""
    try:
        amount_float = float(amount)
        if amount_float < 0:
            return False, "Le montant ne peut pas être négatif"
        if amount_float > 1000000:  # 1 million max
            return False, "Le montant ne peut pas dépasser 1 000 000€"
        return True, "Montant valide"
    except (ValueError, TypeError):
        return False, "Montant invalide"

def validate_date(date_str: str, field_name: str = "date") -> Tuple[bool, str]:
    """Validate date format and value"""
    if not date_str:
        return False, f"{field_name.capitalize()} requise"
    
    try:
        if isinstance(date_str, str):
            parsed_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        elif isinstance(date_str, date):
            parsed_date = date_str
        else:
            return False, f"Format de {field_name} invalide"
        
        # Check if date is not too far in the past
        if parsed_date < date.today().replace(year=date.today().year - 1):
            return False, f"La {field_name} ne peut pas être antérieure à un an"
        
        # Check if date is not too far in the future
        if parsed_date > date.today().replace(year=date.today().year + 5):
            return False, f"La {field_name} ne peut pas être postérieure à 5 ans"
        
        return True, f"{field_name.capitalize()} valide"
    except ValueError:
        return False, f"Format de {field_name} invalide (YYYY-MM-DD attendu)"

def validate_text_length(text: str, min_length: int = 0, max_length: int = 1000, 
                        field_name: str = "texte") -> Tuple[bool, str]:
    """Validate text length"""
    if not text:
        text = ""
    
    if len(text) < min_length:
        return False, f"{field_name.capitalize()} doit contenir au moins {min_length} caractères"
    
    if len(text) > max_length:
        return False, f"{field_name.capitalize()} ne peut pas dépasser {max_length} caractères"
    
    return True, f"{field_name.capitalize()} valide"

def validate_role(role: str) -> Tuple[bool, str]:
    """Validate user role"""
    valid_roles = ['admin', 'tc', 'dr', 'dr_financier', 'dg', 'marketing']
    
    if not role or role not in valid_roles:
        return False, f"Rôle invalide. Rôles valides: {', '.join(valid_roles)}"
    
    return True, "Rôle valide"

def validate_demande_type(demande_type: str) -> Tuple[bool, str]:
    """Validate demande type"""
    valid_types = ['budget', 'marketing']
    
    if not demande_type or demande_type not in valid_types:
        return False, f"Type de demande invalide. Types valides: {', '.join(valid_types)}"
    
    return True, "Type de demande valide"

def validate_status(status: str) -> Tuple[bool, str]:
    """Validate demande status"""
    valid_statuses = ['brouillon', 'en_attente_dr', 'en_attente_financier', 'validee', 'rejetee']
    
    if not status or status not in valid_statuses:
        return False, f"Statut invalide. Statuts valides: {', '.join(valid_statuses)}"
    
    return True, "Statut valide"

def sanitize_search_query(query: str) -> str:
    """Sanitize search query"""
    if not query:
        return ""
    
    # Remove special characters that could cause issues
    sanitized = re.sub(r'[^\w\s\-\.]', '', query.strip())
    
    # Limit length
    return sanitized[:100]

def validate_file_upload(file_data: Any, allowed_extensions: list = None) -> Tuple[bool, str]:
    """Validate file upload"""
    if allowed_extensions is None:
        allowed_extensions = ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.jpg', '.png']
    
    if not file_data:
        return False, "Aucun fichier sélectionné"
    
    # Check file size (assuming file_data has a size attribute)
    if hasattr(file_data, 'size') and file_data.size > 10 * 1024 * 1024:  # 10MB
        return False, "Le fichier ne peut pas dépasser 10MB"
    
    # Check file extension
    if hasattr(file_data, 'name'):
        file_ext = '.' + file_data.name.split('.')[-1].lower()
        if file_ext not in allowed_extensions:
            return False, f"Extension non autorisée. Extensions valides: {', '.join(allowed_extensions)}"
    
    return True, "Fichier valide"

def validate_phone_number(phone: str) -> Tuple[bool, str]:
    """Validate phone number (French format)"""
    if not phone:
        return True, "Numéro optionnel"  # Phone is optional
    
    # Remove spaces, dots, hyphens
    cleaned_phone = re.sub(r'[\s\.\-]', '', phone)
    
    # Check French phone number patterns
    patterns = [
        r'^0[1-9][0-9]{8}$',  # French mobile/landline
        r'^\+33[1-9][0-9]{8}$',  # International format
        r'^33[1-9][0-9]{8}$'  # International without +
    ]
    
    for pattern in patterns:
        if re.match(pattern, cleaned_phone):
            return True, "Numéro valide"
    
    return False, "Format de numéro invalide (format français attendu)"

def validate_region(region: str) -> Tuple[bool, str]:
    """Validate region name"""
    if not region:
        return True, "Région optionnelle"
    
    return validate_text_length(region, 2, 50, "région")

def validate_montant(montant: Any) -> bool:
    """Simple validation du montant (pour compatibilité)"""
    is_valid, _ = validate_amount(montant)
    return is_valid

def validate_text_field(text: str, min_length: int = 1, max_length: int = 1000) -> bool:
    """Simple validation de texte (pour compatibilité)"""
    is_valid, _ = validate_text_length(text, min_length, max_length)
    return is_valid

def validate_required_field(value: Any, field_name: str = "champ") -> Tuple[bool, str]:
    """Validate that a field is not empty"""
    if value is None or (isinstance(value, str) and not value.strip()):
        return False, f"{field_name.capitalize()} est requis"
    return True, f"{field_name.capitalize()} valide"

def validate_urgence(urgence: str) -> Tuple[bool, str]:
    """Validate urgence level"""
    valid_urgences = ['normale', 'urgent', 'critique']
    
    if not urgence or urgence not in valid_urgences:
        return False, f"Niveau d'urgence invalide. Niveaux valides: {', '.join(valid_urgences)}"
    
    return True, "Niveau d'urgence valide"
