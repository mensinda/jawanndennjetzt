<template>
  <ModalErrorMessage ref="errorModal" />
  <ModalImportPoll ref="importModal" :onImportError="handleImportError" :onImportDone="editorComp?.optionsImported()" />
  <div class="container" v-if="!JWDJ_LOGIN_MANAGER || store.user?.authorised">
    <div class="new-poll-head-grid-helper">
      <h1 class="text-center">{{ $t("main.create-a-new-poll") }}</h1>
      <button class="btn btn-info" type="button" @click="importModal?.doShow()">{{ $t("new.import-existing") }}</button>
    </div>

    <!-- Main editor -->
    <EditorComp ref="editorComp" :submitMsg="$t('new.publish-poll')" :canEditOptions="true" @submit="createPoll" />
    <hr class="mt-4 mb-4" />
    <div class="card mb-5">
      <div class="card-header">{{ $t("new.preview") }}</div>
      <div class="card-body">
        <span v-if="store.options.length == 0" class="text-muted user-select-none">
          {{ $t("new.add-option-for-preview") }}
        </span>
        <div v-if="store.options.length > 0">
          <PollComp mode="preview" />
          <hr v-if="store.description.trim()" />
          <PollDescription v-if="store.description.trim()" />
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
import PollComp from "@/components/PollComp.vue"; // @ is an alias to /src
import EditorComp from "@/components/EditorComp.vue";
import ModalErrorMessage from "@/components/ModalErrorMessage.vue";
import ModalImportPoll from "@/components/ModalImportPoll.vue";
import axios from "@/axios";
import { ref, onMounted, onBeforeMount } from "vue";
import { pollStore } from "@/store";
import { endpointUrl } from "@/util";
import { useRouter } from "vue-router";
import { JWDJ_LOGIN_MANAGER } from "@/config";
import { load_user_info } from "@/auth";
import PollDescription from "@/components/PollDescription.vue";

const router = useRouter();
const store = pollStore();
const errorModal = ref<typeof ModalErrorMessage | null>(null);
const importModal = ref<typeof ModalImportPoll | null>(null);
const editorComp = ref<typeof EditorComp | null>(null);

const hasChanges = ref(false);
const pollInput = ref("");
const isChecking = ref(false);

onMounted(() => {
  store.reset();

  hasChanges.value = false;
  pollInput.value = "";
  isChecking.value = false;
});

if (JWDJ_LOGIN_MANAGER) {
  onBeforeMount(async () => {
    await load_user_info();
    if (!store.user?.authorised) {
      router.push({ name: "login" });
    }
  });
}

function createPoll() {
  axios({
    url: endpointUrl("api/new"),
    method: "post",
    data: {
      name: store.name,
      description: store.description,
      allow_not_voted: store.allowNotVoted,
      options: store.options.map((x) => {
        return {
          index: x.index,
          name: x.name,
        };
      }),
    },
  })
    .then((x) => {
      router.push({ name: "poll", params: { id: x.data.id } });
    })
    .catch((x) => {
      if (errorModal.value == null) {
        return;
      }
      errorModal.value.doShow();
      errorModal.value.data = x.response.data;
    });
}

function handleImportError() {
  if (errorModal.value == null) {
    return;
  }
  errorModal.value.doShow();
  errorModal.value.updateData(store.lastError);
}
</script>

<style lang="scss">
.selection-grid {
  display: grid;
  grid-template-columns: 2fr 1fr;
  grid-template-rows: auto;
  grid-template-areas:
    "txt1 btn1"
    "sep1 sep1"
    "txt2 txt2"
    "in1  btn2"
    "err  xxx";

  align-items: center;

  column-gap: 5px;
  row-gap: 5px;
}

.new-poll-head-grid-helper {
  display: grid;
  grid-template-columns: 3fr 2fr;
  @media screen and (max-width: 800px) {
    grid-template-columns: 1fr;
  }
}

.new-poll-head-grid-helper h1 {
  grid-row: 1 / span 1;
  grid-column: 1 / span 2;
}

.new-poll-head-grid-helper button {
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
