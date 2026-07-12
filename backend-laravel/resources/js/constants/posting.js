/**
 * Posting UI constants.
 */

export const POSTING_TEXT = {
    minLength: 50,
    maxLength: 20000,
};

/**
 * Human-readable labels + colors for the three parser strategies.
 * See ml-service/services/posting_parser.py — layered strategy.
 */
export const PARSE_STRATEGY_META = {
    sections: {
        label: 'Structured',
        description: 'Detected clear Required / Preferred / Responsibilities sections.',
        color: 'success',
        icon: 'mdi-check-decagram',
    },
    markers: {
        label: 'Inline signals',
        description: 'No section headers found; classified sentences by "must have" / "nice to have" language.',
        color: 'warning',
        icon: 'mdi-flag-variant-outline',
    },
    fallback: {
        label: 'Best effort',
        description: 'No clear structure detected; treated all sentences as requirements.',
        color: 'info',
        icon: 'mdi-information-outline',
    },
};
