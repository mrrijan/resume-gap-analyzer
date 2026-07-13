<script setup>
import { computed, ref } from 'vue';
import { formatFrequency } from '@/constants/gapAnalysis';

const props = defineProps({
    gap:            { type: Object, required: true },
    rank:           { type: Number, required: true },
    totalPostings:  { type: Number, required: true },
    postingLookup:  { type: Object, default: () => ({}) },  // { id: title }
});

const expanded = ref(false);

const scorePercent = computed(() => Math.round(props.gap.gap_score * 100));
const similarityPercent = computed(() => Math.round(props.gap.avg_similarity * 100));
const frequencyLabel = computed(() =>
    formatFrequency(props.gap.frequency, props.totalPostings)
);
const clusteredCount = computed(() => props.gap.example_requirements?.length || 0);
const hasCluster = computed(() => clusteredCount.value > 1);

function postingTitleFor(id) {
    return props.postingLookup[id] || `Posting #${id}`;
}
</script>

<template>
    <v-card class="mb-3">
        <v-card-text class="pa-5">
            <div class="d-flex align-start ga-4">
                <!-- Rank badge -->
                <div class="rank-badge">
                    #{{ rank }}
                </div>

                <!-- Main content -->
                <div class="flex-grow-1 min-width-0">
                    <div class="text-subtitle-1 font-weight-medium mb-2">
                        {{ gap.canonical_text }}
                    </div>

                    <div class="d-flex flex-wrap ga-2 align-center mb-3">
                        <v-chip size="small" variant="tonal" color="primary">
                            <v-icon start size="14">mdi-briefcase-outline</v-icon>
                            {{ frequencyLabel }}
                        </v-chip>

                        <v-chip size="small" variant="tonal" color="error">
                            <v-icon start size="14">mdi-percent</v-icon>
                            {{ similarityPercent }}% match on your resume
                        </v-chip>

                        <v-chip
                            v-if="hasCluster"
                            size="small"
                            variant="tonal"
                            color="info"
                            @click="expanded = !expanded"
                            style="cursor: pointer;"
                        >
                            <v-icon start size="14">
                                {{ expanded ? 'mdi-chevron-up' : 'mdi-chevron-down' }}
                            </v-icon>
                            {{ clusteredCount }} similar requirements clustered
                        </v-chip>
                    </div>

                    <!-- Impact bar -->
                    <div class="d-flex align-center ga-3">
                        <div class="flex-grow-1">
                            <v-progress-linear
                                :model-value="scorePercent"
                                color="error"
                                bg-color="grey-lighten-3"
                                height="8"
                                rounded
                            />
                        </div>
                        <div class="text-body-2 font-weight-medium text-error" style="min-width: 60px; text-align: right;">
                            {{ scorePercent }}%
                        </div>
                    </div>
                    <div class="text-caption text-medium-emphasis mt-1">
                        Gap impact score
                    </div>

                    <!-- Expanded: clustered examples -->
                    <v-expand-transition>
                        <div v-if="expanded && hasCluster" class="cluster-expand mt-4 pt-4">
                            <div class="text-caption text-medium-emphasis mb-2">
                                This gap was identified across multiple postings from similar requirement text:
                            </div>
                            <ul class="cluster-list">
                                <li
                                    v-for="(req, idx) in gap.example_requirements"
                                    :key="idx"
                                    class="text-body-2 mb-2"
                                >
                                    {{ req }}
                                </li>
                            </ul>

                            <div class="text-caption text-medium-emphasis mt-3 mb-2">
                                Affected postings:
                            </div>
                            <div class="d-flex flex-wrap ga-1">
                                <v-chip
                                    v-for="pid in gap.affected_posting_ids"
                                    :key="pid"
                                    size="x-small"
                                    variant="outlined"
                                >
                                    {{ postingTitleFor(pid) }}
                                </v-chip>
                            </div>
                        </div>
                    </v-expand-transition>
                </div>
            </div>
        </v-card-text>
    </v-card>
</template>

<style scoped>
.rank-badge {
    flex-shrink: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    width: 44px;
    height: 44px;
    border-radius: 8px;
    background-color: rgba(var(--v-theme-primary), 0.08);
    color: rgb(var(--v-theme-primary));
    font-weight: 600;
    font-size: 14px;
}

.cluster-expand {
    border-top: 1px solid rgb(var(--v-theme-border));
}

.cluster-list {
    padding-left: 1.25rem;
    margin: 0;
}
</style>
