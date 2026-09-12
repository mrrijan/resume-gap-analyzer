<script setup>
import { computed, reactive, ref, watch } from 'vue';
import { useAuthStore } from '@/stores/auth';

const props = defineProps({
    modelValue: { type: Boolean, required: true },
});
const emit = defineEmits(['update:modelValue']);

const authStore = useAuthStore();

const isOpen = computed({
    get: () => props.modelValue,
    set: (v) => emit('update:modelValue', v),
});

const form = reactive({
    current_password: '',
    password: '',
    password_confirmation: '',
});

const showCurrent = ref(false);
const showNew = ref(false);
const showConfirm = ref(false);
const successMessage = ref('');
const fieldErrors = ref({});

function fieldError(field) {
    return fieldErrors.value[field]?.[0];
}

watch(isOpen, (open) => {
    if (open) {
        form.current_password = '';
        form.password = '';
        form.password_confirmation = '';
        successMessage.value = '';
        fieldErrors.value = {};
        authStore.error = null;
    }
});

async function handleSubmit() {
    successMessage.value = '';
    fieldErrors.value = {};

    try {
        const data = await authStore.changePassword({ ...form });
        successMessage.value = data.message || 'Password updated successfully.';
        form.current_password = '';
        form.password = '';
        form.password_confirmation = '';
    } catch (err) {
        if (err.response?.status === 422) {
            fieldErrors.value = err.response.data.errors || {};
        }
    }
}
</script>

<template>
    <v-dialog v-model="isOpen" max-width="480">
        <v-card>
            <v-card-item>
                <v-card-title>Change password</v-card-title>
            </v-card-item>

            <v-card-text>
                <v-alert
                    v-if="successMessage"
                    type="success"
                    variant="tonal"
                    density="compact"
                    class="mb-4"
                >
                    {{ successMessage }}
                </v-alert>

                <v-alert
                    v-if="authStore.error && !successMessage"
                    type="error"
                    variant="tonal"
                    density="compact"
                    class="mb-4"
                >
                    {{ authStore.error }}
                </v-alert>

                <v-form @submit.prevent="handleSubmit">
                    <v-text-field
                        v-model="form.current_password"
                        label="Current password"
                        :type="showCurrent ? 'text' : 'password'"
                        :append-inner-icon="showCurrent ? 'mdi-eye-off' : 'mdi-eye'"
                        @click:append-inner="showCurrent = !showCurrent"
                        :error-messages="fieldError('current_password')"
                        autocomplete="current-password"
                    />
                    <v-text-field
                        v-model="form.password"
                        label="New password"
                        :type="showNew ? 'text' : 'password'"
                        :append-inner-icon="showNew ? 'mdi-eye-off' : 'mdi-eye'"
                        @click:append-inner="showNew = !showNew"
                        :error-messages="fieldError('password')"
                        autocomplete="new-password"
                    />
                    <v-text-field
                        v-model="form.password_confirmation"
                        label="Confirm new password"
                        :type="showConfirm ? 'text' : 'password'"
                        :append-inner-icon="showConfirm ? 'mdi-eye-off' : 'mdi-eye'"
                        @click:append-inner="showConfirm = !showConfirm"
                        autocomplete="new-password"
                    />

                    <v-btn
                        type="submit"
                        color="primary"
                        block
                        :loading="authStore.changingPassword"
                        class="mt-2"
                    >
                        Update password
                    </v-btn>
                </v-form>
            </v-card-text>

            <v-divider />

            <v-card-actions class="pa-4">
                <v-spacer />
                <v-btn variant="text" @click="isOpen = false">Close</v-btn>
            </v-card-actions>
        </v-card>
    </v-dialog>
</template>
