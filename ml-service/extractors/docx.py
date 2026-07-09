"""DOCX text extraction using python-docx."""

import io
import docx


def extract_text(content: bytes) -> str:
    """Extract text from DOCX bytes."""
    doc = docx.Document(io.BytesIO(content))
    return "\n".join(p.text for p in doc.paragraphs)