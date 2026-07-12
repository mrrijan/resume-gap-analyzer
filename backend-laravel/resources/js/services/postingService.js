import http from './http';

/**
 * Thin API wrappers for the /postings endpoints.
 */
export const postingService = {
    list() {
        return http.get('/postings');
    },

    show(id) {
        return http.get(`/postings/${id}`);
    },

    create(payload) {
        // payload: { title?, text, source_url? }
        return http.post('/postings', payload);
    },

    update(id, payload) {
        return http.put(`/postings/${id}`, payload);
    },

    destroy(id) {
        return http.delete(`/postings/${id}`);
    },
};
