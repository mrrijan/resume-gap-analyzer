"""
Vocabulary of resume section headers.

SECTION_HEADERS: headers we capture content under.
BOUNDARY_HEADERS: headers we recognize as boundaries but don't collect content from.
"""

SECTION_HEADERS: dict[str, str] = {
    "skills": "skills",
    "technical skills": "skills",
    "core skills": "skills",
    "core competencies": "skills",
    "technologies": "skills",

    "experience": "experience",
    "work experience": "experience",
    "professional experience": "experience",
    "employment": "experience",
    "employment history": "experience",

    "education": "education",
    "academic background": "education",

    "certifications": "certifications",
    "certificates": "certifications",
    "licenses": "certifications",
    "licenses & certifications": "certifications",
}

BOUNDARY_HEADERS: set[str] = {
    "summary", "objective", "profile", "about", "about me",
    "projects", "personal projects", "notable projects",
    "achievements", "accomplishments",
    "awards", "honors", "awards and honors",
    "languages", "language",
    "references", "reference",
    "publications", "presentations",
    "activities", "hobbies", "interests",
    "other activities and projects", "extracurricular", "extracurriculars",
    "volunteer", "volunteering", "volunteer experience",
    "contact", "personal details",
}