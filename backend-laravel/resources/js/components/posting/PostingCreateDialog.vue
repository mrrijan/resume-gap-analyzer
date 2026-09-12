<script setup>
import { computed, ref, watch } from 'vue';
import { usePostingStore } from '@/stores/posting';
import { POSTING_TEXT } from '@/constants/posting';

const props = defineProps({
    modelValue: { type: Boolean, required: true },
});
const emit = defineEmits(['update:modelValue', 'created']);

const postingStore = usePostingStore();

const form = ref({
    title: '',
    text: '',
    source_url: '',
});
const submitAttempted = ref(false);

const isOpen = computed({
    get: () => props.modelValue,
    set: (v) => emit('update:modelValue', v),
});

const textCharCount = computed(() => form.value.text.length);

const textTooShort = computed(() => textCharCount.value > 0 && textCharCount.value < POSTING_TEXT.minLength);
const textTooLong = computed(() => textCharCount.value > POSTING_TEXT.maxLength);
const canSubmit = computed(() =>
    textCharCount.value >= POSTING_TEXT.minLength &&
    textCharCount.value <= POSTING_TEXT.maxLength &&
    !postingStore.creating,
);

// Reset the form whenever the dialog opens fresh.
watch(isOpen, (open) => {
    if (open) {
        form.value = { title: '', text: '', source_url: '' };
        submitAttempted.value = false;
        postingStore.error = null;
    }
});

async function submit() {
    submitAttempted.value = true;
    if (!canSubmit.value) return;

    try {
        const posting = await postingStore.create({
            title: form.value.title || null,
            text: form.value.text,
            source_url: form.value.source_url || null,
        });
        emit('created', posting);
        isOpen.value = false;
    } catch {
        // Store already recorded error; alert renders it below.
    }
}
</script>

<template>
    <v-dialog v-model="isOpen" max-width="720" persistent>
        <v-card>
            <v-card-item>
                <v-card-title>Add a job posting</v-card-title>
                <v-card-subtitle class="mt-1">
                    Paste the full job description text. The parser will extract required and preferred qualifications.
                </v-card-subtitle>
            </v-card-item>

            <v-card-text>
                <v-alert
                    v-if="postingStore.error"
                    type="error"
                    variant="tonal"
                    density="compact"
                    class="mb-4"
                >
                    {{ postingStore.error }}
                </v-alert>

                <v-text-field
                    v-model="form.title"
                    label="Title (optional)"
                    placeholder="e.g. Senior Backend Engineer at Stripe"
                    hint="Leave blank to auto-derive from the posting text."
                />

                <v-textarea
                    v-model="form.text"
                    label="Job description"
                    placeholder="Paste the full posting here..."
                    rows="12"
                    auto-grow
                    :error-messages="submitAttempted && textTooShort
            ? [`Please paste at least ${POSTING_TEXT.minLength} characters.`]
            : submitAttempted && textTooLong
              ? [`Please shorten to under ${POSTING_TEXT.maxLength} characters.`]
              : []"
                />

                <div class="d-flex align-center justify-space-between mt-1 mb-3">
          <span class="text-caption text-medium-emphasis">
            {{ textCharCount.toLocaleString() }} / {{ POSTING_TEXT.maxLength.toLocaleString() }} characters
          </span>
                    <span
                        v-if="textTooShort"
                        class="text-caption"
                        :class="submitAttempted ? 'text-error' : 'text-medium-emphasis'"
                    >
            Minimum {{ POSTING_TEXT.minLength }}
          </span>
                </div>

<!--                <v-text-field-->
<!--                    v-model="form.source_url"-->
<!--                    label="Source URL (optional)"-->
<!--                    placeholder="https://..."-->
<!--                />-->
            </v-card-text>

            <v-divider />

            <v-card-actions class="pa-4">
                <v-spacer />
                <v-btn variant="text" @click="isOpen = false" :disabled="postingStore.creating">
                    Cancel
                </v-btn>
                <v-btn
                    color="primary"
                    variant="flat"
                    :loading="postingStore.creating"
                    :disabled="!canSubmit && submitAttempted"
                    @click="submit"
                >
                    Add posting
                </v-btn>
            </v-card-actions>
        </v-card>
    </v-dialog>
</template>
