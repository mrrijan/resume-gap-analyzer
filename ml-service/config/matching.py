"""Configuration for the matching engine — weighting formulas and thresholds."""

# Required requirements weight (relative to preferred).
# Preferred is fixed at 1. Ratio 2:1 means required matters twice as much.
# See Chapter 3 design section for rationale; alternative ratios (1:1, 3:1)
# are compared in Chapter 4 Result Analysis.
REQUIRED_WEIGHT: int = 2
PREFERRED_WEIGHT: int = 1

# Sentence-transformer model identifier.
# all-MiniLM-L6-v2: ~90MB, fast, general-purpose semantic similarity.
# Well-established baseline for sentence-embedding tasks.
EMBEDDING_MODEL_NAME: str = "sentence-transformers/all-MiniLM-L6-v2"