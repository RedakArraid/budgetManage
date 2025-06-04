"""
Validateurs pour l'application BudgetManage - Version Corrigée
"""
import re
from typing import Tuple, List
from datetime import datetime

def validate_email(email: str) -> bool:
    """
    Valider un format d'email
    
    Args:
        email: L'email à valider
        
    Returns:
        bool: True si l'email est valide
    """
    if not email or not isinstance(email, str):
        return False
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email.strip()))

def validate_password(password: str) -> bool:
    """
    Valider un mot de passe selon les critères de sécurité
    
    Critères:
    - Minimum 8 caractères
    - Au moins 1 lettre majuscule
    - Au moins 1 lettre minuscule
    - Au moins 1 chiffre
    - Au moins 1 caractère spécial
    
    Args:
        password: Le mot de passe à valider
        
    Returns:
        bool: True si le mot de passe respecte tous les critères
    """
    if not password or not isinstance(password, str):
        return False
    
    # Longueur minimum
    if len(password) < 8:
        return False
    
    # Au moins une lettre majuscule
    if not re.search(r'[A-Z]', password):
        return False
    
    # Au moins une lettre minuscule
    if not re.search(r'[a-z]', password):
        return False
    
    # Au moins un chiffre
    if not re.search(r'\d', password):
        return False
    
    # Au moins un caractère spécial
    if not re.search(r'[!@#$%^&*(),.?":{}|<>_\-+=\[\]\\\/~`]', password):
        return False
    
    return True

def get_password_requirements() -> str:
    """
    Obtenir la description des critères de mot de passe
    
    Returns:
        str: Description formatée des critères
    """
    return """
    **Critères requis pour le mot de passe :**
    • Au moins 8 caractères
    • Une lettre majuscule (A-Z)
    • Une lettre minuscule (a-z)
    • Un chiffre (0-9)
    • Un caractère spécial (!@#$%^&*(),.?":{}|<>_-+=[]\\\/~`)
    """

def validate_password_strength(password: str) -> Tuple[bool, List[str]]:
    """
    Valider la force d'un mot de passe et retourner les erreurs spécifiques
    
    Args:
        password: Le mot de passe à valider
        
    Returns:
        Tuple[bool, List[str]]: (is_valid, list_of_errors)
    """
    errors = []
    
    if not password or not isinstance(password, str):
        errors.append("Le mot de passe ne peut pas être vide")
        return False, errors
    
    if len(password) < 8:
        errors.append("Le mot de passe doit contenir au moins 8 caractères")
    
    if not re.search(r'[A-Z]', password):
        errors.append("Le mot de passe doit contenir au moins une lettre majuscule")
    
    if not re.search(r'[a-z]', password):
        errors.append("Le mot de passe doit contenir au moins une lettre minuscule")
    
    if not re.search(r'\d', password):
        errors.append("Le mot de passe doit contenir au moins un chiffre")
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>_\-+=\[\]\\\/~`]', password):
        errors.append("Le mot de passe doit contenir au moins un caractère spécial")
    
    return len(errors) == 0, errors

def validate_name(name: str, field_name: str = "nom") -> bool:
    """
    Valider un nom (nom, prénom, etc.)
    
    Args:
        name: Le nom à valider
        field_name: Le nom du champ (pour les messages d'erreur)
        
    Returns:
        bool: True si le nom est valide
    """
    if not name or not isinstance(name, str):
        return False
    
    name = name.strip()
    
    # Longueur minimum et maximum
    if len(name) < 2 or len(name) > 50:
        return False
    
    # Caractères autorisés (lettres, espaces, tirets, apostrophes)
    if not re.match(r"^[a-zA-ZÀ-ÿ\s\-']+$", name):
        return False
    
    return True

def validate_amount(amount: str) -> Tuple[bool, float]:
    """
    Valider un montant financier
    
    Args:
        amount: Le montant à valider (en string)
        
    Returns:
        Tuple[bool, float]: (is_valid, parsed_amount)
    """
    try:
        if not amount:
            return False, 0.0
        
        # Remplacer les virgules par des points pour le format français
        amount_str = str(amount).replace(',', '.').strip()
        
        # Enlever les espaces et les symboles de devise
        amount_str = re.sub(r'[€$\s]', '', amount_str)
        
        parsed_amount = float(amount_str)
        
        # Vérifier que le montant est positif et raisonnable
        if parsed_amount <= 0 or parsed_amount > 1000000:  # Max 1M€
            return False, 0.0
        
        return True, parsed_amount
        
    except (ValueError, TypeError):
        return False, 0.0

def validate_date(date_str: str) -> bool:
    """
    Valider une date au format français ou ISO
    
    Args:
        date_str: La date à valider
        
    Returns:
        bool: True si la date est valide
    """
    if not date_str:
        return False
    
    formats = ['%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y']
    
    for fmt in formats:
        try:
            datetime.strptime(date_str, fmt)
            return True
        except ValueError:
            continue
    
    return False

def validate_phone(phone: str) -> bool:
    """
    Valider un numéro de téléphone français
    
    Args:
        phone: Le numéro à valider
        
    Returns:
        bool: True si le numéro est valide
    """
    if not phone:
        return False
    
    # Nettoyer le numéro (enlever espaces, tirets, points)
    clean_phone = re.sub(r'[\s\-\.]', '', phone)
    
    # Formats acceptés : 0123456789, +33123456789, 33123456789
    patterns = [
        r'^0[1-9](\d{8})$',  # Format français 01 23 45 67 89
        r'^\+33[1-9](\d{8})$',  # Format international +33 1 23 45 67 89
        r'^33[1-9](\d{8})$'   # Format international sans + 
    ]
    
    return any(re.match(pattern, clean_phone) for pattern in patterns)

def sanitize_string(text: str, max_length: int = 255) -> str:
    """
    Nettoyer et sécuriser une chaîne de caractères
    
    Args:
        text: Le texte à nettoyer
        max_length: Longueur maximale autorisée
        
    Returns:
        str: Texte nettoyé
    """
    if not text:
        return ""
    
    # Enlever les caractères de contrôle et les espaces en début/fin
    cleaned = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', str(text)).strip()
    
    # Limiter la longueur
    if len(cleaned) > max_length:
        cleaned = cleaned[:max_length]
    
    return cleaned

def validate_url(url: str) -> bool:
    """
    Valider une URL
    
    Args:
        url: L'URL à valider
        
    Returns:
        bool: True si l'URL est valide
    """
    if not url:
        return False
    
    url_pattern = re.compile(
        r'^https?://'  # http:// ou https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domaine
        r'localhost|'  # localhost
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # IP
        r'(?::\d+)?'  # port optionnel
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    return bool(url_pattern.match(url))
