<script setup>
import { computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import { useResumeStore } from '@/stores/resume';
import { usePostingStore } from '@/stores/posting';
import { useGapAnalysisStore } from '@/stores/gapAnalysis';

const router = useRouter();
const authStore = useAuthStore();
const resumeStore = useResumeStore();
const postingStore = usePostingStore();
const gapAnalysisStore = useGapAnalysisStore();

const firstName = computed(() => authStore.user?.name?.split(' ')[0] || '');

const hasAnyData = computed(() =>
    resumeStore.resumes.length > 0 || postingStore.postings.length > 0
);

onMounted(() => {
    if (resumeStore.resumes.length === 0) resumeStore.fetchAll();
    if (postingStore.postings.length === 0) postingStore.fetchAll();
    if (gapAnalysisStore.analyses.length === 0) gapAnalysisStore.fetchAll();
});
</script>

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
                <v-card class="cursor-pointer" @click="router.push({ name: 'resumes' })">
                    <v-card-item>
                        <v-card-subtitle>Resumes</v-card-subtitle>
                        <v-card-title class="text-h4 mt-1">
                            {{ resumeStore.resumes.length }}
                        </v-card-title>
                    </v-card-item>
                </v-card>
            </v-col>
            <v-col cols="12" md="4">
                <v-card class="cursor-pointer" @click="router.push({ name: 'postings' })">
                    <v-card-item>
                        <v-card-subtitle>Postings tracked</v-card-subtitle>
                        <v-card-title class="text-h4 mt-1">
                            {{ postingStore.postings.length }}
                        </v-card-title>
                    </v-card-item>
                </v-card>
            </v-col>
            <v-col cols="12" md="4">
                <v-card class="cursor-pointer" @click="router.push({ name: 'gap-analysis' })">
                    <v-card-item>
                        <v-card-subtitle>Gap analyses</v-card-subtitle>
                        <v-card-title class="text-h4 mt-1">
                            {{ gapAnalysisStore.analyses.length }}
                        </v-card-title>
                    </v-card-item>
                </v-card>
            </v-col>
        </v-row>

        <v-card v-if="!hasAnyData" class="mt-6">
            <v-card-item>
                <v-card-title>Get started</v-card-title>
                <v-card-subtitle class="mt-1">
                    Upload your resume and add target postings to see fit scores and gap analysis.
                </v-card-subtitle>
            </v-card-item>
            <v-card-actions class="px-4 pb-4">
                <v-btn color="primary" variant="flat" :to="{ name: 'resumes' }">
                    Upload resume
                </v-btn>
                <v-btn variant="tonal" :to="{ name: 'postings' }">
                    Add a posting
                </v-btn>
            </v-card-actions>
        </v-card>

        <v-card v-else class="mt-6">
            <v-card-item>
                <v-card-title>Quick actions</v-card-title>
            </v-card-item>
            <v-card-actions class="px-4 pb-4 flex-wrap ga-2">
                <v-btn color="primary" variant="flat" :to="{ name: 'resumes' }">
                    Manage resumes
                </v-btn>
                <v-btn variant="tonal" :to="{ name: 'postings' }">
                    Manage postings
                </v-btn>
                <v-btn variant="tonal" :to="{ name: 'matches' }">
                    View matches
                </v-btn>
                <v-btn variant="tonal" :to="{ name: 'gap-analysis' }">
                    Run gap analysis
                </v-btn>
            </v-card-actions>
        </v-card>
    </div>
</template>

<style scoped>
.cursor-pointer {
    cursor: pointer;
}
</style>
