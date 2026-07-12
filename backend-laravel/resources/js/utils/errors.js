/**
 * Best-effort extraction of a user-facing error message from an axios error.
 * Prioritizes: field validation errors > backend message > fallback.
 */
export function extractApiError(err, fallback = 'Something went wrong.') {
    if (err?.response?.status === 422) {
        const errors = err.response.data.errors || {};
        const firstField = Object.keys(errors)[0];
        if (firstField) return errors[firstField][0];
    }
    return err?.response?.data?.message || fallback;
}
