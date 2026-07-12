<script setup>
import { computed } from 'vue';

const props = defineProps({
    resume: {
        type: Object,
        required: true,
    },
});

const parsed = computed(() => props.resume?.latest_version?.parsed || null);

const sections = computed(() => {
    if (!parsed.value) return [];
    return [
        { key: 'skills', label: 'Skills', icon: 'mdi-star-outline', items: parsed.value.skills || [] },
        { key: 'experience', label: 'Experience', icon: 'mdi-briefcase-outline', items: parsed.value.experience || [] },
        { key: 'education', label: 'Education', icon: 'mdi-school-outline', items: parsed.value.education || [] },
        { key: 'certifications', label: 'Certifications', icon: 'mdi-certificate-outline', items: parsed.value.certifications || [] },
    ];
});
</script>

<template>
    <div v-if="parsed">
        <v-row>
            <v-col
                v-for="section in sections"
                :key="section.key"
                cols="12"
                md="6"
            >
                <v-card class="h-100">
                    <v-card-item>
                        <template #prepend>
                            <v-icon color="primary">{{ section.icon }}</v-icon>
                        </template>
                        <v-card-title class="text-subtitle-1 font-weight-medium">
                            {{ section.label }}
                        </v-card-title>
                        <template #append>
                            <v-chip size="small" variant="tonal" color="primary">
                                {{ section.items.length }}
                            </v-chip>
                        </template>
                    </v-card-item>

                    <v-divider />

                    <v-card-text>
                        <div v-if="section.items.length === 0" class="text-body-2 text-medium-emphasis text-center py-3">
                            None detected
                        </div>

                        <!-- Skills: chip layout -->
                        <div v-else-if="section.key === 'skills'" class="d-flex flex-wrap ga-2">
                            <v-chip
                                v-for="(item, idx) in section.items"
                                :key="idx"
                                size="small"
                                variant="tonal"
                            >
                                {{ item }}
                            </v-chip>
                        </div>

                        <!-- Other sections: bulleted list -->
                        <ul v-else class="parsed-list">
                            <li
                                v-for="(item, idx) in section.items"
                                :key="idx"
                                class="text-body-2 mb-1"
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
.ga-2 > * {
    margin: 0;
}
</style>
