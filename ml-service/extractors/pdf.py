"""PDF text extraction using PyMuPDF."""

import fitz


def extract_text(content: bytes) -> str:
    """Extract text from PDF bytes. Decomposes ligatures to plain characters."""
    doc = fitz.open(stream=content, filetype="pdf")
    flags = fitz.TEXTFLAGS_TEXT & ~fitz.TEXT_PRESERVE_LIGATURES
    return "\n".join(page.get_text("text", flags=flags) for page in doc)