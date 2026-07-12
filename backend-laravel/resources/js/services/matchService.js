import http from './http';

/**
 * Thin API wrappers for the /matches endpoints.
 */
export const matchService = {
    list(params = {}) {
        // Backend supports ?resume_id=X and ?posting_id=Y filters.
        return http.get('/matches', { params });
    },

    show(id) {
        return http.get(`/matches/${id}`);
    },

    compute(payload) {
        // payload: { resume_id, posting_id }
        return http.post('/matches', payload);
    },

    destroy(id) {
        return http.delete(`/matches/${id}`);
    },
};
