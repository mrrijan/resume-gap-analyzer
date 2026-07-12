import { defineStore } from 'pinia';
import { computed, ref } from 'vue';
import { resumeService } from '@/services/resumeService';
import { extractApiError } from '@/utils/errors';

/**
 * Resume store — holds the user's uploaded resumes and orchestrates
 * upload/delete actions against the backend.
 */
export const useResumeStore = defineStore('resume', () => {
    // State
    const resumes = ref([]);
    const loading = ref(false);
    const uploading = ref(false);
    const error = ref(null);

    // Getters
    const hasResumes = computed(() => resumes.value.length > 0);
    const latestResume = computed(() => resumes.value[0] || null);

    // Actions
    async function fetchAll() {
        loading.value = true;
        error.value = null;
        try {
            const { data } = await resumeService.list();
            // Backend returns them ordered by created_at desc; latest first.
            resumes.value = data.resumes;
        } catch (err) {
            error.value = extractApiError(err, 'Failed to load resumes.');
            throw err;
        } finally {
            loading.value = false;
        }
    }

    async function upload(file) {
        uploading.value = true;
        error.value = null;
        try {
            const { data } = await resumeService.upload(file);
            // Prepend the new resume to the list.
            resumes.value = [data.resume, ...resumes.value];
            return data.resume;
        } catch (err) {
            error.value = extractApiError(err, 'Failed to upload resume.');
            throw err;
        } finally {
            uploading.value = false;
        }
    }

    async function destroy(id) {
        error.value = null;
        try {
            await resumeService.destroy(id);
            resumes.value = resumes.value.filter((r) => r.id !== id);
        } catch (err) {
            error.value = extractApiError(err, 'Failed to delete resume.');
            throw err;
        }
    }

    function reset() {
        resumes.value = [];
        loading.value = false;
        uploading.value = false;
        error.value = null;
    }

    return {
        // state
        resumes, loading, uploading, error,
        // getters
        hasResumes, latestResume,
        // actions
        fetchAll, upload, destroy, reset,
    };
});
