<script setup>
import { computed } from 'vue';
import { STRENGTH_META } from '@/constants/match';

const props = defineProps({
    strength: { type: String, required: true }, // 'strong' | 'partial' | 'missing'
    items:    { type: Array,  required: true },
});

const meta = computed(() => STRENGTH_META[props.strength]);
</script>

<template>
    <v-card class="h-100">
        <v-card-item>
            <template #prepend>
                <v-icon :color="meta.color" size="24">{{ meta.icon }}</v-icon>
            </template>
            <v-card-title class="text-subtitle-1 font-weight-medium">
                {{ meta.label }}
            </v-card-title>
            <template #append>
                <v-chip size="small" variant="tonal" :color="meta.color">
                    {{ items.length }}
                </v-chip>
            </template>
        </v-card-item>

        <v-divider />

        <v-card-text>
            <div
                v-if="items.length === 0"
                class="text-body-2 text-medium-emphasis text-center py-3"
            >
                None
            </div>
            <div v-else class="d-flex flex-column ga-3">
                <div
                    v-for="(item, idx) in items"
                    :key="idx"
                    class="requirement-item"
                >
                    <div class="d-flex align-start justify-space-between ga-2 mb-1">
                        <span class="text-body-2 flex-grow-1">{{ item.text }}</span>
                        <v-chip size="x-small" variant="tonal" :color="meta.color">
                            {{ Math.round(item.similarity * 100) }}%
                        </v-chip>
                    </div>
                    <div class="text-caption text-medium-emphasis">
                        <v-icon size="12">mdi-source-branch</v-icon>
                        matched against your {{ item.best_matched_section }}
                        &middot; {{ item.bucket === 'required' ? 'Required' : 'Preferred' }}
                    </div>
                </div>
            </div>
        </v-card-text>
    </v-card>
</template>

<style scoped>
.requirement-item {
    padding: 0.5rem 0;
    border-bottom: 1px solid rgb(var(--v-theme-border));
}
.requirement-item:last-child {
    border-bottom: none;
    padding-bottom: 0;
}
</style>
