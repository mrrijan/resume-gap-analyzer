"""Pydantic schemas for gap analysis."""

from typing import Literal
from pydantic import BaseModel

from schemas.match import MatchResult


MatchStrength = Literal["strong", "partial", "missing"]


class ClassifiedRequirement(BaseModel):
    """A single requirement with its classification added."""
    text: str
    bucket: str  # "required" or "preferred" — from M3
    similarity: float
    best_matched_section: str
    strength: MatchStrength  # NEW — classification derived from similarity


class PostingClassification(BaseModel):
    """Per-posting Strong/Partial/Missing breakdown."""
    posting_id: str
    overall_fit: float
    strong: list[ClassifiedRequirement]
    partial: list[ClassifiedRequirement]
    missing: list[ClassifiedRequirement]


class RankedGap(BaseModel):
    """A gap identified across multiple postings, ranked by importance."""
    canonical_text: str  # representative requirement text for this gap
    example_requirements: list[str]  # raw texts from each posting that clustered into this gap
    avg_similarity: float  # mean similarity across all instances
    affected_posting_ids: list[str]
    frequency: float  # proportion of postings that have this gap (0.0 to 1.0)
    gap_score: float  # ranking metric — higher = more important gap


class PostingMatchInput(BaseModel):
    """A single posting's M3 result, as input to gap analysis."""
    posting_id: str  # caller-supplied identifier
    match_result: MatchResult


class GapAnalysisInput(BaseModel):
    """Request DTO: all M3 results for one user's target postings."""
    posting_matches: list[PostingMatchInput]


class GapAnalysisResult(BaseModel):
    """Response DTO."""
    per_posting_classifications: list[PostingClassification]
    ranked_gaps: list[RankedGap]
    total_postings: int