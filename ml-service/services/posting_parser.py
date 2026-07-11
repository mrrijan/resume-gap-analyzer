"""
Job posting parsing service.

Layered strategy:
    Layer 1: Extract by section headers (Required Qualifications, etc.)
    Layer 2: Extract by inline signal phrases (must have, nice to have, etc.)
    Layer 3: Fallback — treat all sentences as required requirements.

Reports which layer succeeded via ParsedPosting.parse_strategy.
"""

import re

from config.posting_markers import (
    REQUIRED_HEADERS,
    PREFERRED_HEADERS,
    RESPONSIBILITIES_HEADERS,
    BOUNDARY_HEADERS,
    REQUIRED_SIGNALS,
    PREFERRED_SIGNALS,
)
from extractors.text_cleanup import strip_control_chars
from schemas.posting import ParsedPosting


def parse(text: str) -> ParsedPosting:
    """Main entrypoint: raw posting text -> ParsedPosting."""
    text = strip_control_chars(text).strip()

    # Layer 1
    layer1 = _extract_by_sections(text)
    if _has_content(layer1):
        return ParsedPosting(
            required=layer1["required"],
            preferred=layer1["preferred"],
            responsibilities=layer1["responsibilities"],
            raw_text=text,
            parse_strategy="sections",
        )

    # Layer 2
    layer2 = _extract_by_markers(text)
    if _has_content(layer2):
        return ParsedPosting(
            required=layer2["required"],
            preferred=layer2["preferred"],
            responsibilities=[],
            raw_text=text,
            parse_strategy="markers",
        )

    # Layer 3 fallback
    return ParsedPosting(
        required=_split_sentences(text),
        preferred=[],
        responsibilities=[],
        raw_text=text,
        parse_strategy="fallback",
    )


def _has_content(sections: dict[str, list[str]]) -> bool:
    """True if any bucket has at least one entry."""
    return any(len(v) > 0 for v in sections.values())


# ---------- Layer 1: section header extraction ----------
def _extract_by_sections(text: str) -> dict[str, list[str]]:
    """
    Walks lines. When a known header is found, subsequent lines are captured
    under that bucket until another header (or boundary) appears.
    """
    buckets: dict[str, list[str]] = {
        "required": [],
        "preferred": [],
        "responsibilities": [],
    }
    current: str | None = None

    for raw_line in text.split("\n"):
        line = raw_line.strip()
        if not line:
            continue

        header_type = _classify_header(line)

        if header_type in ("required", "preferred", "responsibilities"):
            current = header_type
            continue

        if header_type == "boundary":
            current = None
            continue

        if current:
            cleaned = _clean_bullet(line)
            if cleaned:
                buckets[current].append(cleaned)

    return buckets


def _classify_header(line: str) -> str | None:
    """
    Return 'required', 'preferred', 'responsibilities', 'boundary', or None.
    """
    normalized = line.lower().strip(":").strip("*").strip("#").strip()
    if len(normalized) > 45:
        return None
    if normalized in REQUIRED_HEADERS:
        return "required"
    if normalized in PREFERRED_HEADERS:
        return "preferred"
    if normalized in RESPONSIBILITIES_HEADERS:
        return "responsibilities"
    if normalized in BOUNDARY_HEADERS:
        return "boundary"
    return None


def _clean_bullet(line: str) -> str:
    """Strip leading bullet markers, asterisks, hyphens, numbering."""
    return re.sub(r'^[\s\-\*•●·◦▪►]*(?:\d+[\.\)])?\s*', '', line).strip()


# ---------- Layer 2: inline signal extraction ----------
def _extract_by_markers(text: str) -> dict[str, list[str]]:
    """
    Split into sentences and classify each by presence of REQUIRED_SIGNALS or
    PREFERRED_SIGNALS. Uncategorized sentences are dropped.
    """
    sentences = _split_sentences(text)
    buckets: dict[str, list[str]] = {"required": [], "preferred": []}

    for sentence in sentences:
        lower = sentence.lower()
        # Check preferred FIRST — many preferred signals contain "have" which
        # would incorrectly match required signals like "you have".
        if any(sig in lower for sig in PREFERRED_SIGNALS):
            buckets["preferred"].append(sentence)
        elif any(sig in lower for sig in REQUIRED_SIGNALS):
            buckets["required"].append(sentence)

    return buckets


# ---------- Utility: sentence splitter ----------
def _split_sentences(text: str) -> list[str]:
    """
    Split text into sentences. Naive but adequate for job postings.
    Splits on '.', '!', '?', or newlines followed by capital letters.
    """
    # First normalize line breaks so bullet lists are also treated as sentence boundaries.
    normalized = re.sub(r'\n+', '. ', text)
    # Split on sentence-ending punctuation.
    parts = re.split(r'(?<=[.!?])\s+', normalized)
    return [p.strip().rstrip('.').strip() for p in parts if p.strip() and len(p.strip()) > 5]