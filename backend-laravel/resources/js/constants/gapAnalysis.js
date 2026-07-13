/**
 * Gap Analysis display constants.
 */

/**
 * Recommended minimum postings for meaningful frequency-weighted ranking.
 * Per the M4 acceptance criteria — below this, ranking mostly reflects
 * individual similarity, not the frequency-weighted contribution.
 */
export const RECOMMENDED_MIN_POSTINGS = 5;

/**
 * Format a frequency (0.0 - 1.0) as a "X of Y postings" string.
 */
export function formatFrequency(freq, total) {
    const count = Math.round(freq * total);
    return `${count} of ${total} postings`;
}
