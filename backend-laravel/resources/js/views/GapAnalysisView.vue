<script setup>
import { onMounted, ref } from 'vue';
import { useRouter } from 'vue-router';
import { useGapAnalysisStore } from '@/stores/gapAnalysis';
import { useResumeStore } from '@/stores/resume';
import { usePostingStore } from '@/stores/posting';
import { useMatchStore } from '@/stores/match';

import GapAnalysisCreateDialog from '@/components/gapAnalysis/GapAnalysisCreateDialog.vue';

const router = useRouter();
const gapAnalysisStore = useGapAnalysisStore();
const resumeStore = useResumeStore();
const postingStore = usePostingStore();
const matchStore = useMatchStore();

const createDialogOpen = ref(false);
const deleteDialog = ref(false);
const analysisToDelete = ref(null);

onMounted(() => {
    gapAnalysisStore.fetchAll();

    console.log('after fetch:', gapAnalysisStore.analyses.length, gapAnalysisStore.analyses);

    // Preload for the dialog if needed.
    if (!resumeStore.hasResumes) resumeStore.fetchAll();
    if (!postingStore.hasPostings) postingStore.fetchAll();
    if (matchStore.matches.length === 0) matchStore.fetchAll();
});

function onCreated(analysis) {
    router.push({ name: 'gap-analysis-detail', params: { id: analysis.id } });
}

function askDelete(analysis) {
    analysisToDelete.value = analysis;
    deleteDialog.value = true;
}

async function confirmDelete() {
    if (!analysisToDelete.value) return;
    await gapAnalysisStore.destroy(analysisToDelete.value.id);
    deleteDialog.value = false;
    analysisToDelete.value = null;
}

function formatDate(iso) {
    if (!iso) return '';
    return new Date(iso).toLocaleString(undefined, {
        year: 'numeric', month: 'short', day: 'numeric',
        hour: '2-digit', minute: '2-digit',
    });
}

function topGapCanonical(analysis) {
    return analysis.ranked_gaps?.[0]?.canonical_text || '—';
}
</script>

<template>
    <div>
        <!-- Header -->
        <div class="d-flex align-center justify-space-between mb-6">
            <div>
                <h1 class="text-h4 font-weight-bold mb-1">Gap Analysis</h1>
                <p class="text-body-1 text-medium-emphasis mb-0">
                    Rank what's holding you back across your target postings.
                </p>
            </div>
            <v-btn
                color="primary"
                variant="flat"
                prepend-icon="mdi-magnify-scan"
                @click="createDialogOpen = true"
            >
                Run new analysis
            </v-btn>
        </div>

        <!-- Loading -->
        <div v-if="gapAnalysisStore.loading && gapAnalysisStore.analyses.length === 0" class="text-center py-12">
            <v-progress-circular indeterminate color="primary" />
        </div>

        <!-- Empty -->
        <v-card v-else-if="!gapAnalysisStore.hasAnalyses" class="text-center pa-8">
            <v-icon size="48" color="primary" class="mb-4">mdi-chart-bar-stacked</v-icon>
            <div class="text-h6 font-weight-medium mb-1">No analyses yet</div>
            <div class="text-body-2 text-medium-emphasis mb-4">
                Run your first gap analysis to see which skills matter most across your target postings.
            </div>
            <v-btn color="primary" variant="flat" @click="createDialogOpen = true">
                Run your first analysis
            </v-btn>
        </v-card>

        <!-- List of past runs -->
        <v-row v-else>
            <v-col
                v-for="analysis in gapAnalysisStore.analyses"
                :key="analysis.id"
                cols="12"
                md="6"
            >
                <v-card
                    class="h-100 cursor-pointer"
                    :to="{ name: 'gap-analysis-detail', params: { id: analysis.id } }"
                >
                    <v-card-item>
                        <template #prepend>
                            <v-icon color="primary" size="28">mdi-chart-bar-stacked</v-icon>
                        </template>
                        <v-card-title class="text-subtitle-1 font-weight-medium">
                            {{ analysis.total_postings }} posting{{ analysis.total_postings === 1 ? '' : 's' }} analyzed
                        </v-card-title>
                        <v-card-subtitle>
                            {{ formatDate(analysis.computed_at) }}
                        </v-card-subtitle>
                        <template #append>
                            <v-btn
                                icon="mdi-delete-outline"
                                variant="text"
                                size="small"
                                color="error"
                                @click.stop.prevent="askDelete(analysis)"
                            />
                        </template>
                    </v-card-item>

                    <v-divider />

                    <v-card-text class="pt-3">
                        <div class="text-caption text-medium-emphasis mb-1">
                            Top-ranked gap
                        </div>
                        <div class="text-body-2 font-weight-medium text-truncate">
                            {{ topGapCanonical(analysis) }}
                        </div>
                        <div class="text-caption text-medium-emphasis mt-2">
                            {{ analysis.ranked_gaps?.length || 0 }} total gaps identified
                        </div>
                    </v-card-text>
                </v-card>
            </v-col>
        </v-row>

        <!-- Dialogs -->
        <GapAnalysisCreateDialog v-model="createDialogOpen" @created="onCreated" />

        <v-dialog v-model="deleteDialog" max-width="440">
            <v-card>
                <v-card-title>Delete this analysis?</v-card-title>
                <v-card-text>
                    <p class="text-body-2 text-medium-emphasis mb-0">
                        This deletes only the snapshot. Your resumes, postings, and matches are unaffected. You can rerun the analysis at any time.
                    </p>
                </v-card-text>
                <v-card-actions>
                    <v-spacer />
                    <v-btn variant="text" @click="deleteDialog = false">Cancel</v-btn>
                    <v-btn color="error" variant="flat" @click="confirmDelete">Delete</v-btn>
                </v-card-actions>
            </v-card>
        </v-dialog>
    </div>
</template>

<style scoped>
.cursor-pointer {
    cursor: pointer;
}
</style>
