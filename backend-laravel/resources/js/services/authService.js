/**
 * Thin API wrappers for auth endpoints. No state, no logic beyond the HTTP call.
 * The auth store consumes these and manages state.
 */

import http from './http';

export const authService = {
    register(payload) {
        return http.post('/register', payload);
    },

    login(payload) {
        return http.post('/login', payload);
    },

    logout() {
        return http.post('/logout');
    },

    me() {
        return http.get('/me');
    },

    changePassword(payload) {
        return http.put('/change-password', payload);
    },
};
