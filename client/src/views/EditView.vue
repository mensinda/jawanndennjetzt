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
  <NotFoundComp
    v-if="pollstatus == '404'"
    desc="The requested poll was not found"
    :info="`{ ID = ${$route.params.id} }`"
  />
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
    <EditorComp submitMsg="↻ Update Poll ↻" ref="editComp" :canEditOptions="false" @submit="updatePoll" />
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

<script lang="ts">
import PollComp from "@/components/PollComp.vue"; // @ is an alias to /src
import EditorComp from "@/components/EditorComp.vue";
import ModalErrorMessage from "@/components/ModalErrorMessage.vue";
import ModalConfirm from "@/components/ModalConfirm.vue";
import NotFoundComp from "@/components/NotFoundComp.vue";
import axios from "@/axios";
import { defineComponent, ref } from "vue";
import { pollStore } from "@/store";
import { endpointUrl, setStoreFromResponse, PollData } from "@/util";
import PollDescription from "@/components/PollDescription.vue";
import router from "@/router";

export default defineComponent({
  components: {
    ModalErrorMessage,
    ModalConfirm,
    EditorComp,
    PollDescription,
    PollComp,
    NotFoundComp,
  },

  data() {
    return {
      pollstatus: "loading",
    };
  },

  setup() {
    const store = pollStore();
    const errorModal = ref<typeof ModalErrorMessage | null>(null);
    const confirmModal = ref<typeof ModalConfirm | null>(null);
    const editComp = ref<typeof EditorComp | null>(null);

    return { store, errorModal, confirmModal, editComp };
  },

  mounted() {
    this.pollstatus = "loading";
    this.reload();
  },

  beforeUnmount() {
    this.store.footerInfo = "";
  },

  methods: {
    reload() {
      if (this.editComp) {
        this.editComp.hasChanges = false;
      }
      axios<PollData>({
        url: endpointUrl("api/poll/" + this.$route.params.id),
        method: "get",
      })
        .then((x) => {
          setStoreFromResponse(x.data);
          this.pollstatus = "ready";
        })
        .catch((x) => {
          if (x.response.data.code == "POLL_NOT_FOUND") {
            this.pollstatus = "404";
            return;
          }
          if (this.errorModal == null) {
            return;
          }
          this.errorModal.doShow();
          this.errorModal.data = x.response.data;
        });
    },

    deletePoll() {
      axios({
        url: endpointUrl("api/poll/" + this.$route.params.id + "/delete"),
        method: "post",
        data: {},
      })
        .then((_) => {
          router.replace("/");
        })
        .catch((x) => {
          if (this.errorModal == null) {
            return;
          }
          this.errorModal.doShow();
          this.errorModal.data = x.response.data;
        });
    },

    updatePoll() {
      this.pollstatus = "updating";

      axios({
        url: endpointUrl("api/poll/" + this.$route.params.id + "/update"),
        method: "post",
        data: {
          name: this.store.name,
          description: this.store.description,
          allow_not_voted: this.store.allowNotVoted,
        },
      })
        .then((_) => {
          this.reload();
          if (this.editComp) {
            this.editComp.hasChanges = false;
          }
        })
        .catch((x) => {
          if (this.errorModal == null) {
            return;
          }
          this.errorModal.doShow();
          this.errorModal.data = x.response.data;
          this.reload();
        });
    },
  },
});
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
