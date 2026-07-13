<script setup>
import { computed, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useGapAnalysisStore } from '@/stores/gapAnalysis';
import { usePostingStore } from '@/stores/posting';
import { RECOMMENDED_MIN_POSTINGS } from '@/constants/gapAnalysis';

import GapStatCard from '@/components/gapAnalysis/GapStatCard.vue';
import RankedGapCard from '@/components/gapAnalysis/RankedGapCard.vue';

const route = useRoute();
const router = useRouter();
const gapAnalysisStore = useGapAnalysisStore();
const postingStore = usePostingStore();

const analysis = computed(() => gapAnalysisStore.currentAnalysis);

const totalPostings = computed(() => analysis.value?.total_postings || 0);
const topGap = computed(() => analysis.value?.ranked_gaps?.[0] || null);
const gapCount = computed(() => analysis.value?.ranked_gaps?.length || 0);

// Look up posting titles by ID for the ranked gap cards.
const postingLookup = computed(() => {
    const map = {};
    for (const p of postingStore.postings) {
        map[p.id] = p.title || 'Untitled posting';
    }
    return map;
});

// Warning when analysis was run with too few postings for meaningful ranking.
const lowPostingsWarning = computed(() =>
    totalPostings.value > 0 && totalPostings.value < RECOMMENDED_MIN_POSTINGS
);

const computedDateFull = computed(() => {
    if (!analysis.value?.computed_at) return '';
    return new Date(analysis.value.computed_at).toLocaleString(undefined, {
        year: 'numeric', month: 'long', day: 'numeric',
        hour: '2-digit', minute: '2-digit',
    });
});

onMounted(() => {
    gapAnalysisStore.fetchOne(Number(route.params.id));
    // Preload posting titles for the cluster detail chips.
    if (!postingStore.hasPostings) postingStore.fetchAll();
});

function goBack() {
    if (window.history.length > 1) {
        router.back();
    } else {
        router.push({ name: 'gap-analysis' });
    }
}
</script>

<template>
    <div>
        <!-- Back nav -->
        <v-btn
            variant="text"
            prepend-icon="mdi-arrow-left"
            class="mb-4 ms-n2"
            @click="goBack"
        >
            Back
        </v-btn>

        <!-- Loading -->
        <div v-if="gapAnalysisStore.loadingDetail && !analysis" class="text-center py-12">
            <v-progress-circular indeterminate color="primary" />
        </div>

        <!-- Error -->
        <v-alert
            v-else-if="gapAnalysisStore.error && !analysis"
            type="error"
            variant="tonal"
        >
            {{ gapAnalysisStore.error }}
        </v-alert>

        <!-- Loaded -->
        <div v-else-if="analysis">
            <!-- Header -->
            <div class="mb-6">
                <div class="text-caption text-medium-emphasis text-uppercase mb-1">
                    Gap Analysis
                </div>
                <h1 class="text-h4 font-weight-bold mb-1">
                    Across {{ totalPostings }} posting{{ totalPostings === 1 ? '' : 's' }}
                </h1>
                <p class="text-body-2 text-medium-emphasis mb-0">
                    Computed {{ computedDateFull }}
                </p>
            </div>

            <!-- Low-postings warning -->
            <v-alert
                v-if="lowPostingsWarning"
                type="info"
                variant="tonal"
                density="compact"
                class="mb-6"
            >
                This analysis was run against {{ totalPostings }} posting{{ totalPostings === 1 ? '' : 's' }}.
                Cross-posting frequency ranking becomes most meaningful with
                {{ RECOMMENDED_MIN_POSTINGS }}+ postings.
            </v-alert>

            <!-- Stat cards -->
            <v-row class="mb-6">
                <v-col cols="12" md="4">
                    <GapStatCard
                        label="Postings analyzed"
                        :value="totalPostings"
                        icon="mdi-briefcase-outline"
                        color="primary"
                        caption="Included in this analysis snapshot"
                    />
                </v-col>
                <v-col cols="12" md="4">
                    <GapStatCard
                        label="Gaps identified"
                        :value="gapCount"
                        icon="mdi-alert-circle-outline"
                        color="error"
                        caption="After clustering similar requirements"
                    />
                </v-col>
                <v-col cols="12" md="4">
                    <GapStatCard
                        label="Top gap"
                        :value="topGap ? topGap.canonical_text.split(' ').slice(0, 4).join(' ') + (topGap.canonical_text.split(' ').length > 4 ? '…' : '') : '—'"
                        icon="mdi-target"
                        color="warning"
                        :caption="topGap ? `Affects ${Math.round(topGap.frequency * totalPostings)} of ${totalPostings} postings` : ''"
                    />
                </v-col>
            </v-row>

            <!-- Ranked gaps list -->
            <div class="mb-3">
                <div class="d-flex align-center justify-space-between">
                    <div>
                        <div class="text-h6 font-weight-medium">
                            Ranked gaps
                        </div>
                        <div class="text-body-2 text-medium-emphasis">
                            Ordered by (frequency across postings) &times; (match deficiency).
                            Higher impact = biggest opportunity if addressed.
                        </div>
                    </div>
                </div>
            </div>

            <div v-if="gapCount === 0" class="text-center py-8">
                <v-icon size="48" color="success" class="mb-3">mdi-check-decagram</v-icon>
                <div class="text-h6 font-weight-medium">No significant gaps</div>
                <div class="text-body-2 text-medium-emphasis">
                    Your resume matches these postings' requirements well.
                </div>
            </div>

            <div v-else>
                <RankedGapCard
                    v-for="(gap, idx) in analysis.ranked_gaps"
                    :key="idx"
                    :gap="gap"
                    :rank="idx + 1"
                    :total-postings="totalPostings"
                    :posting-lookup="postingLookup"
                />
            </div>
        </div>
    </div>
</template>
