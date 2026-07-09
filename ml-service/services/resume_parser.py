"""
Resume parsing service.

Orchestrates: file bytes -> raw text -> cleaned text -> structured sections.
"""

import re

from config.resume_headers import SECTION_HEADERS, BOUNDARY_HEADERS
from extractors import pdf, docx
from extractors.text_cleanup import strip_control_chars, fix_letter_spacing
from schemas.resume import ParsedResume


def parse(content: bytes, filename: str) -> ParsedResume:
    """Main entrypoint: file bytes + filename -> ParsedResume."""
    filename_lower = filename.lower()

    if filename_lower.endswith(".pdf"):
        text = pdf.extract_text(content)
    elif filename_lower.endswith(".docx"):
        text = docx.extract_text(content)
    else:
        raise ValueError("Only PDF and DOCX are supported")

    text = strip_control_chars(text)
    text = fix_letter_spacing(text)

    sections = _split_into_sections(text)

    return ParsedResume(
        skills=_extract_skills(sections.get("skills", [])),
        experience=_extract_entries(sections.get("experience", [])),
        education=_extract_entries(sections.get("education", [])),
        certifications=_extract_entries(sections.get("certifications", [])),
        raw_text=text,
    )


# ---------- Section splitting ----------
def _split_into_sections(text: str) -> dict[str, list[str]]:
    """Walk lines. Open a section on SECTION header, close on any header."""
    sections: dict[str, list[str]] = {}
    current_section: str | None = None

    for raw_line in text.split("\n"):
        line = raw_line.strip()
        if not line:
            continue

        header_type, canonical = _classify_header(line)

        if header_type == "section":
            current_section = canonical
            sections.setdefault(current_section, [])
            continue

        if header_type == "boundary":
            current_section = None
            continue

        if current_section:
            sections[current_section].append(line)

    return sections


def _classify_header(line: str) -> tuple[str | None, str | None]:
    """Return (type, canonical_name). Type is 'section', 'boundary', or None."""
    normalized = line.lower().strip(":").strip()
    if len(normalized) > 40:
        return (None, None)
    if normalized in SECTION_HEADERS:
        return ("section", SECTION_HEADERS[normalized])
    if normalized in BOUNDARY_HEADERS:
        return ("boundary", None)
    return (None, None)


# ---------- Section-specific extractors ----------
def _extract_skills(lines: list[str]) -> list[str]:
    """Flatten skills lines into a deduplicated list of individual skills."""
    skills: list[str] = []
    for line in lines:
        if ":" in line:
            line = line.split(":", 1)[1]

        parts = re.split(r'[,/|•·]', line)
        for part in parts:
            skill = part.strip()
            if skill and len(skill) < 60:
                skills.append(skill)

    seen: set[str] = set()
    unique: list[str] = []
    for s in skills:
        key = s.lower()
        if key not in seen:
            seen.add(key)
            unique.append(s)
    return unique


def _extract_entries(lines: list[str]) -> list[str]:
    """For non-skills sections, return each line as-is."""
    return lines