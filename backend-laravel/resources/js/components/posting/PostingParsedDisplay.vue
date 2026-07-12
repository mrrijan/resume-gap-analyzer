<script setup>
import { computed } from 'vue';
import { PARSE_STRATEGY_META } from '@/constants/posting';

const props = defineProps({
    posting: {
        type: Object,
        required: true,
    },
});

const parsed = computed(() => props.posting?.parsed || null);

const strategyMeta = computed(() => {
    const strategy = parsed.value?.parse_strategy;
    return PARSE_STRATEGY_META[strategy] || null;
});

const sections = computed(() => {
    if (!parsed.value) return [];
    return [
        {
            key: 'required',
            label: 'Required',
            icon: 'mdi-check-circle-outline',
            color: 'error',
            items: parsed.value.required || [],
        },
        {
            key: 'preferred',
            label: 'Preferred',
            icon: 'mdi-star-outline',
            color: 'warning',
            items: parsed.value.preferred || [],
        },
        {
            key: 'responsibilities',
            label: 'Responsibilities',
            icon: 'mdi-briefcase-outline',
            color: 'primary',
            items: parsed.value.responsibilities || [],
        },
    ];
});
</script>

<template>
    <div v-if="parsed">
        <!-- Strategy badge -->
        <div v-if="strategyMeta" class="mb-4">
            <v-chip :color="strategyMeta.color" variant="tonal" size="small">
                <v-icon start size="16">{{ strategyMeta.icon }}</v-icon>
                Parsed via: {{ strategyMeta.label }}
            </v-chip>
            <div class="text-caption text-medium-emphasis mt-1">
                {{ strategyMeta.description }}
            </div>
        </div>

        <v-row>
            <v-col
                v-for="section in sections"
                :key="section.key"
                cols="12"
                md="4"
            >
                <v-card class="h-100">
                    <v-card-item>
                        <template #prepend>
                            <v-icon :color="section.color">{{ section.icon }}</v-icon>
                        </template>
                        <v-card-title class="text-subtitle-1 font-weight-medium">
                            {{ section.label }}
                        </v-card-title>
                        <template #append>
                            <v-chip size="small" variant="tonal" :color="section.color">
                                {{ section.items.length }}
                            </v-chip>
                        </template>
                    </v-card-item>

                    <v-divider />

                    <v-card-text>
                        <div v-if="section.items.length === 0" class="text-body-2 text-medium-emphasis text-center py-3">
                            None detected
                        </div>
                        <ul v-else class="parsed-list">
                            <li
                                v-for="(item, idx) in section.items"
                                :key="idx"
                                class="text-body-2 mb-2"
                            >
                                {{ item }}
                            </li>
                        </ul>
                    </v-card-text>
                </v-card>
            </v-col>
        </v-row>
    </div>
</template>

<style scoped>
.parsed-list {
    padding-left: 1.25rem;
    margin: 0;
}
</style>
