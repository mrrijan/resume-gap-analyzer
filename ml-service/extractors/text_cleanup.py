"""
Text cleanup utilities for post-processing raw extracted text.
"""

import re


def strip_control_chars(text: str) -> str:
    """Drop non-printable icon-font chars (keeps \\n and \\t)."""
    return re.sub(r'[\x00-\x09\x0B-\x1F\x7F]', '', text)


def fix_letter_spacing(text: str) -> str:
    """Collapse 'R i j a n' -> 'Rijan' (3+ single letters separated by spaces)."""
    return re.sub(
        r'\b(?:[A-Za-z] ){2,}[A-Za-z]\b',
        lambda m: m.group().replace(' ', ''),
        text,
    )