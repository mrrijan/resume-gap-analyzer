import http from './http';

/**
 * Thin API wrappers for the /resumes endpoints.
 * No state, no logic beyond the HTTP call.
 */
export const resumeService = {
    list() {
        return http.get('/resumes');
    },

    show(id) {
        return http.get(`/resumes/${id}`);
    },

    upload(file) {
        const formData = new FormData();
        formData.append('file', file);
        return http.post('/resumes', formData, {
            headers: { 'Content-Type': 'multipart/form-data' },
        });
    },

    destroy(id) {
        return http.delete(`/resumes/${id}`);
    },
};
