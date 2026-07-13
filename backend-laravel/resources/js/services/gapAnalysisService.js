import http from './http';

/**
 * Thin API wrappers for the /gap-analyses endpoints.
 */
export const gapAnalysisService = {
    list() {
        return http.get('/gap-analyses');
    },

    show(id) {
        return http.get(`/gap-analyses/${id}`);
    },

    create(payload) {
        // payload: { resume_id, posting_ids: [] }
        return http.post('/gap-analyses', payload);
    },

    destroy(id) {
        return http.delete(`/gap-analyses/${id}`);
    },
};
