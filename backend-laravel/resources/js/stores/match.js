import { defineStore } from 'pinia';
import { computed, ref } from 'vue';
import { matchService } from '@/services/matchService';
import { extractApiError } from '@/utils/errors';

export const useMatchStore = defineStore('match', () => {
    // State
    const matches = ref([]);
    const currentMatch = ref(null);
    const loading = ref(false);
    const computing = ref(false);
    const loadingDetail = ref(false);
    const error = ref(null);

    // Getters
    const hasMatches = computed(() => matches.value.length > 0);

    // Actions
    async function fetchAll(filters = {}) {
        loading.value = true;
        error.value = null;
        try {
            const { data } = await matchService.list(filters);
            matches.value = data.matches;
        } catch (err) {
            error.value = extractApiError(err, 'Failed to load matches.');
            throw err;
        } finally {
            loading.value = false;
        }
    }

    async function fetchOne(id) {
        loadingDetail.value = true;
        error.value = null;
        try {
            const { data } = await matchService.show(id);
            currentMatch.value = data.match;
            return data.match;
        } catch (err) {
            error.value = extractApiError(err, 'Failed to load match.');
            throw err;
        } finally {
            loadingDetail.value = false;
        }
    }

    async function compute(payload) {
        computing.value = true;
        error.value = null;
        try {
            const { data } = await matchService.compute(payload);
            // Insert or replace: if a match for this resume-version + posting existed,
            // upsert semantics on the backend mean we should update in place.
            const idx = matches.value.findIndex(
                (m) => m.resume_version_id === data.match.resume_version_id
                    && m.posting_id === data.match.posting_id
            );
            if (idx >= 0) {
                matches.value[idx] = data.match;
            } else {
                matches.value = [data.match, ...matches.value];
            }
            return data.match;
        } catch (err) {
            error.value = extractApiError(err, 'Failed to compute match.');
            throw err;
        } finally {
            computing.value = false;
        }
    }

    async function destroy(id) {
        error.value = null;
        try {
            await matchService.destroy(id);
            matches.value = matches.value.filter((m) => m.id !== id);
            if (currentMatch.value?.id === id) currentMatch.value = null;
        } catch (err) {
            error.value = extractApiError(err, 'Failed to delete match.');
            throw err;
        }
    }

    function reset() {
        matches.value = [];
        currentMatch.value = null;
        loading.value = false;
        computing.value = false;
        loadingDetail.value = false;
        error.value = null;
    }

    return {
        // state
        matches, currentMatch, loading, computing, loadingDetail, error,
        // getters
        hasMatches,
        // actions
        fetchAll, fetchOne, compute, destroy, reset,
    };
});

