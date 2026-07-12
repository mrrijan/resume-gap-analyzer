<script setup>
import { computed, onMounted, ref } from 'vue';
import { useRouter } from 'vue-router';
import { useMatchStore } from '@/stores/match';
import { useResumeStore } from '@/stores/resume';
import { usePostingStore } from '@/stores/posting';

import MatchCreateDialog from '@/components/match/MatchCreateDialog.vue';
import { fitTier } from '@/constants/match';

const router = useRouter();
const matchStore = useMatchStore();
const resumeStore = useResumeStore();
const postingStore = usePostingStore();

const createDialogOpen = ref(false);
const deleteDialog = ref(false);
const matchToDelete = ref(null);

onMounted(() => {
    matchStore.fetchAll();
    // Preload for the create dialog's dropdowns.
    if (!resumeStore.hasResumes) resumeStore.fetchAll();
    if (!postingStore.hasPostings) postingStore.fetchAll();
});

function tierFor(percent) {
    return fitTier(percent);
}

function resumeLabel(match) {
    // Backend doesn't currently include resume/version metadata on the match resource,
    // so we look it up in the resume store if available.
    // Fallback to the version id if unresolved.
    for (const r of resumeStore.resumes) {
        if (r.latest_version?.id === match.resume_version_id) {
            return r.original_filename;
        }
    }
    return `Resume version #${match.resume_version_id}`;
}

function onCreated(match) {
    router.push({ name: 'match-detail', params: { id: match.id } });
}

function askDelete(match) {
    matchToDelete.value = match;
    deleteDialog.value = true;
}

async function confirmDelete() {
    if (!matchToDelete.value) return;
    await matchStore.destroy(matchToDelete.value.id);
    deleteDialog.value = false;
    matchToDelete.value = null;
}

function formatDate(iso) {
    if (!iso) return '';
    return new Date(iso).toLocaleDateString(undefined, {
        year: 'numeric', month: 'short', day: 'numeric',
    });
}
</script>

<template>
    <div>
        <!-- Header -->
        <div class="d-flex align-center justify-space-between mb-6">
            <div>
                <h1 class="text-h4 font-weight-bold mb-1">Matches</h1>
                <p class="text-body-1 text-medium-emphasis mb-0">
                    Fit scores between your resumes and target postings.
                </p>
            </div>
            <v-btn
                color="primary"
                variant="flat"
                prepend-icon="mdi-calculator"
                @click="createDialogOpen = true"
            >
                Compute match
            </v-btn>
        </div>

        <!-- Loading -->
        <div v-if="matchStore.loading && matchStore.matches.length === 0" class="text-center py-12">
            <v-progress-circular indeterminate color="primary" />
        </div>

        <!-- Empty -->
        <v-card v-else-if="!matchStore.hasMatches" class="text-center pa-8">
            <v-icon size="48" color="primary" class="mb-4">mdi-scale-balance</v-icon>
            <div class="text-h6 font-weight-medium mb-1">No matches yet</div>
            <div class="text-body-2 text-medium-emphasis mb-4">
                Compute your first match to see how a resume stacks up against a posting.
            </div>
            <v-btn color="primary" variant="flat" @click="createDialogOpen = true">
                Compute your first match
            </v-btn>
        </v-card>

        <!-- List -->
        <v-row v-else>
            <v-col
                v-for="match in matchStore.matches"
                :key="match.id"
                cols="12"
                md="6"
                lg="4"
            >
                <v-card
                    class="h-100 cursor-pointer"
                    :to="{ name: 'match-detail', params: { id: match.id } }"
                >
                    <v-card-item>
                        <template #prepend>
                            <v-progress-circular
                                :model-value="Math.round(match.overall_fit)"
                                :size="52"
                                :width="5"
                                :color="tierFor(match.overall_fit).color"
                                bg-color="grey-lighten-3"
                            >
                <span class="text-caption font-weight-bold">
                  {{ Math.round(match.overall_fit) }}
                </span>
                            </v-progress-circular>
                        </template>
                        <v-card-title class="text-subtitle-1 font-weight-medium text-truncate">
                            {{ match.posting?.title || 'Untitled posting' }}
                        </v-card-title>
                        <v-card-subtitle class="text-truncate">
                            vs. {{ resumeLabel(match) }}
                        </v-card-subtitle>
                        <template #append>
                            <v-btn
                                icon="mdi-delete-outline"
                                variant="text"
                                size="small"
                                color="error"
                                @click.stop.prevent="askDelete(match)"
                            />
                        </template>
                    </v-card-item>

                    <v-divider />

                    <v-card-text class="pt-3">
                        <v-chip
                            :color="tierFor(match.overall_fit).color"
                            variant="tonal"
                            size="small"
                            class="mb-2"
                        >
                            {{ tierFor(match.overall_fit).label }}
                        </v-chip>
                        <div class="text-caption text-medium-emphasis">
                            Computed {{ formatDate(match.computed_at) }}
                        </div>
                    </v-card-text>
                </v-card>
            </v-col>
        </v-row>

        <!-- Dialogs -->
        <MatchCreateDialog v-model="createDialogOpen" @created="onCreated" />

        <v-dialog v-model="deleteDialog" max-width="440">
            <v-card>
                <v-card-title>Delete this match?</v-card-title>
                <v-card-text>
                    <p class="text-body-2 text-medium-emphasis mb-0">
                        You can recompute it later. This action cannot be undone.
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
