/**
 * Vue Router setup with authentication guards.
 *
 * Route meta:
 *   requiresAuth: true  → must be logged in
 *   requiresGuest: true → must NOT be logged in (e.g. login page redirects
 *                         to dashboard if already authenticated)
 */

import { createRouter, createWebHistory } from 'vue-router';
import { useAuthStore } from '@/stores/auth';

const routes = [
    // ---------- Auth ----------
    {
        path: '/login',
        name: 'login',
        component: () => import('@/views/auth/LoginView.vue'),
        meta: { requiresGuest: true, layout: 'auth' },
    },
    {
        path: '/register',
        name: 'register',
        component: () => import('@/views/auth/RegisterView.vue'),
        meta: { requiresGuest: true, layout: 'auth' },
    },

    // ---------- App ----------
    {
        path: '/',
        name: 'dashboard',
        component: () => import('@/views/DashboardView.vue'),
        meta: { requiresAuth: true, layout: 'app' },
    },
    {
        path: '/resumes',
        name: 'resumes',
        component: () => import('@/views/ResumeView.vue'),
        meta: { requiresAuth: true, layout: 'app' },
    },
    // ---------- Fallback ----------
    {
        path: '/:pathMatch(.*)*',
        redirect: { name: 'dashboard' },
    },
];

export const router = createRouter({
    history: createWebHistory(),
    routes,
});

// Global guard — enforces requiresAuth / requiresGuest meta.
router.beforeEach((to) => {
    const auth = useAuthStore();

    if (to.meta.requiresAuth && !auth.isAuthenticated) {
        return { name: 'login', query: { redirect: to.fullPath } };
    }

    if (to.meta.requiresGuest && auth.isAuthenticated) {
        return { name: 'dashboard' };
    }
});
