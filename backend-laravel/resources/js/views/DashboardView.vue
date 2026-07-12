<template>
    <div>
        <div class="mb-6">
            <h1 class="text-h4 font-weight-bold mb-1">
                Welcome back{{ firstName ? `, ${firstName}` : '' }}
            </h1>
            <p class="text-body-1 text-medium-emphasis">
                Your resume-to-job matching workspace.
            </p>
        </div>

        <v-row>
            <v-col cols="12" md="4">
                <v-card>
                    <v-card-item>
                        <v-card-subtitle>Resumes</v-card-subtitle>
                        <v-card-title class="text-h4 mt-1">0</v-card-title>
                    </v-card-item>
                </v-card>
            </v-col>
            <v-col cols="12" md="4">
                <v-card>
                    <v-card-item>
                        <v-card-subtitle>Postings tracked</v-card-subtitle>
                        <v-card-title class="text-h4 mt-1">0</v-card-title>
                    </v-card-item>
                </v-card>
            </v-col>
            <v-col cols="12" md="4">
                <v-card>
                    <v-card-item>
                        <v-card-subtitle>Gap analyses</v-card-subtitle>
                        <v-card-title class="text-h4 mt-1">0</v-card-title>
                    </v-card-item>
                </v-card>
            </v-col>
        </v-row>

        <v-card class="mt-6">
            <v-card-item>
                <v-card-title>Get started</v-card-title>
                <v-card-subtitle class="mt-1">
                    Upload your resume and add target postings to see fit scores and gap analysis.
                </v-card-subtitle>
            </v-card-item>
        </v-card>
    </div>
</template>

<script setup>
import { computed } from 'vue';
import { useAuthStore } from '@/stores/auth';

const authStore = useAuthStore();

const firstName = computed(() => {
    return authStore.user?.name?.split(' ')[0] || '';
});
</script>
