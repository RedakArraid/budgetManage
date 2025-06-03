"""
Security utilities for password hashing and validation
"""
import bcrypt
import re
from typing import Tuple

def hash_password(password: str) -> bytes:
    """Hash a password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

def verify_password(password: str, hashed: bytes) -> bool:
    """Verify a password against its hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed)

def generate_secure_password(length: int = 12) -> str:
    """Generate a secure random password"""
    import secrets
    import string
    
    # Ensure we have at least one of each character type
    password = [
        secrets.choice(string.ascii_lowercase),
        secrets.choice(string.ascii_uppercase),
        secrets.choice(string.digits),
        secrets.choice('!@#$%^&*')
    ]
    
    # Fill the rest with random characters
    all_chars = string.ascii_letters + string.digits + '!@#$%^&*'
    for _ in range(length - 4):
        password.append(secrets.choice(all_chars))
    
    # Shuffle the password
    secrets.SystemRandom().shuffle(password)
    return ''.join(password)

def validate_password_strength(password: str) -> Tuple[bool, str]:
    """Validate password strength"""
    if len(password) < 8:
        return False, "Le mot de passe doit contenir au moins 8 caractères"
    
    if not re.search(r'[A-Z]', password):
        return False, "Le mot de passe doit contenir au moins une majuscule"
    
    if not re.search(r'[a-z]', password):
        return False, "Le mot de passe doit contenir au moins une minuscule"
    
    if not re.search(r'\d', password):
        return False, "Le mot de passe doit contenir au moins un chiffre"
    
    # Optional: check for special characters
    if len(password) >= 12 and not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Pour un mot de passe de 12+ caractères, un caractère spécial est recommandé"
    
    return True, "Mot de passe valide"

def check_password_common(password: str) -> bool:
    """Check if password is in common passwords list"""
    # Simple check against most common passwords
    common_passwords = {
        'password', '123456', '123456789', 'qwerty', 'abc123',
        'password123', 'admin', 'letmein', 'welcome', 'monkey'
    }
    return password.lower() in common_passwords

def sanitize_input(input_str: str) -> str:
    """Sanitize user input to prevent injection attacks"""
    if not isinstance(input_str, str):
        return str(input_str)
    
    # Remove potential SQL injection characters
    dangerous_chars = ["'", '"', ';', '--', '/*', '*/', 'xp_', 'sp_']
    
    sanitized = input_str
    for char in dangerous_chars:
        sanitized = sanitized.replace(char, '')
    
    return sanitized.strip()

def mask_email(email: str) -> str:
    """Mask email for display purposes"""
    if '@' not in email:
        return email
    
    local, domain = email.split('@', 1)
    if len(local) <= 2:
        masked_local = local
    else:
        masked_local = local[0] + '*' * (len(local) - 2) + local[-1]
    
    return f"{masked_local}@{domain}"

def generate_session_token() -> str:
    """Generate a secure session token"""
    import secrets
    return secrets.token_urlsafe(32)
