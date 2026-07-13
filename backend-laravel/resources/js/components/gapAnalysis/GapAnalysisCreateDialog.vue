<script setup>
import { computed, ref, watch } from 'vue';
import { useResumeStore } from '@/stores/resume';
import { usePostingStore } from '@/stores/posting';
import { useMatchStore } from '@/stores/match';
import { useGapAnalysisStore } from '@/stores/gapAnalysis';
import { RECOMMENDED_MIN_POSTINGS } from '@/constants/gapAnalysis';

const props = defineProps({
    modelValue: { type: Boolean, required: true },
});
const emit = defineEmits(['update:modelValue', 'created']);

const resumeStore = useResumeStore();
const postingStore = usePostingStore();
const matchStore = useMatchStore();
const gapAnalysisStore = useGapAnalysisStore();

const isOpen = computed({
    get: () => props.modelValue,
    set: (v) => emit('update:modelValue', v),
});

const form = ref({
    resume_id: null,
    posting_ids: [],
});

const resumeOptions = computed(() => resumeStore.resumes.map((r) => ({
    title: r.original_filename,
    value: r.id,
})));

/**
 * For each posting: whether the currently-selected resume has a match for it.
 * We look up matches by resume_version_id, which we get from the resume's
 * latest_version.
 */
const selectedResume = computed(() =>
    resumeStore.resumes.find(r => r.id === form.value.resume_id) || null
);

const currentVersionId = computed(() =>
    selectedResume.value?.latest_version?.id || null
);

const postingsWithMatchInfo = computed(() => {
    const versionId = currentVersionId.value;
    return postingStore.postings.map((p) => ({
        ...p,
        hasMatch: versionId !== null && matchStore.matches.some(
            m => m.resume_version_id === versionId && m.posting_id === p.id
        ),
    }));
});

const selectedCount = computed(() => form.value.posting_ids.length);
const selectedWithoutMatch = computed(() =>
    form.value.posting_ids.filter(id =>
        !postingsWithMatchInfo.value.find(p => p.id === id)?.hasMatch
    )
);

const canSubmit = computed(() =>
    form.value.resume_id !== null &&
    selectedCount.value >= 1 &&
    !gapAnalysisStore.creating
);

const showLowCountHint = computed(() =>
    selectedCount.value > 0 && selectedCount.value < RECOMMENDED_MIN_POSTINGS
);

// Prefill / reset when dialog opens.
watch(isOpen, async (open) => {
    if (!open) return;

    // Preload lists we depend on.
    if (!resumeStore.hasResumes) await resumeStore.fetchAll().catch(() => {});
    if (!postingStore.hasPostings) await postingStore.fetchAll().catch(() => {});
    if (matchStore.matches.length === 0) await matchStore.fetchAll().catch(() => {});

    form.value = {
        resume_id: resumeStore.latestResume?.id || null,
        posting_ids: [],
    };
    gapAnalysisStore.error = null;
    gapAnalysisStore.missingPostingIds = [];
});

function selectAllWithMatch() {
    form.value.posting_ids = postingsWithMatchInfo.value
        .filter(p => p.hasMatch)
        .map(p => p.id);
}

function clearSelection() {
    form.value.posting_ids = [];
}

function togglePosting(id) {
    const idx = form.value.posting_ids.indexOf(id);
    if (idx >= 0) {
        form.value.posting_ids.splice(idx, 1);
    } else {
        form.value.posting_ids.push(id);
    }
}

async function submit() {
    if (!canSubmit.value) return;
    try {
        const analysis = await gapAnalysisStore.create({ ...form.value });
        emit('created', analysis);
        isOpen.value = false;
    } catch {
        // Store already recorded error. The missing_posting_ids UI reads from
        // gapAnalysisStore.missingPostingIds — no extra handling here.
    }
}
</script>

<template>
    <v-dialog v-model="isOpen" max-width="720" persistent scrollable>
        <v-card>
            <v-card-item>
                <v-card-title>Run gap analysis</v-card-title>
                <v-card-subtitle class="mt-1">
                    Pick a resume and the postings to include. We'll rank gaps by frequency across your selected postings.
                </v-card-subtitle>
            </v-card-item>

            <v-card-text style="max-height: 60vh;">
                <v-alert
                    v-if="gapAnalysisStore.error"
                    type="error"
                    variant="tonal"
                    density="compact"
                    class="mb-4"
                >
                    {{ gapAnalysisStore.error }}
                    <div v-if="gapAnalysisStore.missingPostingIds.length" class="mt-2 text-caption">
                        Missing matches for posting IDs: {{ gapAnalysisStore.missingPostingIds.join(', ') }}.
                        Compute those from the Matches page first.
                    </div>
                </v-alert>

                <v-alert
                    v-if="!resumeStore.hasResumes"
                    type="warning"
                    variant="tonal"
                    density="compact"
                    class="mb-4"
                >
                    You haven't uploaded a resume yet.
                </v-alert>

                <v-alert
                    v-if="!postingStore.hasPostings"
                    type="warning"
                    variant="tonal"
                    density="compact"
                    class="mb-4"
                >
                    You haven't added any postings yet.
                </v-alert>

                <!-- Resume selector -->
                <v-select
                    v-model="form.resume_id"
                    label="Resume"
                    :items="resumeOptions"
                    item-title="title"
                    item-value="value"
                    :disabled="!resumeStore.hasResumes || gapAnalysisStore.creating"
                    prepend-inner-icon="mdi-file-document-outline"
                    class="mb-4"
                />

                <!-- Posting multi-select -->
                <div v-if="postingStore.hasPostings">
                    <div class="d-flex align-center justify-space-between mb-2">
                        <div class="text-subtitle-2">
                            Postings to include
                            <span class="text-caption text-medium-emphasis ms-1">
                ({{ selectedCount }} selected)
              </span>
                        </div>
                        <div class="d-flex ga-2">
                            <v-btn
                                size="small"
                                variant="text"
                                :disabled="gapAnalysisStore.creating"
                                @click="selectAllWithMatch"
                            >
                                Select all with matches
                            </v-btn>
                            <v-btn
                                size="small"
                                variant="text"
                                :disabled="gapAnalysisStore.creating"
                                @click="clearSelection"
                            >
                                Clear
                            </v-btn>
                        </div>
                    </div>

                    <v-alert
                        v-if="showLowCountHint"
                        type="info"
                        variant="tonal"
                        density="compact"
                        class="mb-3"
                    >
                        Cross-posting ranking is most meaningful with {{ RECOMMENDED_MIN_POSTINGS }} or more postings.
                    </v-alert>

                    <v-alert
                        v-if="selectedWithoutMatch.length > 0"
                        type="warning"
                        variant="tonal"
                        density="compact"
                        class="mb-3"
                    >
                        {{ selectedWithoutMatch.length }} of your selected postings don't have a computed match against this resume yet. Compute them from Matches first.
                    </v-alert>

                    <div class="posting-list">
                        <div
                            v-for="posting in postingsWithMatchInfo"
                            :key="posting.id"
                            class="posting-item"
                            :class="{ 'posting-item--selected': form.posting_ids.includes(posting.id) }"
                            @click="togglePosting(posting.id)"
                        >
                            <v-checkbox-btn
                                :model-value="form.posting_ids.includes(posting.id)"
                                :disabled="gapAnalysisStore.creating"
                                @click.stop="togglePosting(posting.id)"
                            />
                            <div class="flex-grow-1 min-width-0">
                                <div class="text-body-2 font-weight-medium text-truncate">
                                    {{ posting.title || 'Untitled posting' }}
                                </div>
                                <div class="text-caption text-medium-emphasis">
                                    <v-icon size="12" class="me-1">
                                        {{ posting.hasMatch ? 'mdi-check-circle' : 'mdi-alert-circle-outline' }}
                                    </v-icon>
                                    {{ posting.hasMatch ? 'Match available' : 'No match yet' }}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </v-card-text>

            <v-divider />

            <v-card-actions class="pa-4">
                <v-spacer />
                <v-btn
                    variant="text"
                    :disabled="gapAnalysisStore.creating"
                    @click="isOpen = false"
                >
                    Cancel
                </v-btn>
                <v-btn
                    color="primary"
                    variant="flat"
                    :loading="gapAnalysisStore.creating"
                    :disabled="!canSubmit"
                    @click="submit"
                >
                    Run analysis
                </v-btn>
            </v-card-actions>
        </v-card>
    </v-dialog>
</template>

<style scoped>
.posting-list {
    display: flex;
    flex-direction: column;
    gap: 4px;
    max-height: 320px;
    overflow-y: auto;
    border: 1px solid rgb(var(--v-theme-border));
    border-radius: 6px;
    padding: 6px;
}
.posting-item {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 8px 10px;
    border-radius: 6px;
    cursor: pointer;
    transition: background-color 0.15s ease;
}
.posting-item:hover {
    background-color: rgba(37, 99, 235, 0.04);
}
.posting-item--selected {
    background-color: rgba(37, 99, 235, 0.08);
}
</style>
