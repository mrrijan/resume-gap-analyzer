"""
Vocabulary for job posting parsing.

REQUIRED_HEADERS / PREFERRED_HEADERS / RESPONSIBILITIES_HEADERS:
    Recognized section headers we capture content under.

BOUNDARY_HEADERS:
    Headers we recognize (so they stop content flow) but don't capture.

REQUIRED_SIGNALS / PREFERRED_SIGNALS:
    Inline phrases used to classify individual sentences when section headers
    aren't present (Layer 2 fallback).
"""

# ---------- Layer 1: section headers ----------
REQUIRED_HEADERS: set[str] = {
    "required qualifications",
    "requirements",
    "required skills",
    "required experience",
    "must haves",
    "must have",
    "essential qualifications",
    "essential skills",
    "what you'll need",
    "what you need",
    "qualifications",
    "who you are",
    "what we're looking for",
    "what we are looking for",
    "minimum qualifications",
    "basic qualifications",
    "eligibility",
    "eligibility criteria",
    "who should apply",
    "candidate profile",
    "required profile",
    "skills required",
    "skills and qualifications",
}

PREFERRED_HEADERS: set[str] = {
    "preferred qualifications",
    "preferred skills",
    "preferred experience",
    "preferred",
    "nice to have",
    "nice to haves",
    "bonus",
    "bonus points",
    "pluses",
    "desired qualifications",
    "desired skills",
    "would be great",
    "we'd love",
    "we'd also love",
    "additional qualifications",
}

RESPONSIBILITIES_HEADERS: set[str] = {
    "responsibilities",
    "key responsibilities",
    "duties",
    "what you'll do",
    "what you will do",
    "role",
    "your role",
    "in this role",
    "the role",
    "day to day",
    "day-to-day",
    "what you'll be doing",
    "job responsibilities",
    "job duties",
    "what you'll learn",
    "what you will learn",
    "what to expect",
    "learning outcomes",
    "you will",
    "you'll",
}

BOUNDARY_HEADERS: set[str] = {
    "about the company",
    "about us",
    "about",
    "company overview",
    "our mission",
    "our team",
    "benefits",
    "perks",
    "compensation",
    "salary",
    "salary range",
    "location",
    "working schedule",
    "work schedule",
    "job summary",
    "summary",
    "overview",
    "position",
    "how to apply",
    "application process",
    "equal opportunity",
    "eeo statement",
    "diversity",
    "why join us",
    "why work here",
    "contact",
    "company description",
    "role description",
    "about the job",
    "about the role",
    "fellowship details",
    "internship details",
    "position details",
    "important information",
    "additional information",
    "notes",
    "note",
    "duration",
    "mode",
    "working hours",
    "working days",
    "duration",
}


# ---------- Layer 2: inline signal phrases ----------
# All matched case-insensitively as substrings.
REQUIRED_SIGNALS: list[str] = [
    "must have",
    "must be",
    "required",
    "you must",
    "you have",
    "you should have",
    "requires",
    "essential",
    "mandatory",
    "need to have",
]

PREFERRED_SIGNALS: list[str] = [
    "nice to have",
    "preferred",
    "bonus",
    "we'd love",
    "we would love",
    "ideally",
    "would be a plus",
    "is a plus",
    "helpful",
    "not required but",
]