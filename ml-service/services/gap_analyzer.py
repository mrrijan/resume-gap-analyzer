"""
Gap analysis service — the algorithmic centerpiece of the project.

Two sub-algorithms:

    1. Per-posting classification (M4a)
       Each requirement from M3 is labeled Strong/Partial/Missing based on
       similarity thresholds.

    2. Cross-posting gap ranking (M4b) — original contribution
       Gaps (Missing + Partial items) from ALL postings are:
           a) Embedded and clustered — semantically similar gaps from
              different postings are merged (e.g. "Git" ≈ "version control").
           b) Scored by (frequency across postings) × (1 - avg_similarity).
           c) Sorted descending — highest score = biggest opportunity.

    The frequency-weighted ranking is the project's original algorithmic
    contribution: instead of showing users every missing skill equally, it
    surfaces skills that would unlock the most postings if addressed.
"""

from functools import lru_cache

import numpy as np
from sentence_transformers import SentenceTransformer

from config.matching import EMBEDDING_MODEL_NAME
from config.gap_analysis import (
    STRONG_MATCH_THRESHOLD,
    PARTIAL_MATCH_THRESHOLD,
    GAP_CLUSTER_THRESHOLD,
    FREQUENCY_EXPONENT,
    DEFICIENCY_EXPONENT,
    GAP_CLASSIFICATIONS,
)
from schemas.match import RequirementMatch
from schemas.gap import (
    GapAnalysisInput,
    GapAnalysisResult,
    ClassifiedRequirement,
    PostingClassification,
    RankedGap,
)


# ---------- Model reuse ----------
# Same model as M3. lru_cache means we share the loaded instance.
@lru_cache(maxsize=1)
def _get_model() -> SentenceTransformer:
    return SentenceTransformer(EMBEDDING_MODEL_NAME)


# ---------- Entry point ----------
def analyze(payload: GapAnalysisInput) -> GapAnalysisResult:
    """Run gap analysis over a set of resume-vs-posting match results."""
    if not payload.posting_matches:
        raise ValueError("At least one posting match is required")

    # Step 1 (M4a): Classify every requirement in every posting.
    per_posting = [
        _classify_posting(pm.posting_id, pm.match_result.per_requirement,
                          pm.match_result.overall_fit)
        for pm in payload.posting_matches
    ]

    # Step 2 (M4b): Collect gaps (missing + partial) across all postings,
    # cluster semantically similar ones, and rank.
    ranked = _rank_gaps_across_postings(per_posting)

    return GapAnalysisResult(
        per_posting_classifications=per_posting,
        ranked_gaps=ranked,
        total_postings=len(payload.posting_matches),
    )


# ---------- M4a: per-posting classification ----------
def _classify_posting(
    posting_id: str,
    requirements: list[RequirementMatch],
    overall_fit: float,
) -> PostingClassification:
    """Classify each requirement in one posting as strong/partial/missing."""
    strong: list[ClassifiedRequirement] = []
    partial: list[ClassifiedRequirement] = []
    missing: list[ClassifiedRequirement] = []

    for req in requirements:
        strength = _classify_strength(req.similarity)
        classified = ClassifiedRequirement(
            text=req.text,
            bucket=req.bucket,
            similarity=req.similarity,
            best_matched_section=req.best_matched_section,
            strength=strength,
        )
        if strength == "strong":
            strong.append(classified)
        elif strength == "partial":
            partial.append(classified)
        else:
            missing.append(classified)

    return PostingClassification(
        posting_id=posting_id,
        overall_fit=overall_fit,
        strong=strong,
        partial=partial,
        missing=missing,
    )


def _classify_strength(similarity: float) -> str:
    """Map raw similarity to strong/partial/missing."""
    if similarity >= STRONG_MATCH_THRESHOLD:
        return "strong"
    if similarity >= PARTIAL_MATCH_THRESHOLD:
        return "partial"
    return "missing"


# ---------- M4b: cross-posting gap ranking (the original contribution) ----------
def _rank_gaps_across_postings(
    per_posting: list[PostingClassification],
) -> list[RankedGap]:
    """
    Collect all gap requirements across postings, cluster semantically similar
    ones, then rank by (frequency across postings) × (match deficiency).
    """
    total_postings = len(per_posting)

    # Flatten gaps from all postings, remembering source posting for each.
    gap_records: list[dict] = []
    for pc in per_posting:
        for req in pc.strong + pc.partial + pc.missing:
            if req.strength in GAP_CLASSIFICATIONS:
                gap_records.append({
                    "text": req.text,
                    "similarity": req.similarity,
                    "posting_id": pc.posting_id,
                })

    if not gap_records:
        return []

    # Cluster semantically similar gaps using embedding similarity.
    clusters = _cluster_gaps(gap_records)

    # Score each cluster and build result objects.
    ranked: list[RankedGap] = []
    for cluster in clusters:
        # Deduplicate posting IDs — one posting shouldn't count twice even if it
        # had two similar requirements clustered together.
        affected = list({r["posting_id"] for r in cluster})
        frequency = len(affected) / total_postings
        avg_similarity = float(np.mean([r["similarity"] for r in cluster]))
        deficiency = 1.0 - avg_similarity

        gap_score = (frequency ** FREQUENCY_EXPONENT) * (deficiency ** DEFICIENCY_EXPONENT)

        # Pick a canonical text — the requirement in the cluster whose similarity
        # is closest to the cluster's median (representative, not extreme).
        sorted_by_sim = sorted(cluster, key=lambda r: r["similarity"])
        canonical = sorted_by_sim[len(sorted_by_sim) // 2]["text"]

        ranked.append(RankedGap(
            canonical_text=canonical,
            example_requirements=list({r["text"] for r in cluster}),
            avg_similarity=avg_similarity,
            affected_posting_ids=affected,
            frequency=frequency,
            gap_score=gap_score,
        ))

    # Sort by score descending — highest score = most impactful gap.
    ranked.sort(key=lambda g: g.gap_score, reverse=True)
    return ranked


def _cluster_gaps(gap_records: list[dict]) -> list[list[dict]]:
    """
    Greedy clustering: for each gap, either merge it into an existing cluster
    (if its embedding is close enough to the cluster's centroid) or start a
    new one.

    Simple and deterministic. Not optimal in the "provably best clustering"
    sense, but works well for O(n) gaps where n is small (a user has, say,
    30-70 gap requirements at most across their target postings).
    """
    model = _get_model()
    texts = [r["text"] for r in gap_records]
    embeddings = model.encode(texts, normalize_embeddings=True)

    clusters: list[dict] = []
    # Each cluster tracks: members list, running centroid embedding.
    for i, record in enumerate(gap_records):
        emb = embeddings[i]

        best_cluster_idx = -1
        best_similarity = -1.0
        for c_idx, cluster in enumerate(clusters):
            sim = float(np.dot(cluster["centroid"], emb))
            if sim > best_similarity:
                best_similarity = sim
                best_cluster_idx = c_idx

        if best_cluster_idx >= 0 and best_similarity >= GAP_CLUSTER_THRESHOLD:
            # Merge into existing cluster; update centroid as running mean.
            cluster = clusters[best_cluster_idx]
            cluster["members"].append(record)
            n = len(cluster["members"])
            cluster["centroid"] = (cluster["centroid"] * (n - 1) + emb) / n
            # Renormalize centroid so future dot products remain valid cosine.
            cluster["centroid"] = cluster["centroid"] / np.linalg.norm(cluster["centroid"])
        else:
            clusters.append({"members": [record], "centroid": emb.copy()})

    return [c["members"] for c in clusters]