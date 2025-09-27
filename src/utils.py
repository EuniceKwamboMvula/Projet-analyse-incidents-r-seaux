from datetime import datetime

def parse_date(s: str):
    """
    Convertit une string en datetime.
    Supporte: YYYY-MM-DD ou YYYY-MM-DDTHH:MM:SS
    """
    if s is None:
        return None
    for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%S"):
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            continue
    raise ValueError(f"Format de date non supporté: {s}")

def safe_float(val, default=None):
    try:
        return float(val)
    except (ValueError, TypeError):
        return default
