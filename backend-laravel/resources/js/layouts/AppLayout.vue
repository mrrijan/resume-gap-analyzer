<template>
    <v-app>
        <!-- Left sidebar -->
        <v-navigation-drawer
            :model-value="true"
            permanent
            width="260"
        >
            <div class="d-flex align-center px-4 py-4">
                <v-icon color="primary" size="28" class="me-2">mdi-check-decagram</v-icon>
                <span class="text-h6 font-weight-bold">Alignr</span>
            </div>

            <v-divider />

            <v-list nav density="comfortable" class="px-2 py-2">
                <v-list-subheader class="text-uppercase text-caption">
                    Workspace
                </v-list-subheader>

                <v-list-item
                    v-for="item in navItems"
                    :key="item.name"
                    :to="{ name: item.route }"
                    :prepend-icon="item.icon"
                    :title="item.label"
                    rounded="lg"
                    color="primary"
                />
            </v-list>

            <template #append>
                <v-divider />
                <div class="pa-3">
                    <div class="d-flex align-center">
                        <v-avatar color="primary" size="36" class="me-3">
              <span class="text-white text-body-2 font-weight-medium">
                {{ userInitials }}
              </span>
                        </v-avatar>
                        <div class="flex-grow-1 min-width-0">
                            <div class="text-body-2 font-weight-medium text-truncate">
                                {{ authStore.user?.name || '—' }}
                            </div>
                            <div class="text-caption text-medium-emphasis text-truncate">
                                {{ authStore.user?.email || '' }}
                            </div>
                        </div>
                        <v-btn
                            icon="mdi-logout"
                            variant="text"
                            size="small"
                            @click="handleLogout"
                        />
                    </div>
                </div>
            </template>
        </v-navigation-drawer>

        <!-- Main content -->
        <v-main>
            <v-container fluid class="py-6 px-8">
                <slot />
            </v-container>
        </v-main>
    </v-app>
</template>

<script setup>
import { computed } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';

const authStore = useAuthStore();
const router    = useRouter();

const navItems = [
    { name: 'dashboard',    label: 'Dashboard',    icon: 'mdi-view-dashboard-outline', route: 'dashboard' },
    { name: 'resumes',   label: 'Resumes',   icon: 'mdi-file-document-outline',  route: 'resumes' },
    { name: 'postings',  label: 'Postings',  icon: 'mdi-briefcase-outline',      route: 'postings' },
    { name: 'matches',   label: 'Matches',   icon: 'mdi-scale-balance',          route: 'matches'  },
    // more items added as we build the features
];

const userInitials = computed(() => {
    const name = authStore.user?.name || '';
    return name
        .split(' ')
        .map((part) => part.charAt(0).toUpperCase())
        .slice(0, 2)
        .join('') || '?';
});

async function handleLogout() {
    await authStore.logout();
    router.push({ name: 'login' });
}
</script>
