<script setup>
import {computed, onMounted, ref, nextTick} from 'vue';
import {useResumeStore} from '@/stores/resume';

import ResumeUploader from '@/components/resume/ResumeUploader.vue';
import ResumeParsedDisplay from '@/components/resume/ResumeParsedDisplay.vue';

const resumeStore = useResumeStore();

const deleteDialog = ref(false);
const resumeToDelete = ref(null);
const selectedResumeId = ref(null);

onMounted(() => {
    resumeStore.fetchAll();
});

const displayedResume = computed(() => {
    if (selectedResumeId.value) {
        return resumeStore.resumes.find(r => r.id === selectedResumeId.value)
            || resumeStore.latestResume;
    }
    return resumeStore.latestResume;
});

function askDelete(resume) {
    resumeToDelete.value = resume;
    deleteDialog.value = true;
}

async function onUploaded(resume) {
    selectedResumeId.value = resume.id;
    await nextTick();  // wait for the DOM to update
    document.querySelector('[data-parsed-anchor]')?.scrollIntoView({
        behavior: 'smooth',
        block: 'start',
    });
}

async function confirmDelete() {
    if (!resumeToDelete.value) return;
    const deletedId = resumeToDelete.value.id;
    await resumeStore.destroy(deletedId);
    if (selectedResumeId.value === deletedId) {
        selectedResumeId.value = null;
    }
    deleteDialog.value = false;
    resumeToDelete.value = null;
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
        <!-- Page header -->
        <div class="d-flex align-center justify-space-between mb-6">
            <div>
                <h1 class="text-h4 font-weight-bold mb-1">Resumes</h1>
                <p class="text-body-1 text-medium-emphasis mb-0">
                    Upload a resume to analyze against your target job postings.
                </p>
            </div>
        </div>

        <!-- Loading state -->
        <div v-if="resumeStore.loading && resumeStore.resumes.length === 0" class="text-center py-12">
            <v-progress-circular indeterminate color="primary"/>
        </div>

        <!-- Empty state -->
        <div v-else-if="!resumeStore.hasResumes">
            <ResumeUploader  @uploaded="onUploaded"/>
        </div>

        <!-- Populated -->
        <div v-else>
            <!-- List of resumes -->
            <div class="mb-6">
                <div class="text-subtitle-2 text-medium-emphasis mb-3">
                    Your resumes ({{ resumeStore.resumes.length }})
                </div>

                <v-row>
                    <v-col
                        v-for="resume in resumeStore.resumes"
                        :key="resume.id"
                        cols="12"
                        md="6"
                        lg="4"
                    >
                        <v-card
                            :variant="selectedResumeId === resume.id
                            || (!selectedResumeId && resume.id === resumeStore.latestResume?.id)
                            ? 'tonal'
                            : 'elevated'"
                            :color="selectedResumeId === resume.id
                            || (!selectedResumeId && resume.id === resumeStore.latestResume?.id)
                            ? 'primary'
                            : undefined"
                            class="cursor-pointer"
                            @click="selectedResumeId = resume.id"
                        >
                            <v-card-item>
                                <template #prepend>
                                    <v-icon color="primary" size="28">mdi-file-document-outline</v-icon>
                                </template>
                                <v-card-title class="text-subtitle-1 font-weight-medium text-truncate">
                                    {{ resume.original_filename }}
                                </v-card-title>
                                <v-card-subtitle>
                                    Uploaded {{ formatDate(resume.created_at) }}
                                </v-card-subtitle>
                                <template #append>
                                    <v-btn
                                        icon="mdi-delete-outline"
                                        variant="text"
                                        size="small"
                                        color="error"
                                        @click.stop="askDelete(resume)"
                                    />
                                </template>
                            </v-card-item>
                        </v-card>
                    </v-col>
                </v-row>
            </div>

            <!-- Upload another -->
            <div class="mb-6">
                <div class="text-subtitle-2 text-medium-emphasis mb-3">
                    Upload another
                </div>
                <ResumeUploader  @uploaded="onUploaded"/>
            </div>

            <!-- Parsed sections of latest -->
            <div>
                <div class="text-subtitle-2 text-medium-emphasis mb-3" data-parsed-anchor>
                    {{ displayedResume?.original_filename }} &middot; parsed sections
                </div>
                <ResumeParsedDisplay :resume="displayedResume" />
            </div>
        </div>

        <!-- Delete confirmation -->
        <v-dialog v-model="deleteDialog" max-width="440">
            <v-card>
                <v-card-title>Delete this resume?</v-card-title>
                <v-card-text>
                    <p class="mb-2">
                        <strong>{{ resumeToDelete?.original_filename }}</strong>
                    </p>
                    <p class="text-body-2 text-medium-emphasis mb-0">
                        This will also remove any matches computed against this resume. This action cannot be undone.
                    </p>
                </v-card-text>
                <v-card-actions>
                    <v-spacer/>
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
