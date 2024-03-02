<template>
  <ModalErrorMessage ref="errorModal" />
  <div class="container">
    <h1 class="display-2 text-center mb-4">{{ $t("my.my-polls") }}</h1>
    <div class="card mb-4">
      <label class="card-header">{{ $t("my.polls-created-by-me") }}</label>
      <div class="card-body">
        <div v-if="createdByMe.length == 0 && !loading" class="text-muted">{{ $t("my.no-created-polls") }}</div>
        <ul class="mb-0">
          <li v-if="loading" class="text-muted">{{ $t("my.loading") }}</li>
          <li v-for="x in createdByMe" :key="x.id">
            <div><router-link class="remove-last-margin" :to="`/poll/${x.id}`" v-html="markdown(x.name)" /></div>
          </li>
        </ul>
      </div>
    </div>
    <div class="card">
      <label class="card-header">{{ $t("my.polls-voted-in") }}</label>
      <div class="card-body">
        <div v-if="votedIn.length == 0 && !loading" class="text-muted">{{ $t("my.no-polls-voted") }}</div>
        <ul class="mb-0">
          <li v-if="loading" class="text-muted">{{ $t("my.loading") }}</li>
          <li v-for="x in votedIn" :key="x.id">
            <div><router-link class="remove-last-margin" :to="`/poll/${x.id}`" v-html="markdown(x.name)" /></div>
          </li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { ref, onMounted } from "vue";
import { endpointUrl, markdown } from "@/util";
import ModalErrorMessage from "@/components/ModalErrorMessage.vue";

const errorModal = ref<typeof ModalErrorMessage | null>(null);

const loading = ref(true);
const createdByMe = ref<{ id: string; name: string }[]>([]);
const votedIn = ref<{ id: string; name: string }[]>([]);

onMounted(() => reload());

async function reload() {
  loading.value = true;
  createdByMe.value = [];
  votedIn.value = [];

  const response = await window.fetch(endpointUrl("api/my-polls"));

  if (!response.ok) {
    await errorModal.value?.showError(response);
    return;
  }

  const data = await response.json();
  createdByMe.value = data.created_by_me;
  votedIn.value = data.voted_in;
  loading.value = false;
}
</script>
