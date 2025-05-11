import re

def normalize_title(title: str) -> str:
    """Normalize title for consistent matching and grouping."""
    return re.sub(r"[^a-z0-9]", "", title.lower())
