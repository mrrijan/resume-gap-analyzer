<script setup>
import { computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import { useResumeStore } from '@/stores/resume';
import { usePostingStore } from '@/stores/posting';
import { useMatchStore } from '@/stores/match';
import { useGapAnalysisStore } from '@/stores/gapAnalysis';
import { fitTier } from '@/constants/match';

const router = useRouter();
const authStore = useAuthStore();
const resumeStore = useResumeStore();
const postingStore = usePostingStore();
const matchStore = useMatchStore();
const gapAnalysisStore = useGapAnalysisStore();

const firstName = computed(() => authStore.user?.name?.split(' ')[0] || '');

const hasAnyData = computed(() =>
    resumeStore.resumes.length > 0 || postingStore.postings.length > 0
);

const recentMatches = computed(() =>
    [...matchStore.matches]
        .sort((a, b) => new Date(b.computed_at) - new Date(a.computed_at))
        .slice(0, 5)
);

const averageFit = computed(() => {
    if (matchStore.matches.length === 0) return null;
    const sum = matchStore.matches.reduce((acc, m) => acc + Number(m.overall_fit), 0);
    return Math.round(sum / matchStore.matches.length);
});

const latestGapAnalysis = computed(() => {
    if (gapAnalysisStore.analyses.length === 0) return null;
    return [...gapAnalysisStore.analyses]
        .sort((a, b) => new Date(b.computed_at) - new Date(a.computed_at))[0];
});

const topGap = computed(() => latestGapAnalysis.value?.ranked_gaps?.[0] || null);

function postingTitleFor(match) {
    return match.posting?.title || 'Untitled posting';
}

onMounted(() => {
    if (resumeStore.resumes.length === 0) resumeStore.fetchAll();
    if (postingStore.postings.length === 0) postingStore.fetchAll();
    if (matchStore.matches.length === 0) matchStore.fetchAll();
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

        <!-- Stat cards -->
        <v-row>
            <v-col cols="12" md="3">
                <v-card class="cursor-pointer h-100" @click="router.push({ name: 'resumes' })">
                    <v-card-item>
                        <template #prepend>
                            <v-icon color="primary" size="24">mdi-file-document-outline</v-icon>
                        </template>
                        <v-card-subtitle>Resumes</v-card-subtitle>
                        <v-card-title class="text-h4 mt-1">
                            {{ resumeStore.resumes.length }}
                        </v-card-title>
                    </v-card-item>
                </v-card>
            </v-col>
            <v-col cols="12" md="3">
                <v-card class="cursor-pointer h-100" @click="router.push({ name: 'postings' })">
                    <v-card-item>
                        <template #prepend>
                            <v-icon color="primary" size="24">mdi-briefcase-outline</v-icon>
                        </template>
                        <v-card-subtitle>Postings tracked</v-card-subtitle>
                        <v-card-title class="text-h4 mt-1">
                            {{ postingStore.postings.length }}
                        </v-card-title>
                    </v-card-item>
                </v-card>
            </v-col>
            <v-col cols="12" md="3">
                <v-card class="cursor-pointer h-100" @click="router.push({ name: 'matches' })">
                    <v-card-item>
                        <template #prepend>
                            <v-icon :color="averageFit !== null ? fitTier(averageFit).color : 'primary'" size="24">
                                mdi-scale-balance
                            </v-icon>
                        </template>
                        <v-card-subtitle>Average fit</v-card-subtitle>
                        <v-card-title class="text-h4 mt-1">
                            {{ averageFit !== null ? `${averageFit}%` : '—' }}
                        </v-card-title>
                    </v-card-item>
                </v-card>
            </v-col>
            <v-col cols="12" md="3">
                <v-card class="cursor-pointer h-100" @click="router.push({ name: 'gap-analysis' })">
                    <v-card-item>
                        <template #prepend>
                            <v-icon color="primary" size="24">mdi-chart-bar-stacked</v-icon>
                        </template>
                        <v-card-subtitle>Gap analyses</v-card-subtitle>
                        <v-card-title class="text-h4 mt-1">
                            {{ gapAnalysisStore.analyses.length }}
                        </v-card-title>
                    </v-card-item>
                </v-card>
            </v-col>
        </v-row>

        <!-- Empty state -->
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

        <!-- Populated: recent matches + top gap -->
        <v-row v-else class="mt-2">
            <v-col cols="12" md="7">
                <v-card class="h-100">
                    <v-card-item>
                        <v-card-title>Recent match scores</v-card-title>
                        <v-card-subtitle>Your latest computed fits</v-card-subtitle>
                    </v-card-item>
                    <v-divider />
                    <v-card-text v-if="recentMatches.length === 0" class="text-center py-8">
                        <v-icon size="40" color="grey" class="mb-2">mdi-scale-balance</v-icon>
                        <div class="text-body-2 text-medium-emphasis mb-3">
                            No matches computed yet.
                        </div>
                        <v-btn size="small" color="primary" variant="tonal" :to="{ name: 'matches' }">
                            Compute a match
                        </v-btn>
                    </v-card-text>
                    <v-card-text v-else>
                        <div
                            v-for="match in recentMatches"
                            :key="match.id"
                            class="match-row cursor-pointer"
                            @click="router.push({ name: 'match-detail', params: { id: match.id } })"
                        >
                            <div class="d-flex align-center justify-space-between mb-1">
                <span class="text-body-2 font-weight-medium text-truncate">
                  {{ postingTitleFor(match) }}
                </span>
                                <span
                                    class="text-body-2 font-weight-bold ms-2"
                                    :class="`text-${fitTier(Number(match.overall_fit)).color}`"
                                >
                  {{ Math.round(match.overall_fit) }}%
                </span>
                            </div>
                            <v-progress-linear
                                :model-value="Number(match.overall_fit)"
                                :color="fitTier(Number(match.overall_fit)).color"
                                bg-color="grey-lighten-3"
                                height="8"
                                rounded
                            />
                        </div>
                    </v-card-text>
                </v-card>
            </v-col>

            <v-col cols="12" md="5">
                <v-card class="h-100">
                    <v-card-item>
                        <v-card-title>Top gap</v-card-title>
                        <v-card-subtitle>From your latest gap analysis</v-card-subtitle>
                    </v-card-item>
                    <v-divider />
                    <v-card-text v-if="!topGap" class="text-center py-8">
                        <v-icon size="40" color="grey" class="mb-2">mdi-chart-bar-stacked</v-icon>
                        <div class="text-body-2 text-medium-emphasis mb-3">
                            No gap analysis run yet.
                        </div>
                        <v-btn size="small" color="primary" variant="tonal" :to="{ name: 'gap-analysis' }">
                            Run analysis
                        </v-btn>
                    </v-card-text>
                    <v-card-text v-else>
                        <v-chip color="error" variant="tonal" size="small" class="mb-3">
                            <v-icon start size="14">mdi-alert-circle-outline</v-icon>
                            Highest impact
                        </v-chip>
                        <div class="text-body-1 font-weight-medium mb-2">
                            {{ topGap.canonical_text }}
                        </div>
                        <div class="text-caption text-medium-emphasis mb-3">
                            Affects {{ Math.round(topGap.frequency * latestGapAnalysis.total_postings) }}
                            of {{ latestGapAnalysis.total_postings }} tracked postings
                        </div>
                        <v-btn
                            size="small"
                            variant="tonal"
                            color="primary"
                            :to="{ name: 'gap-analysis-detail', params: { id: latestGapAnalysis.id } }"
                        >
                            View full analysis
                        </v-btn>
                    </v-card-text>
                </v-card>
            </v-col>
        </v-row>
    </div>
</template>

<style scoped>
.cursor-pointer {
    cursor: pointer;
}
.match-row {
    padding: 10px 0;
    border-bottom: 1px solid rgb(var(--v-theme-border));
}
.match-row:last-child {
    border-bottom: none;
    padding-bottom: 0;
}
</style>
