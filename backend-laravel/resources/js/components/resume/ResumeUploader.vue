<script setup>
import { ref } from 'vue';
import { useResumeStore } from '@/stores/resume';
import { RESUME_UPLOAD } from '@/constants/resume';

const emit = defineEmits(['uploaded']);

const resumeStore = useResumeStore();

const fileInput = ref(null);
const isDragging = ref(false);
const localError = ref('');

function openFilePicker() {
    fileInput.value?.click();
}

function onFileSelected(event) {
    const file = event.target.files?.[0];
    if (file) handleFile(file);
    // Reset the input so selecting the same file again still fires change.
    event.target.value = '';
}

function onDrop(event) {
    isDragging.value = false;
    const file = event.dataTransfer.files?.[0];
    if (file) handleFile(file);
}

async function handleFile(file) {
    localError.value = '';

    // Client-side validation — fail fast before the round trip.
    if (!RESUME_UPLOAD.acceptedMimeTypes.includes(file.type)) {
        localError.value = 'Only PDF and DOCX files are accepted.';
        return;
    }
    if (file.size > RESUME_UPLOAD.maxSizeBytes) {
        localError.value = `File must be under ${RESUME_UPLOAD.maxSizeMb} MB.`;
        return;
    }

    try {
        const resume = await resumeStore.upload(file);
        emit('uploaded', resume);
    } catch {
        // Store already set `error`; nothing extra needed here.
    }
}
</script>

<template>
    <v-card
        :class="['uploader', { 'uploader--dragging': isDragging }]"
        @dragover.prevent="isDragging = true"
        @dragleave.prevent="isDragging = false"
        @drop.prevent="onDrop"
    >
        <div class="d-flex flex-column align-center text-center pa-8">
            <v-icon
                size="48"
                color="primary"
                class="mb-4"
            >
                mdi-cloud-upload-outline
            </v-icon>

            <div class="text-h6 font-weight-medium mb-1">
                Upload your resume
            </div>
            <div class="text-body-2 text-medium-emphasis mb-5">
                PDF or DOCX &middot; up to {{ RESUME_UPLOAD.maxSizeMb }} MB
            </div>

            <v-btn
                color="primary"
                size="large"
                :loading="resumeStore.uploading"
                @click="openFilePicker"
            >
                <v-icon start>mdi-file-upload-outline</v-icon>
                Choose file
            </v-btn>

            <div class="text-caption text-medium-emphasis mt-3">
                or drop a file here
            </div>

            <v-alert
                v-if="localError || resumeStore.error"
                type="error"
                variant="tonal"
                density="compact"
                class="mt-4 w-100"
            >
                {{ localError || resumeStore.error }}
            </v-alert>
        </div>

        <input
            ref="fileInput"
            type="file"
            :accept="RESUME_UPLOAD.acceptedTypes"
            class="d-none"
            @change="onFileSelected"
        />
    </v-card>
</template>

<style scoped>
.uploader {
    transition: border-color 0.2s ease, background-color 0.2s ease;
}
.uploader--dragging {
    border-color: rgb(var(--v-theme-primary)) !important;
    background-color: rgba(37, 99, 235, 0.04);
}
</style>
