"""Snippet generation for Alfred."""


def generate_uid(keyword: str, emoji: str) -> str:
    """Generate stable UID from keyword and emoji hex codes."""
    hex_codes = "-".join(f"{ord(c):X}" for c in emoji)
    return f"{keyword}-{hex_codes}"
