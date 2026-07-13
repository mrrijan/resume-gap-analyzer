/**
 * Auth store — the single source of truth for "who is logged in?"
 *
 * Holds: current user object + auth token.
 * Persists the token to localStorage; user is refetched from /me on app boot.
 * All auth-related actions (register, login, logout) live here.
 */

import { defineStore } from 'pinia';
import { computed, ref } from 'vue';
import { authService } from '@/services/authService';

export const useAuthStore = defineStore('auth', () => {
    // State
    const user  = ref(null);
    const token = ref(localStorage.getItem('auth_token'));

    // Getters
    const isAuthenticated = computed(() => Boolean(token.value));

    // Actions
    async function register(payload) {
        const { data } = await authService.register(payload);
        setAuth(data.user, data.token);
        return data;
    }

    async function login(payload) {
        const { data } = await authService.login(payload);
        setAuth(data.user, data.token);
        return data;
    }

    async function logout() {
        try {
            await authService.logout();
        } catch (e) {
            console.warn('Logout API call failed; clearing local state anyway.', e);
        }
        // Clear other stores so a new user doesn't see the previous one's data.
        const { useResumeStore } = await import('@/stores/resume');
        const { usePostingStore } = await import('@/stores/posting');
        const { useMatchStore } = await import('@/stores/match');
        const { useGapAnalysisStore } = await import('@/stores/gapAnalysis');

        useResumeStore().reset();
        usePostingStore().reset();
        useMatchStore().reset();
        useGapAnalysisStore().reset();

        clearAuth();
    }

    /**
     * Called on app boot to hydrate the user if we have a stored token.
     * Returns true if hydration succeeded, false if the token was invalid.
     */
    async function fetchCurrentUser() {
        if (!token.value) return false;
        try {
            const { data } = await authService.me();
            user.value = data.user;
            return true;
        } catch (e) {
            // Token was rejected — clear it.
            clearAuth();
            return false;
        }
    }

    function setAuth(userObj, tokenStr) {
        user.value  = userObj;
        token.value = tokenStr;
        localStorage.setItem('auth_token', tokenStr);
    }

    function clearAuth() {
        user.value  = null;
        token.value = null;
        localStorage.removeItem('auth_token');
    }

    return {
        // state
        user, token,
        // getters
        isAuthenticated,
        // actions
        register, login, logout, fetchCurrentUser, clearAuth,
    };
});
