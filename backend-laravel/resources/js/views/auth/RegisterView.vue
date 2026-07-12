<template>
    <v-card class="pa-2">
        <v-card-item>
            <v-card-title class="text-h5 font-weight-bold">
                Create your account
            </v-card-title>
            <v-card-subtitle class="mt-1">
                Start analyzing your resume against target roles
            </v-card-subtitle>
        </v-card-item>

        <v-card-text>
            <v-alert
                v-if="errorMessage"
                type="error"
                variant="tonal"
                density="compact"
                class="mb-4"
            >
                {{ errorMessage }}
            </v-alert>

            <v-form ref="formRef" @submit.prevent="handleSubmit">
                <v-text-field
                    v-model="form.name"
                    label="Name"
                    :error-messages="fieldError('name')"
                    required
                />
                <v-text-field
                    v-model="form.email"
                    label="Email"
                    type="email"
                    autocomplete="email"
                    :error-messages="fieldError('email')"
                    required
                />
                <v-text-field
                    v-model="form.password"
                    label="Password"
                    :type="showPassword ? 'text' : 'password'"
                    autocomplete="current-password"
                    :error-messages="fieldError('password')"
                    :append-inner-icon="showPassword ? 'mdi-eye-off' : 'mdi-eye'"
                    @click:append-inner="showPassword = !showPassword"
                    required
                />
                <v-text-field
                    v-model="form.password_confirmation"
                    label="Confirm password"
                    :type="showPasswordConfirm ? 'text' : 'password'"
                    autocomplete="new-password"
                    :append-inner-icon="showPasswordConfirm ? 'mdi-eye-off' : 'mdi-eye'"
                    @click:append-inner="showPasswordConfirm = !showPasswordConfirm"
                    required
                />

                <v-btn
                    type="submit"
                    color="primary"
                    size="large"
                    block
                    :loading="loading"
                    class="mt-2"
                >
                    Create account
                </v-btn>
            </v-form>
        </v-card-text>

        <v-divider />

        <v-card-actions class="justify-center py-4">
      <span class="text-body-2 text-medium-emphasis">
        Already have an account?
      </span>
            <v-btn
                variant="text"
                color="primary"
                :to="{ name: 'login' }"
                density="compact"
            >
                Sign in
            </v-btn>
        </v-card-actions>
    </v-card>
</template>

<script setup>
import { reactive, ref } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';

const authStore = useAuthStore();
const router    = useRouter();

const form = reactive({
    name:                  '',
    email:                 '',
    password:              '',
    password_confirmation: '',
});

const loading      = ref(false);
const showPassword        = ref(false);
const showPasswordConfirm = ref(false);
const errorMessage = ref('');
const fieldErrors  = ref({});

function fieldError(field) {
    return fieldErrors.value[field]?.[0];
}

async function handleSubmit() {
    loading.value      = true;
    errorMessage.value = '';
    fieldErrors.value  = {};

    try {
        await authStore.register({ ...form });
        router.push({ name: 'dashboard' });
    } catch (err) {
        if (err.response?.status === 422) {
            fieldErrors.value  = err.response.data.errors || {};
            errorMessage.value = 'Please correct the errors below.';
        } else {
            errorMessage.value = err.response?.data?.message
                || 'Registration failed. Please try again.';
        }
    } finally {
        loading.value = false;
    }
}
</script>
