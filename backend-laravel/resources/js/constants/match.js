/**
 * Match display constants — mirrors backend classification thresholds.
 * See:
 *   backend-laravel/app/Http/Controllers/MatchController.php (STRONG_THRESHOLD, PARTIAL_THRESHOLD)
 *   ml-service/config/gap_analysis.py                       (source of truth)
 * If thresholds change, update all three.
 */

export const STRENGTH_META = {
    strong: {
        label: 'Strong matches',
        shortLabel: 'Strong',
        color: 'success',
        icon: 'mdi-check-circle',
        description: 'Requirements your resume clearly addresses.',
    },
    partial: {
        label: 'Partial matches',
        shortLabel: 'Partial',
        color: 'warning',
        icon: 'mdi-progress-check',
        description: 'Requirements your resume touches on but could strengthen.',
    },
    missing: {
        label: 'Missing',
        shortLabel: 'Missing',
        color: 'error',
        icon: 'mdi-alert-circle-outline',
        description: 'Requirements not detectably present in your resume.',
    },
};

/**
 * Fit score → tier band for display purposes.
 * Empirical bands based on typical sentence-transformer similarity ranges.
 */
export function fitTier(percent) {
    if (percent >= 55) return { label: 'Strong candidate', color: 'success' };
    if (percent >= 40) return { label: 'Reasonable fit',   color: 'warning' };
    return { label: 'Notable gaps', color: 'error' };
}
