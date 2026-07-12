/**
 * Global axios instance for the Laravel API.
 *
 * All service files import this — never call axios directly elsewhere.
 * Two interceptors handle cross-cutting concerns:
 *   1. Request: attach the bearer token from the auth store
 *   2. Response: on 401, log the user out and redirect to /login
 *
 * We import stores inline (not at module top) to avoid a circular dependency —
 * the auth store also imports http.js indirectly through authService.
 */

import axios from 'axios';

const http = axios.create({
    baseURL: '/api',
    headers: {
        Accept: 'application/json',
        'Content-Type': 'application/json',
    },
});

// ---------- Request interceptor: attach auth token ----------
http.interceptors.request.use((config) => {
    // Lazy import to break circular dep with the auth store.
    const token = localStorage.getItem('auth_token');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

// ---------- Response interceptor: global error handling ----------
http.interceptors.response.use(
    (response) => response,
    async (error) => {
        // Any 401 anywhere in the app means "your session is dead."
        // Clear local auth state and bounce to /login.
        if (error.response?.status === 401) {
            localStorage.removeItem('auth_token');
            // Import lazily to avoid circular deps at module init time.
            const { useAuthStore } = await import('@/stores/auth');
            const { router } = await import('@/router');
            const authStore = useAuthStore();
            authStore.clearAuth();

            // Only redirect if we're not already on an auth page.
            const current = router.currentRoute.value;
            if (current.name !== 'login' && current.name !== 'register') {
                router.push({ name: 'login' });
            }
        }
        return Promise.reject(error);
    },
);

export default http;
