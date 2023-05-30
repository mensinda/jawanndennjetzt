<template>
  <Transition>
    <div v-if="show">
      <div @click="show = false" class="modal show" role="dialog" style="display: block">
        <div @click.stop="stop" class="modal-dialog" role="document">
          <div class="modal-content">
            <div class="modal-header bg-info fw-bold text-white">
              <h5 class="modal-title user-select-none">Import existing poll</h5>
              <button @click="show = false" type="button" class="btn-close text-white" aria-label="Close">
                <span aria-hidden="true"></span>
              </button>
            </div>
            <div class="modal-body">
              <div class="form-group">
                <input
                  v-model="pollInput"
                  type="input"
                  :class="{ 'is-invalid': invalidId, 'form-control': true }"
                  placeholder="Existing Poll ID or URL..."
                  @input="pollInputChanged"
                />
                <div class="text-danger small mt-1" :style="{ visibility: invalidId ? 'visible' : 'hidden' }">
                  Unable to find the poll with the ID "{{ pollIdFromInput }}"
                </div>
              </div>

              <!-- Warning -->
              <div class="mt-3">
                <span class="text-warning fw-bold">Warning:</span> Importing a poll will overwrite all current settings!
              </div>
            </div>

            <div class="modal-footer">
              <button
                @click="importPoll"
                :disabled="!isValidPoll"
                type="button"
                :class="{ btn: true, 'btn-success': isValidPoll, 'btn-secondary': !isValidPoll }"
              >
                {{ isChecking ? "Checking..." : "Import poll settings" }}
              </button>
              <button @click="show = false" type="button" class="btn btn-primary" data-dismiss="modal">Close</button>
            </div>
          </div>
        </div>
      </div>
      <div @click="show = false" class="modal-backdrop show" id="backdrop" style="display: block"></div>
    </div>
  </Transition>
</template>

<script lang="ts">
import { defineComponent } from "vue";
import { endpointUrl, markdown } from "@/util";
import { pollStore } from "@/store";
import debounce from "lodash.debounce";
import axios from "axios";

export default defineComponent({
  emits: ["importDone", "importError"],

  data() {
    return {
      show: false,
      hasChanges: false,
      isValidPoll: false,
      isChecking: false,
      pollInput: "",
    };
  },

  setup() {
    const store = pollStore();

    return { store };
  },

  computed: {
    pollIdFromInput(): string {
      const idx = this.pollInput.lastIndexOf("/");
      if (idx < 0) {
        return this.pollInput;
      }
      return this.pollInput.substring(idx + 1);
    },

    invalidId() {
      return this.hasChanges && !this.isValidPoll && !this.isChecking;
    },
  },

  methods: {
    doShow() {
      this.show = true;
      this.hasChanges = false;
      this.isValidPoll = false;
      this.isChecking = false;
      this.pollInput = "";
    },

    markdown,

    pollInputChanged() {
      this.hasChanges = true;
      this.isValidPoll = false;

      const pId = this.pollIdFromInput;
      if (pId.length < 1) {
        return;
      }

      this.isChecking = true;
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

    importPoll() {
      this.show = false;

      axios({ url: endpointUrl("api/poll/" + this.pollIdFromInput), method: "get" })
        .then((x) => {
          this.store.reset();
          this.store.name = x.data.name;
          this.store.description = x.data.description;
          this.store.options = x.data.options;
          this.store.allowNotVoted = x.data.allow_not_voted;

          this.$emit("importDone");
        })
        .catch((x) => {
          this.store.lastError = x.response.data;
          this.$emit("importError");
        });
    },

    handleConfirm() {
      this.$emit("importDone");
      this.show = false;
    },
  },
});
</script>
