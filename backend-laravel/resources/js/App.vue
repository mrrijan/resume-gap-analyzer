<template>
    <v-app>
        <component :is="layoutComponent">
            <router-view />
        </component>
    </v-app>
</template>

<script setup>
import { computed, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import { useAuthStore } from '@/stores/auth';

import AuthLayout from '@/layouts/AuthLayout.vue';
import AppLayout  from '@/layouts/AppLayout.vue';

const route     = useRoute();
const authStore = useAuthStore();

const layoutComponent = computed(() => {
    return route.meta.layout === 'auth' ? AuthLayout : AppLayout;
});

// Hydrate user info on app boot if we have a stored token.
onMounted(async () => {
    if (authStore.token) {
        await authStore.fetchCurrentUser();
    }
});
</script>
