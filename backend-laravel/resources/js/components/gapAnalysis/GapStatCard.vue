<script setup>
defineProps({
    label:       { type: String, required: true },
    value:       { type: [String, Number], required: true },
    caption:     { type: String, default: '' },
    icon:        { type: String, default: null },
    color:       { type: String, default: 'primary' },
});
</script>

<template>
    <v-card class="h-100">
        <v-card-text class="pa-5">
            <div class="d-flex align-center ga-2 mb-2">
                <v-icon v-if="icon" :color="color" size="18">{{ icon }}</v-icon>
                <span class="text-caption text-medium-emphasis text-uppercase">
          {{ label }}
        </span>
            </div>

            <div class="text-h4 font-weight-bold" :class="`text-${color}`">
                {{ value }}
            </div>

            <div v-if="caption" class="text-caption text-medium-emphasis mt-2">
                {{ caption }}
            </div>
        </v-card-text>
    </v-card>
</template>
