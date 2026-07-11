"""
Configuration for the gap analysis engine.

Thresholds and parameters can be tuned via Chapter 4 experiments.
"""

# ---------- Classification thresholds ----------
# Applied to raw cosine similarity scores from M3.
STRONG_MATCH_THRESHOLD: float = 0.60
PARTIAL_MATCH_THRESHOLD: float = 0.35
# similarity >= STRONG_MATCH_THRESHOLD             -> "strong"
# PARTIAL_MATCH_THRESHOLD <= similarity < STRONG   -> "partial"
# similarity < PARTIAL_MATCH_THRESHOLD             -> "missing"


# ---------- Cross-posting clustering ----------
# Two requirements from different postings are treated as the SAME gap if
# their embeddings' cosine similarity exceeds this threshold.
# Higher = stricter clustering (fewer merges, more distinct gaps).
# Lower = looser clustering (more merges, may conflate different skills).
GAP_CLUSTER_THRESHOLD: float = 0.65


# ---------- Ranking ----------
# gap_score = (missing_count / total_postings) ** FREQUENCY_EXPONENT
#             × (1 - avg_similarity) ** DEFICIENCY_EXPONENT
# Both exponents = 1.0 gives simple frequency × deficiency (per spec).
# Tweaking these lets Chapter 4 experiments explore ranking sensitivity.
FREQUENCY_EXPONENT: float = 1.0
DEFICIENCY_EXPONENT: float = 1.0


# ---------- Which classifications count as gaps? ----------
# Only "missing" and "partial" requirements are considered gaps to rank.
# "strong" matches are ignored (they're not gaps).
GAP_CLASSIFICATIONS: set[str] = {"missing", "partial"}