"""Pydantic schemas for job posting parsing."""

from typing import Literal
from pydantic import BaseModel


ParseStrategy = Literal["sections", "markers", "fallback"]


class PostingInput(BaseModel):
    """Request DTO for POST /parse-posting."""
    text: str


class ParsedPosting(BaseModel):
    """Response DTO for POST /parse-posting."""
    required: list[str]
    preferred: list[str]
    responsibilities: list[str]
    raw_text: str
    parse_strategy: ParseStrategy