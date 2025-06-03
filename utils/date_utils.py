"""
Date and time utilities
"""
from datetime import datetime, date, timedelta
from typing import Optional, Union
import locale

def format_date(date_obj: Union[date, datetime, str], format_type: str = 'short') -> str:
    """Format date for display"""
    if isinstance(date_obj, str):
        try:
            date_obj = datetime.strptime(date_obj, '%Y-%m-%d').date()
        except ValueError:
            try:
                date_obj = datetime.strptime(date_obj[:10], '%Y-%m-%d').date()
            except ValueError:
                return date_obj
    
    if isinstance(date_obj, datetime):
        date_obj = date_obj.date()
    
    if not isinstance(date_obj, date):
        return str(date_obj)
    
    if format_type == 'short':
        return date_obj.strftime('%d/%m/%Y')
    elif format_type == 'long':
        try:
            # Try to use French locale
            locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8')
            return date_obj.strftime('%A %d %B %Y')
        except locale.Error:
            # Fallback to English
            return date_obj.strftime('%A %d %B %Y')
    elif format_type == 'iso':
        return date_obj.isoformat()
    else:
        return date_obj.strftime(format_type)

def format_datetime(datetime_obj: Union[datetime, str], format_type: str = 'short') -> str:
    """Format datetime for display"""
    if isinstance(datetime_obj, str):
        try:
            datetime_obj = datetime.fromisoformat(datetime_obj.replace('Z', '+00:00'))
        except ValueError:
            return datetime_obj
    
    if not isinstance(datetime_obj, datetime):
        return str(datetime_obj)
    
    if format_type == 'short':
        return datetime_obj.strftime('%d/%m/%Y %H:%M')
    elif format_type == 'long':
        try:
            locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8')
            return datetime_obj.strftime('%A %d %B %Y à %H:%M')
        except locale.Error:
            return datetime_obj.strftime('%A %d %B %Y at %H:%M')
    elif format_type == 'time_only':
        return datetime_obj.strftime('%H:%M')
    elif format_type == 'iso':
        return datetime_obj.isoformat()
    else:
        return datetime_obj.strftime(format_type)

def get_relative_time(datetime_obj: Union[datetime, str]) -> str:
    """Get relative time (e.g., 'il y a 2 heures')"""
    if isinstance(datetime_obj, str):
        try:
            datetime_obj = datetime.fromisoformat(datetime_obj.replace('Z', '+00:00'))
        except ValueError:
            return datetime_obj
    
    if not isinstance(datetime_obj, datetime):
        return str(datetime_obj)
    
    now = datetime.now()
    diff = now - datetime_obj
    
    if diff.days > 0:
        if diff.days == 1:
            return "hier"
        elif diff.days < 7:
            return f"il y a {diff.days} jours"
        elif diff.days < 30:
            weeks = diff.days // 7
            return f"il y a {weeks} semaine{'s' if weeks > 1 else ''}"
        elif diff.days < 365:
            months = diff.days // 30
            return f"il y a {months} mois"
        else:
            years = diff.days // 365
            return f"il y a {years} an{'s' if years > 1 else ''}"
    
    hours = diff.seconds // 3600
    if hours > 0:
        return f"il y a {hours} heure{'s' if hours > 1 else ''}"
    
    minutes = diff.seconds // 60
    if minutes > 0:
        return f"il y a {minutes} minute{'s' if minutes > 1 else ''}"
    
    return "à l'instant"

def get_business_days_between(start_date: date, end_date: date) -> int:
    """Calculate business days between two dates"""
    business_days = 0
    current_date = start_date
    
    while current_date <= end_date:
        if current_date.weekday() < 5:  # Monday to Friday
            business_days += 1
        current_date += timedelta(days=1)
    
    return business_days

def is_business_day(check_date: date) -> bool:
    """Check if a date is a business day"""
    return check_date.weekday() < 5

def get_next_business_day(from_date: Optional[date] = None) -> date:
    """Get next business day"""
    if from_date is None:
        from_date = date.today()
    
    next_day = from_date + timedelta(days=1)
    while not is_business_day(next_day):
        next_day += timedelta(days=1)
    
    return next_day

def get_month_boundaries(year: int, month: int) -> tuple[date, date]:
    """Get first and last day of a month"""
    first_day = date(year, month, 1)
    
    if month == 12:
        last_day = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        last_day = date(year, month + 1, 1) - timedelta(days=1)
    
    return first_day, last_day

def get_quarter_boundaries(year: int, quarter: int) -> tuple[date, date]:
    """Get first and last day of a quarter"""
    if quarter == 1:
        return date(year, 1, 1), date(year, 3, 31)
    elif quarter == 2:
        return date(year, 4, 1), date(year, 6, 30)
    elif quarter == 3:
        return date(year, 7, 1), date(year, 9, 30)
    elif quarter == 4:
        return date(year, 10, 1), date(year, 12, 31)
    else:
        raise ValueError("Quarter must be 1, 2, 3, or 4")

def parse_date_range(date_range: str) -> tuple[Optional[date], Optional[date]]:
    """Parse date range string like '2024-01-01 to 2024-12-31'"""
    if not date_range or ' to ' not in date_range:
        return None, None
    
    try:
        start_str, end_str = date_range.split(' to ')
        start_date = datetime.strptime(start_str.strip(), '%Y-%m-%d').date()
        end_date = datetime.strptime(end_str.strip(), '%Y-%m-%d').date()
        return start_date, end_date
    except ValueError:
        return None, None

def get_time_ago_string(datetime_obj: Union[datetime, str]) -> str:
    """Get time ago string in French"""
    return get_relative_time(datetime_obj)

def format_duration(seconds: int) -> str:
    """Format duration in seconds to human readable string"""
    if seconds < 60:
        return f"{seconds} seconde{'s' if seconds != 1 else ''}"
    
    minutes = seconds // 60
    if minutes < 60:
        return f"{minutes} minute{'s' if minutes != 1 else ''}"
    
    hours = minutes // 60
    remaining_minutes = minutes % 60
    
    if hours < 24:
        if remaining_minutes > 0:
            return f"{hours}h{remaining_minutes:02d}"
        return f"{hours} heure{'s' if hours != 1 else ''}"
    
    days = hours // 24
    remaining_hours = hours % 24
    
    if remaining_hours > 0:
        return f"{days} jour{'s' if days != 1 else ''} {remaining_hours}h"
    return f"{days} jour{'s' if days != 1 else ''}"

def get_current_fiscal_year() -> int:
    """Get current fiscal year (assuming fiscal year starts in January)"""
    return date.today().year

def is_weekend(check_date: date) -> bool:
    """Check if a date is weekend"""
    return check_date.weekday() >= 5

def get_age_in_days(from_date: date, to_date: Optional[date] = None) -> int:
    """Get age in days between two dates"""
    if to_date is None:
        to_date = date.today()
    
    return (to_date - from_date).days
