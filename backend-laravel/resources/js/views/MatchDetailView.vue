<script setup>
import { computed, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useMatchStore } from '@/stores/match';
import { STRENGTH_META } from '@/constants/match';

import FitScoreDisplay from '@/components/match/FitScoreDisplay.vue';
import RequirementColumn from '@/components/match/RequirementColumn.vue';

const route = useRoute();
const router = useRouter();
const matchStore = useMatchStore();

const match = computed(() => matchStore.currentMatch);

// Group requirements by strength for the three columns.
const grouped = computed(() => {
    const buckets = { strong: [], partial: [], missing: [] };
    if (!match.value?.gap_classification) return buckets;
    for (const req of match.value.gap_classification) {
        if (buckets[req.strength]) buckets[req.strength].push(req);
    }
    // Sort each bucket by similarity descending — best-in-class first.
    for (const key of Object.keys(buckets)) {
        buckets[key].sort((a, b) => b.similarity - a.similarity);
    }
    return buckets;
});

const strengthsOrder = ['strong', 'partial', 'missing'];

const computedDate = computed(() => {
    if (!match.value?.computed_at) return '';
    return new Date(match.value.computed_at).toLocaleString();
});

onMounted(() => {
    matchStore.fetchOne(Number(route.params.id));
});

function goBack() {
    if (window.history.length > 1) {
        router.back();
    } else {
        router.push({ name: 'matches' });
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
        <div v-if="matchStore.loadingDetail && !match" class="text-center py-12">
            <v-progress-circular indeterminate color="primary" />
        </div>

        <!-- Not found / error -->
        <v-alert
            v-else-if="matchStore.error && !match"
            type="error"
            variant="tonal"
        >
            {{ matchStore.error }}
        </v-alert>

        <!-- Loaded -->
        <div v-else-if="match">
            <!-- Header card: fit score + posting summary -->
            <v-card class="mb-6">
                <v-card-text class="pa-6">
                    <v-row align="center">
                        <v-col cols="12" md="4" class="text-center">
                            <FitScoreDisplay :overall-fit="Number(match.overall_fit)" />
                        </v-col>
                        <v-col cols="12" md="8">
                            <div class="text-caption text-medium-emphasis text-uppercase mb-1">
                                Match detail
                            </div>
                            <div class="text-h5 font-weight-bold mb-1">
                                {{ match.posting?.title || 'Untitled posting' }}
                            </div>
                            <div class="text-body-2 text-medium-emphasis mb-4">
                                Computed {{ computedDate }}
                            </div>

                            <div class="d-flex ga-3 flex-wrap">
                                <div>
                                    <div class="text-caption text-medium-emphasis">Required avg</div>
                                    <div class="text-body-1 font-weight-medium">
                                        {{ Math.round(match.avg_required * 100) }}%
                                    </div>
                                </div>
                                <v-divider vertical />
                                <div>
                                    <div class="text-caption text-medium-emphasis">Preferred avg</div>
                                    <div class="text-body-1 font-weight-medium">
                                        {{ match.avg_preferred != null ? `${Math.round(match.avg_preferred * 100)}%` : '—' }}
                                    </div>
                                </div>
                                <v-divider vertical />
                                <div>
                                    <div class="text-caption text-medium-emphasis">Weighting</div>
                                    <div class="text-body-1 font-weight-medium">
                                        Req {{ match.required_weight }} : Pref {{ match.preferred_weight }}
                                    </div>
                                </div>
                            </div>
                        </v-col>
                    </v-row>
                </v-card-text>
            </v-card>

            <!-- Three columns: Strong / Partial / Missing -->
            <div class="text-h6 font-weight-medium mb-3">Requirement breakdown</div>
            <p class="text-body-2 text-medium-emphasis mb-4">
                Each posting requirement classified against your resume content by semantic similarity.
            </p>

            <v-row>
                <v-col
                    v-for="strength in strengthsOrder"
                    :key="strength"
                    cols="12"
                    md="4"
                >
                    <RequirementColumn
                        :strength="strength"
                        :items="grouped[strength]"
                    />
                </v-col>
            </v-row>
        </div>
    </div>
</template>
