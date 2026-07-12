<script setup>
import { computed } from 'vue';
import { fitTier } from '@/constants/match';

const props = defineProps({
    overallFit: { type: Number, required: true },
    size:       { type: Number, default: 140 },
});

const tier = computed(() => fitTier(props.overallFit));

const rounded = computed(() => Math.round(props.overallFit));
</script>

<template>
    <div class="d-flex flex-column align-center">
        <v-progress-circular
            :model-value="rounded"
            :size="size"
            :width="10"
            :color="tier.color"
            bg-color="grey-lighten-3"
        >
            <div class="text-center">
                <div class="text-h4 font-weight-bold">{{ rounded }}<span class="text-h6">%</span></div>
            </div>
        </v-progress-circular>
        <div class="text-caption text-medium-emphasis mt-2">Overall fit</div>
        <v-chip
            :color="tier.color"
            variant="tonal"
            size="small"
            class="mt-1"
        >
            <v-icon start size="14">mdi-trending-up</v-icon>
            {{ tier.label }}
        </v-chip>
    </div>
</template>
