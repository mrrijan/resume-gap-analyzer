"""
Matching service: computes semantic similarity between a parsed resume and
a parsed job posting, and produces an overall fit score.

Approach:
    1. Embed each individual resume line as its own vector. Preserving line
       granularity avoids semantic dilution — a "Git" skill in a 21-item skills
       list would otherwise get averaged into meaninglessness. We track which
       resume section each line came from so we can still report the
       best-matched section per requirement.
    2. For each posting requirement, embed it and compute cosine similarity
       against every resume line embedding. The MAX similarity wins — that
       requirement is best-matched by whichever specific resume line it's
       most semantically close to.
    3. Average requirement scores within their bucket (required / preferred).
    4. Combine buckets using configurable weights to yield an overall fit
       percentage.

The pretrained model is the "unavoidable circumstance" dependency (training an
embedding model from scratch is out of scope for a BCA capstone). Everything
downstream of embedding — comparison strategy, aggregation formula, weighting —
is our own algorithm.
"""

from functools import lru_cache

import numpy as np
from sentence_transformers import SentenceTransformer

from config.matching import (
    REQUIRED_WEIGHT,
    PREFERRED_WEIGHT,
    EMBEDDING_MODEL_NAME,
)
from schemas.match import MatchInput, MatchResult, RequirementMatch


# ---------- Model loading (cached) ----------
@lru_cache(maxsize=1)
def _get_model() -> SentenceTransformer:
    """Load the embedding model once and cache it in memory."""
    return SentenceTransformer(EMBEDDING_MODEL_NAME)


# ---------- Entry point ----------
def match(payload: MatchInput) -> MatchResult:
    """Match a parsed resume against a parsed posting."""
    model = _get_model()

    # Flatten all resume lines into a single list, remembering the section
    # each line originated from. This is the "no more blobs" refactor:
    # we compare requirements against individual lines, not concatenated soups.
    resume_lines, line_sections = _flatten_resume(payload)

    if not resume_lines:
        raise ValueError("Resume has no content to match against")

    # Embed all resume lines in one batch (much faster than one-by-one).
    resume_embeddings = model.encode(resume_lines, normalize_embeddings=True)

    # Score requirements from both buckets against the same resume line pool.
    per_requirement: list[RequirementMatch] = []
    per_requirement.extend(
        _score_bucket(
            requirements=payload.posting_required,
            bucket="required",
            model=model,
            resume_lines=resume_lines,
            line_sections=line_sections,
            resume_embeddings=resume_embeddings,
        )
    )
    per_requirement.extend(
        _score_bucket(
            requirements=payload.posting_preferred,
            bucket="preferred",
            model=model,
            resume_lines=resume_lines,
            line_sections=line_sections,
            resume_embeddings=resume_embeddings,
        )
    )

    # Aggregate per bucket.
    required_scores = [m.similarity for m in per_requirement if m.bucket == "required"]
    preferred_scores = [m.similarity for m in per_requirement if m.bucket == "preferred"]

    avg_required = float(np.mean(required_scores)) if required_scores else 0.0
    avg_preferred = float(np.mean(preferred_scores)) if preferred_scores else 0.0

    overall_fit = _compute_overall_fit(
        avg_required=avg_required,
        avg_preferred=avg_preferred,
        has_required=bool(required_scores),
        has_preferred=bool(preferred_scores),
    )

    return MatchResult(
        overall_fit=overall_fit,
        avg_required=avg_required,
        avg_preferred=avg_preferred,
        required_weight=REQUIRED_WEIGHT,
        preferred_weight=PREFERRED_WEIGHT,
        per_requirement=per_requirement,
    )


# ---------- Resume flattening ----------
def _flatten_resume(payload: MatchInput) -> tuple[list[str], list[str]]:
    """
    Flatten all resume sections into two parallel lists:
        resume_lines[i] = the i-th resume item (a skill, a bullet, a cert, etc.)
        line_sections[i] = the section it came from ("skills", "experience", ...)
    Empty lines are dropped.
    """
    resume_lines: list[str] = []
    line_sections: list[str] = []

    section_map = {
        "skills": payload.resume_skills,
        "experience": payload.resume_experience,
        "education": payload.resume_education,
        "certifications": payload.resume_certifications,
    }

    for section_name, lines in section_map.items():
        for line in lines:
            stripped = line.strip()
            if stripped:
                resume_lines.append(stripped)
                line_sections.append(section_name)

    return resume_lines, line_sections


# ---------- Bucket scoring ----------
def _score_bucket(
    requirements: list[str],
    bucket: str,
    model: SentenceTransformer,
    resume_lines: list[str],
    line_sections: list[str],
    resume_embeddings: np.ndarray,
) -> list[RequirementMatch]:
    """Score every requirement in a bucket against all resume lines."""
    if not requirements:
        return []

    requirement_embeddings = model.encode(requirements, normalize_embeddings=True)

    matches: list[RequirementMatch] = []
    for req_text, req_emb in zip(requirements, requirement_embeddings):
        # Cosine similarity vs. each resume line (embeddings are pre-normalized,
        # so dot product == cosine similarity).
        similarities = resume_embeddings @ req_emb
        best_idx = int(np.argmax(similarities))
        matches.append(
            RequirementMatch(
                text=req_text,
                bucket=bucket,
                similarity=float(similarities[best_idx]),
                best_matched_section=line_sections[best_idx],
            )
        )
    return matches


# ---------- Overall fit aggregation ----------
def _compute_overall_fit(
    avg_required: float,
    avg_preferred: float,
    has_required: bool,
    has_preferred: bool,
) -> float:
    """
    Weighted average of the two bucket scores, expressed as 0-100 percentage.

    If a bucket is empty (posting had no required-only or no preferred-only items),
    it's excluded from the average so it doesn't drag the score toward zero.
    """
    numerator = 0.0
    denominator = 0

    if has_required:
        numerator += REQUIRED_WEIGHT * avg_required
        denominator += REQUIRED_WEIGHT

    if has_preferred:
        numerator += PREFERRED_WEIGHT * avg_preferred
        denominator += PREFERRED_WEIGHT

    if denominator == 0:
        return 0.0

    return round((numerator / denominator) * 100, 2)