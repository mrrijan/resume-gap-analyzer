<script setup>
import { computed, nextTick, onMounted, ref } from 'vue';
import { usePostingStore } from '@/stores/posting';

import PostingCreateDialog from '@/components/posting/PostingCreateDialog.vue';
import PostingParsedDisplay from '@/components/posting/PostingParsedDisplay.vue';

const postingStore = usePostingStore();

const createDialogOpen = ref(false);
const deleteDialog = ref(false);
const postingToDelete = ref(null);
const selectedPostingId = ref(null);

const displayedPosting = computed(() => {
    if (selectedPostingId.value) {
        return postingStore.postings.find(p => p.id === selectedPostingId.value)
            || postingStore.latestPosting;
    }
    return postingStore.latestPosting;
});

onMounted(() => {
    postingStore.fetchAll();
});

async function onCreated(posting) {
    selectedPostingId.value = posting.id;
    await nextTick();
    document.querySelector('[data-parsed-anchor]')?.scrollIntoView({
        behavior: 'smooth',
        block: 'start',
    });
}

function askDelete(posting) {
    postingToDelete.value = posting;
    deleteDialog.value = true;
}

async function confirmDelete() {
    if (!postingToDelete.value) return;
    const deletedId = postingToDelete.value.id;
    await postingStore.destroy(deletedId);
    if (selectedPostingId.value === deletedId) {
        selectedPostingId.value = null;
    }
    deleteDialog.value = false;
    postingToDelete.value = null;
}

function formatDate(iso) {
    if (!iso) return '';
    return new Date(iso).toLocaleDateString(undefined, {
        year: 'numeric', month: 'short', day: 'numeric',
    });
}

function isSelected(posting) {
    if (selectedPostingId.value) return selectedPostingId.value === posting.id;
    return posting.id === postingStore.latestPosting?.id;
}
</script>

<template>
    <div>
        <!-- Page header -->
        <div class="d-flex align-center justify-space-between mb-6">
            <div>
                <h1 class="text-h4 font-weight-bold mb-1">Postings</h1>
                <p class="text-body-1 text-medium-emphasis mb-0">
                    Track job postings and analyze how your resume matches each one.
                </p>
            </div>
            <v-btn
                color="primary"
                variant="flat"
                prepend-icon="mdi-plus"
                @click="createDialogOpen = true"
            >
                Add posting
            </v-btn>
        </div>

        <!-- Loading -->
        <div v-if="postingStore.loading && postingStore.postings.length === 0" class="text-center py-12">
            <v-progress-circular indeterminate color="primary" />
        </div>

        <!-- Empty state -->
        <v-card v-else-if="!postingStore.hasPostings" class="text-center pa-8">
            <v-icon size="48" color="primary" class="mb-4">mdi-briefcase-plus-outline</v-icon>
            <div class="text-h6 font-weight-medium mb-1">No postings yet</div>
            <div class="text-body-2 text-medium-emphasis mb-4">
                Paste a job description to see how your resume matches up.
            </div>
            <v-btn color="primary" variant="flat" @click="createDialogOpen = true">
                Add your first posting
            </v-btn>
        </v-card>

        <!-- Populated -->
        <div v-else>
            <!-- List -->
            <div class="mb-6">
                <div class="text-subtitle-2 text-medium-emphasis mb-3">
                    Your postings ({{ postingStore.postings.length }})
                </div>

                <v-row>
                    <v-col
                        v-for="posting in postingStore.postings"
                        :key="posting.id"
                        cols="12"
                        md="6"
                        lg="4"
                    >
                        <v-card
                            :variant="isSelected(posting) ? 'tonal' : 'elevated'"
                            :color="isSelected(posting) ? 'primary' : undefined"
                            class="cursor-pointer h-100"
                            @click="selectedPostingId = posting.id"
                        >
                            <v-card-item>
                                <template #prepend>
                                    <v-icon color="primary" size="28">mdi-briefcase-outline</v-icon>
                                </template>
                                <v-card-title class="text-subtitle-1 font-weight-medium text-truncate">
                                    {{ posting.title || 'Untitled posting' }}
                                </v-card-title>
                                <v-card-subtitle>
                                    Added {{ formatDate(posting.created_at) }}
                                </v-card-subtitle>
                                <template #append>
                                    <v-btn
                                        icon="mdi-delete-outline"
                                        variant="text"
                                        size="small"
                                        color="error"
                                        @click.stop="askDelete(posting)"
                                    />
                                </template>
                            </v-card-item>
                        </v-card>
                    </v-col>
                </v-row>
            </div>

            <!-- Parsed sections of selected -->
            <div>
                <div class="text-subtitle-2 text-medium-emphasis mb-3" data-parsed-anchor>
                    {{ displayedPosting?.title || 'Latest posting' }} &middot; parsed sections
                </div>
                <PostingParsedDisplay :posting="displayedPosting" />
            </div>
        </div>

        <!-- Dialogs -->
        <PostingCreateDialog
            v-model="createDialogOpen"
            @created="onCreated"
        />

        <v-dialog v-model="deleteDialog" max-width="440">
            <v-card>
                <v-card-title>Delete this posting?</v-card-title>
                <v-card-text>
                    <p class="mb-2">
                        <strong>{{ postingToDelete?.title || 'Untitled posting' }}</strong>
                    </p>
                    <p class="text-body-2 text-medium-emphasis mb-0">
                        This will also remove any matches computed against this posting. This action cannot be undone.
                    </p>
                </v-card-text>
                <v-card-actions>
                    <v-spacer />
                    <v-btn variant="text" @click="deleteDialog = false">Cancel</v-btn>
                    <v-btn color="error" variant="flat" @click="confirmDelete">Delete</v-btn>
                </v-card-actions>
            </v-card>
        </v-dialog>
    </div>
</template>

<style scoped>
.cursor-pointer {
    cursor: pointer;
}
</style>
