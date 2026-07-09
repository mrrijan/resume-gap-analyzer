"""Pydantic schema for parsed resume output."""

from pydantic import BaseModel


class ParsedResume(BaseModel):
    skills: list[str]
    experience: list[str]
    education: list[str]
    certifications: list[str]
    raw_text: str