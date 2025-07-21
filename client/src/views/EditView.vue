<template>
  <ModalErrorMessage ref="errorModal" />
  <ModalConfirm ref="confirmModal" @confirmedDeletion="deletePoll()" />
  <div v-if="pollstatus == 'loading'">
    <div class="root-display-container text-center">
      <h1 class="display-1 text-muted">{{ $t("main.title") }}</h1>
      <h3 class="mb-5 text-muted">{{ $t("main.subtitle") }}</h3>
      <h1 class="mb-5">{{ $t("main.loading-poll") }}</h1>
      <small class="text-muted">{ ID = {{ $route.params.id }} }</small>
    </div>
  </div>
  <NotFoundComp v-if="pollstatus == '404'" :desc="$t('404.poll-not-found')" :info="`{ ID = ${$route.params.id} }`" />
  <div v-if="pollstatus == 'ready'" class="container">
    <div class="edit-head-grid-helper">
      <h1 class="text-center">{{ $t("edit.edit-poll") }}</h1>
      <button
        class="btn btn-info"
        type="button"
        @click="$router.push({ name: 'poll', params: { id: $route.params.id } })"
      >
        <h4 style="margin: 0">{{ $t("edit.return-to-poll") }}</h4>
      </button>
    </div>
    <EditorComp :submitMsg="$t('edit.do-update')" ref="editComp" :isNewPoll="false" @submit="updatePoll" />
    <div class="d-flex flex-row">
      <button @click="confirmModal?.doShow()" class="btn btn-lg btn-danger col" type="button">
        {{ $t("edit.delete-poll") }}
      </button>
    </div>
    <hr class="mt-4 mb-4" />
    <div class="card">
      <div class="card-header">{{ $t("edit.preview") }}</div>
      <div class="card-body">
        <PollComp mode="preview" />
        <hr v-if="store.description.trim()" />
        <PollDescription v-if="store.description.trim()" />
      </div>
    </div>
  </div>
  <div class="mb-5" />
</template>

<script lang="ts" setup>
import PollComp from "@/components/PollComp.vue"; // @ is an alias to /src
import EditorComp from "@/components/EditorComp.vue";
import ModalErrorMessage from "@/components/ModalErrorMessage.vue";
import ModalConfirm from "@/components/ModalConfirm.vue";
import NotFoundComp from "@/components/NotFoundComp.vue";
import { ref, onMounted, onBeforeUnmount } from "vue";
import { pollStore } from "@/store";
import { endpointUrl, setStoreFromResponse, fetchHeaders } from "@/util";
import { useRoute } from "vue-router";
import PollDescription from "@/components/PollDescription.vue";
import router from "@/router";

const store = pollStore();
const route = useRoute();
const errorModal = ref<typeof ModalErrorMessage | null>(null);
const confirmModal = ref<typeof ModalConfirm | null>(null);
const editComp = ref<typeof EditorComp | null>(null);

const pollstatus = ref("loading");

onMounted(() => {
  pollstatus.value = "loading";
  reload();
});

onBeforeUnmount(() => {
  store.footerInfo = "";
});

async function reload() {
  if (editComp.value) {
    editComp.value.hasChanges = false;
  }

  const response = await window.fetch(endpointUrl("api/poll/" + route.params.id));

  if (!response.ok) {
    try {
      const data = await response.json();
      if (data.code == "POLL_NOT_FOUND") {
        pollstatus.value = "404";
        return;
      }
    } catch {
      // Do nothing I guess...
    }
    await errorModal.value?.showError(response);
    return;
  }

  setStoreFromResponse(await response.json());
  pollstatus.value = "ready";
}

async function deletePoll() {
  const response = await window.fetch(endpointUrl("api/poll/" + route.params.id + "/delete"), {
    method: "post",
    headers: fetchHeaders(),
  });

  if (!response.ok) {
    await errorModal.value?.showError(response);
    return;
  }

  router.replace("/");
}

async function updatePoll() {
  pollstatus.value = "updating";

  const response = await window.fetch(endpointUrl("api/poll/" + route.params.id + "/update"), {
    method: "post",
    headers: fetchHeaders(),
    body: JSON.stringify({
      name: store.name,
      description: store.description,
      allow_not_voted: store.allowNotVoted,
      options: store.options.map((x) => {
        return {
          old_index: x.orig_index,
          index: x.index,
          name: x.name,
        };
      }),
    }),
  });

  if (response.ok) {
    if (editComp.value) {
      editComp.value.hasChanges = false;
    }
  } else {
    await errorModal.value?.showError(response);
  }

  await reload();
}
</script>

<style lang="scss">
.edit-head-grid-helper {
  display: grid;
  grid-template-columns: 3fr 2fr;
  @media screen and (max-width: 800px) {
    grid-template-columns: 1fr;
  }
}

.edit-head-grid-helper h1 {
  grid-row: 1 / span 1;
  grid-column: 1 / span 2;
}

.edit-head-grid-helper button {
  @media screen and (min-width: 800px) {
    grid-row: 1 / span 1;
    grid-column: 2 / span 1;
    align-self: center;
    justify-self: end;
  }
  @media screen and (max-width: 800px) {
    margin-bottom: 1rem;
  }
}
</style>
