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
    <EditorComp :submitMsg="$t('edit.do-update')" ref="editComp" :canEditOptions="false" @submit="updatePoll" />
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
import axios, { AxiosError } from "@/axios";
import { ref, onMounted, onBeforeUnmount } from "vue";
import { pollStore } from "@/store";
import { endpointUrl, setStoreFromResponse, PollData } from "@/util";
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
  try {
    const res = await axios<PollData>({
      url: endpointUrl("api/poll/" + route.params.id),
      method: "get",
    });

    setStoreFromResponse(res.data);
    pollstatus.value = "ready";
  } catch (x) {
    if (!(x instanceof AxiosError)) {
      return;
    }
    if (x.response?.data.code == "POLL_NOT_FOUND") {
      pollstatus.value = "404";
      return;
    }
    if (errorModal.value == null) {
      return;
    }
    errorModal.value.doShow();
    errorModal.value.data = x.response?.data;
  }
}

async function deletePoll() {
  try {
    await axios({
      url: endpointUrl("api/poll/" + route.params.id + "/delete"),
      method: "post",
      data: {},
    });

    router.replace("/");
  } catch (x) {
    if (errorModal.value == null || !(x instanceof AxiosError)) {
      return;
    }
    errorModal.value.doShow();
    errorModal.value.data = x.response?.data;
  }
}

async function updatePoll() {
  pollstatus.value = "updating";

  try {
    await axios({
      url: endpointUrl("api/poll/" + route.params.id + "/update"),
      method: "post",
      data: {
        name: store.name,
        description: store.description,
        allow_not_voted: store.allowNotVoted,
      },
    });

    await reload();
    if (editComp.value) {
      editComp.value.hasChanges = false;
    }
  } catch (x) {
    if (errorModal.value == null || !(x instanceof AxiosError)) {
      return;
    }
    errorModal.value.doShow();
    errorModal.value.data = x.response?.data;
    await reload();
  }
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
