"""Pydantic schemas for the matching engine."""

from typing import Literal
from pydantic import BaseModel


RequirementBucket = Literal["required", "preferred"]


class RequirementMatch(BaseModel):
    """Similarity result for a single posting requirement."""
    text: str
    bucket: RequirementBucket
    similarity: float  # 0.0 to 1.0
    best_matched_section: str  # which resume section produced the max score


class MatchResult(BaseModel):
    """Overall match result: resume vs. one posting."""
    overall_fit: float  # 0.0 to 100.0 (percentage)
    avg_required: float  # 0.0 to 1.0
    avg_preferred: float  # 0.0 to 1.0
    required_weight: int
    preferred_weight: int
    per_requirement: list[RequirementMatch]


class MatchInput(BaseModel):
    """Request DTO: caller sends already-parsed resume + parsed posting."""
    resume_skills: list[str]
    resume_experience: list[str]
    resume_education: list[str]
    resume_certifications: list[str]
    posting_required: list[str]
    posting_preferred: list[str]