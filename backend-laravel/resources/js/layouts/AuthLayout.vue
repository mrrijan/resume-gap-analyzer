<template>
    <v-main class="auth-layout">
        <v-container class="fill-height" fluid>
            <v-row align="center" justify="center">
                <v-col cols="12" sm="8" md="5" lg="4">
                    <slot />
                </v-col>
            </v-row>
        </v-container>
    </v-main>
</template>

<script setup>
// Centered layout for login/register screens.
// A single-column card in the middle of the viewport.
</script>

<style scoped>
.auth-layout {
    min-height: 100vh;
}
</style>
