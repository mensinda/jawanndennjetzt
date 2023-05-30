<template>
  <ModalErrorMessage ref="errorModal" />
  <ModalImportPoll ref="importModal" :onImportError="handleImportError" :onImportDone="editorComp?.optionsImported()" />
  <div class="container">
    <div class="new-poll-head-grid-helper">
      <h1 class="text-center">Create a new poll</h1>
      <button class="btn btn-info" type="button" @click="importModal?.doShow()">♻ Import existing poll</button>
    </div>

    <!-- Main editor -->
    <EditorComp ref="editorComp" submitMsg="🚀 Publish Poll 🚀" :canEditOptions="true" @submit="createPoll" />
    <hr class="mt-4 mb-4" />
    <div class="card mb-5">
      <div class="card-header">Preview</div>
      <div class="card-body">
        <span v-if="store.options.length == 0" class="text-muted user-select-none">
          Add an option to see a preview of your poll...
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

<script lang="ts">
import PollComp from "@/components/PollComp.vue"; // @ is an alias to /src
import EditorComp from "@/components/EditorComp.vue";
import ModalErrorMessage from "@/components/ModalErrorMessage.vue";
import ModalImportPoll from "@/components/ModalImportPoll.vue";
import axios from "axios";
import { defineComponent, ref } from "vue";
import { pollStore } from "@/store";
import { endpointUrl } from "@/util";
import PollDescription from "@/components/PollDescription.vue";

export default defineComponent({
  components: {
    PollComp,
    EditorComp,
    ModalErrorMessage,
    ModalImportPoll,
    PollDescription,
  },

  data() {
    return {
      hasChanges: false,
      pollInput: "",
      isValidPoll: false,
      isChecking: false,
    };
  },

  setup() {
    const store = pollStore();
    const errorModal = ref<typeof ModalErrorMessage | null>(null);
    const importModal = ref<typeof ModalImportPoll | null>(null);
    const editorComp = ref<typeof EditorComp | null>(null);

    return { store, errorModal, importModal, editorComp };
  },

  mounted() {
    this.store.reset();

    this.hasChanges = false;
    this.pollInput = "";
    this.isChecking = false;
  },

  methods: {
    createPoll() {
      axios({
        url: endpointUrl("api/new"),
        method: "post",
        data: {
          name: this.store.name,
          description: this.store.description,
          allow_not_voted: this.store.allowNotVoted,
          options: this.store.options.map((x) => {
            return {
              index: x.index,
              name: x.name,
            };
          }),
        },
      })
        .then((x) => {
          this.$router.push({ name: "poll", params: { id: x.data.id } });
        })
        .catch((x) => {
          if (this.errorModal == null) {
            return;
          }
          this.errorModal.doShow();
          this.errorModal.data = x.response.data;
        });
    },

    handleImportError() {
      if (this.errorModal == null) {
        return;
      }
      this.errorModal.doShow();
      this.errorModal.updateData(this.store.lastError);
    },
  },
});
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
  grid-template-columns: 3fr 1fr;
}

.new-poll-head-grid-helper h1 {
  grid-row: 1 / span 1;
  grid-column: 1 / span 2;
}

.new-poll-head-grid-helper button {
  grid-row: 1 / span 1;
  grid-column: 2 / span 1;
  align-self: center;
  justify-self: end;
}
</style>
