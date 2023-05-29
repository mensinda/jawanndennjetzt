<template>
  <ModalErrorMessage ref="errorModal" />
  <div class="container">
    <div class="row mb-3">
      <h1 class="text-center">Create a new poll</h1>
    </div>

    <!-- Main editor -->
    <div v-if="showMain">
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

    <!-- Initial setup -->
    <div v-if="!showMain" class="root-display-container">
      <div class="container">
        <div class="card">
          <div class="card-header">Do you want to start fresh or create a new poll?</div>
          <div class="card-body selection-grid">
            <span>Start from a blank slate for creating your new poll.</span>
            <button @click="startNewPoll" class="btn btn-lg btn-success">Start fresh</button>
            <hr style="grid-area: sep1" />
            <span style="grid-area: txt2">
              Or copy the settings from an existing poll by entering the poll ID or poll URL in the input field below.
            </span>
            <button
              style="grid-area: btn2"
              @click="copyExistingPoll"
              class="btn btn-primary"
              :class="{ disabled: !isValidPoll || isChecking }"
            >
              {{ isChecking ? "Checking..." : "Copy settings" }}
            </button>
            <input
              v-model="pollInput"
              type="input"
              style="grid-area: in1"
              :class="{ 'is-invalid': hasChanges && !isValidPoll && !isChecking, 'form-control': true }"
              placeholder="Existing poll ID or URL..."
              @input="pollInputChanged"
            />
            <div class="invalid-feedback">Unable to find the poll with the ID "{{ pollIdFromInput }}"</div>

            <!-- Dummy element to avoid jumping -->
            <div style="min-height: 25px; grid-area: xxx" />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import PollComp from "@/components/PollComp.vue"; // @ is an alias to /src
import EditorComp from "@/components/EditorComp.vue";
import ModalErrorMessage from "@/components/ModalErrorMessage.vue";
import axios from "axios";
import { defineComponent, ref } from "vue";
import { pollStore } from "@/store";
import { endpointUrl } from "@/util";
import PollDescription from "@/components/PollDescription.vue";
import debounce from "lodash.debounce";

export default defineComponent({
  components: {
    PollComp,
    EditorComp,
    ModalErrorMessage,
    PollDescription,
  },

  data() {
    return {
      showMain: false,
      hasChanges: false,
      pollInput: "",
      isValidPoll: false,
      isChecking: false,
    };
  },

  setup() {
    const store = pollStore();
    const errorModal = ref<typeof ModalErrorMessage | null>(null);

    return { store, errorModal };
  },

  mounted() {
    this.store.reset();

    this.showMain = false;
    this.hasChanges = false;
    this.pollInput = "";
    this.isChecking = false;
  },

  computed: {
    pollIdFromInput(): string {
      const idx = this.pollInput.lastIndexOf("/");
      if (idx < 0) {
        return this.pollInput;
      }
      return this.pollInput.substring(idx + 1);
    },
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

    pollInputChanged() {
      this.hasChanges = true;
      this.isValidPoll = false;
      this.isChecking = true;

      const pId = this.pollIdFromInput;
      if (pId.length < 1) {
        return;
      }

      this.checkPollId(pId);
    },

    checkPollId: debounce(function (this: any, pId: string) {
      axios({ url: endpointUrl("api/poll/" + pId + "/exists"), method: "get" })
        .then((x) => {
          this.isValidPoll = x.data.found;
          this.isChecking = false;
        })
        .catch((x) => {
          if (this.errorModal == null) {
            return;
          }
          this.errorModal.doShow();
          this.errorModal.data = x.response.data;
          this.isChecking = false;
        });
    }, 250),

    copyExistingPoll() {
      axios({ url: endpointUrl("api/poll/" + this.pollIdFromInput), method: "get" })
        .then((x) => {
          this.store.reset();
          this.store.name = x.data.name;
          this.store.description = x.data.description;
          this.store.options = x.data.options;
          this.store.allowNotVoted = x.data.allow_not_voted;

          this.showMain = true;
        })
        .catch((x) => {
          if (this.errorModal == null) {
            return;
          }
          this.errorModal.doShow();
          this.errorModal.data = x.response.data;
        });
    },

    startNewPoll() {
      this.store.reset();
      this.showMain = true;
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
</style>
