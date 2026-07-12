import { defineStore } from 'pinia';
import { computed, ref } from 'vue';
import { postingService } from '@/services/postingService';
import { extractApiError } from '@/utils/errors';

export const usePostingStore = defineStore('posting', () => {
    // State
    const postings = ref([]);
    const loading = ref(false);
    const creating = ref(false);
    const error = ref(null);

    // Getters
    const hasPostings = computed(() => postings.value.length > 0);
    const latestPosting = computed(() => postings.value[0] || null);

    // Actions
    async function fetchAll() {
        loading.value = true;
        error.value = null;
        try {
            const { data } = await postingService.list();
            postings.value = data.postings;
        } catch (err) {
            error.value = extractApiError(err, 'Failed to load postings.');
            throw err;
        } finally {
            loading.value = false;
        }
    }

    async function create(payload) {
        creating.value = true;
        error.value = null;
        try {
            const { data } = await postingService.create(payload);
            postings.value = [data.posting, ...postings.value];
            return data.posting;
        } catch (err) {
            error.value = extractApiError(err, 'Failed to add posting.');
            throw err;
        } finally {
            creating.value = false;
        }
    }

    async function destroy(id) {
        error.value = null;
        try {
            await postingService.destroy(id);
            postings.value = postings.value.filter((p) => p.id !== id);
        } catch (err) {
            error.value = extractApiError(err, 'Failed to delete posting.');
            throw err;
        }
    }

    function reset() {
        postings.value = [];
        loading.value = false;
        creating.value = false;
        error.value = null;
    }

    return {
        // state
        postings, loading, creating, error,
        // getters
        hasPostings, latestPosting,
        // actions
        fetchAll, create, destroy, reset,
    };
});

