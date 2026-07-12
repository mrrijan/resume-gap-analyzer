<script setup>
import { computed, ref, watch } from 'vue';
import { useResumeStore } from '@/stores/resume';
import { usePostingStore } from '@/stores/posting';
import { useMatchStore } from '@/stores/match';

const props = defineProps({
    modelValue:            { type: Boolean, required: true },
    preselectedResumeId:   { type: Number,  default: null },
    preselectedPostingId:  { type: Number,  default: null },
});

const emit = defineEmits(['update:modelValue', 'created']);

const resumeStore = useResumeStore();
const postingStore = usePostingStore();
const matchStore = useMatchStore();

const isOpen = computed({
    get: () => props.modelValue,
    set: (v) => emit('update:modelValue', v),
});

const form = ref({
    resume_id: null,
    posting_id: null,
});

const resumeOptions = computed(() => resumeStore.resumes.map((r) => ({
    title: r.original_filename,
    value: r.id,
})));

const postingOptions = computed(() => postingStore.postings.map((p) => ({
    title: p.title || 'Untitled posting',
    value: p.id,
})));

const canSubmit = computed(() =>
    form.value.resume_id !== null &&
    form.value.posting_id !== null &&
    !matchStore.computing
);

// Prefill / reset whenever the dialog opens.
watch(isOpen, async (open) => {
    if (!open) return;

    // Make sure our option lists are populated — safe even if already loaded.
    if (!resumeStore.hasResumes) await resumeStore.fetchAll().catch(() => {});
    if (!postingStore.hasPostings) await postingStore.fetchAll().catch(() => {});

    form.value = {
        resume_id: props.preselectedResumeId
            || resumeStore.latestResume?.id
            || null,
        posting_id: props.preselectedPostingId ?? null,
    };
    matchStore.error = null;
});

async function submit() {
    if (!canSubmit.value) return;
    try {
        const match = await matchStore.compute({ ...form.value });
        emit('created', match);
        isOpen.value = false;
    } catch {
        // store.error already set; alert renders below
    }
}
</script>

<template>
    <v-dialog v-model="isOpen" max-width="560" persistent>
        <v-card>
            <v-card-item>
                <v-card-title>Compute a match</v-card-title>
                <v-card-subtitle class="mt-1">
                    Pick a resume and posting. We'll score how well they fit and classify each requirement.
                </v-card-subtitle>
            </v-card-item>

            <v-card-text>
                <v-alert
                    v-if="matchStore.error"
                    type="error"
                    variant="tonal"
                    density="compact"
                    class="mb-4"
                >
                    {{ matchStore.error }}
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

                <v-select
                    v-model="form.resume_id"
                    label="Resume"
                    :items="resumeOptions"
                    item-title="title"
                    item-value="value"
                    :disabled="!resumeStore.hasResumes || matchStore.computing"
                    prepend-inner-icon="mdi-file-document-outline"
                />

                <v-select
                    v-model="form.posting_id"
                    label="Posting"
                    :items="postingOptions"
                    item-title="title"
                    item-value="value"
                    :disabled="!postingStore.hasPostings || matchStore.computing"
                    prepend-inner-icon="mdi-briefcase-outline"
                />
            </v-card-text>

            <v-divider />

            <v-card-actions class="pa-4">
                <v-spacer />
                <v-btn
                    variant="text"
                    :disabled="matchStore.computing"
                    @click="isOpen = false"
                >
                    Cancel
                </v-btn>
                <v-btn
                    color="primary"
                    variant="flat"
                    :loading="matchStore.computing"
                    :disabled="!canSubmit"
                    @click="submit"
                >
                    Compute match
                </v-btn>
            </v-card-actions>
        </v-card>
    </v-dialog>
</template>
