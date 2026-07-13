import { defineStore } from 'pinia';
import { computed, ref } from 'vue';
import { gapAnalysisService } from '@/services/gapAnalysisService';
import { extractApiError } from '@/utils/errors';

export const useGapAnalysisStore = defineStore('gapAnalysis', () => {
    // State
    const analyses = ref([]);
    const currentAnalysis = ref(null);
    const loading = ref(false);
    const loadingDetail = ref(false);
    const creating = ref(false);
    const error = ref(null);
    // Backend can return { message, missing_posting_ids } when matches are missing.
    // Store that separately so the UI can point at what's missing.
    const missingPostingIds = ref([]);

    // Getters
    const hasAnalyses = computed(() => analyses.value.length > 0);

    // Actions
    async function fetchAll() {
        loading.value = true;
        error.value = null;
        try {
            const { data } = await gapAnalysisService.list();
            analyses.value = data.gap_analyses;
        } catch (err) {
            error.value = extractApiError(err, 'Failed to load gap analyses.');
            throw err;
        } finally {
            loading.value = false;
        }
    }

    async function fetchOne(id) {
        loadingDetail.value = true;
        error.value = null;
        try {
            const { data } = await gapAnalysisService.show(id);
            currentAnalysis.value = data.gap_analysis;
            return data.gap_analysis;
        } catch (err) {
            error.value = extractApiError(err, 'Failed to load gap analysis.');
            throw err;
        } finally {
            loadingDetail.value = false;
        }
    }

    async function create(payload) {
        creating.value = true;
        error.value = null;
        missingPostingIds.value = [];
        try {
            const { data } = await gapAnalysisService.create(payload);
            analyses.value = [data.gap_analysis, ...analyses.value];
            return data.gap_analysis;
        } catch (err) {
            // Special-case: 422 with missing_posting_ids — matches need to be computed first.
            if (err?.response?.status === 422 && err.response.data.missing_posting_ids) {
                missingPostingIds.value = err.response.data.missing_posting_ids;
                error.value = err.response.data.message
                    || 'Some postings do not have a computed match yet.';
            } else {
                error.value = extractApiError(err, 'Failed to run gap analysis.');
            }
            throw err;
        } finally {
            creating.value = false;
        }
    }

    async function destroy(id) {
        error.value = null;
        try {
            await gapAnalysisService.destroy(id);
            analyses.value = analyses.value.filter((a) => a.id !== id);
            if (currentAnalysis.value?.id === id) currentAnalysis.value = null;
        } catch (err) {
            error.value = extractApiError(err, 'Failed to delete gap analysis.');
            throw err;
        }
    }

    function reset() {
        analyses.value = [];
        currentAnalysis.value = null;
        loading.value = false;
        loadingDetail.value = false;
        creating.value = false;
        error.value = null;
        missingPostingIds.value = [];
    }

    return {
        // state
        analyses, currentAnalysis, loading, loadingDetail, creating, error, missingPostingIds,
        // getters
        hasAnalyses,
        // actions
        fetchAll, fetchOne, create, destroy, reset,
    };
});
