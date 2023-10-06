<template>
  <Transition>
    <div v-if="show">
      <div @click="show = false" class="modal show" role="dialog" style="display: block">
        <div @click.stop="stop" class="modal-dialog" role="document">
          <div class="modal-content">
            <div class="modal-header bg-info fw-bold text-white">
              <h5 class="modal-title user-select-none">{{ $t("modal.import.title") }}</h5>
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
                  :placeholder="$t('modal.import.input-placeholder')"
                  @input="pollInputChanged"
                />
                <div class="text-danger small mt-1" :style="{ visibility: invalidId ? 'visible' : 'hidden' }">
                  {{ $t("modal.import.not-found") }} "{{ pollIdFromInput }}"
                </div>
              </div>

              <!-- Warning -->
              <div class="mt-3">
                <span class="text-warning fw-bold">{{ $t("modal.import.warning") }}</span>
                {{ $t("modal.import.waning-body") }}
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
              <button @click="show = false" type="button" class="btn btn-primary" data-dismiss="modal">
                {{ $t("common.close") }}
              </button>
            </div>
          </div>
        </div>
      </div>
      <div @click="show = false" class="modal-backdrop show" id="backdrop" style="display: block"></div>
    </div>
  </Transition>
</template>

<script setup lang="ts">
import { computed, ref } from "vue";
import { endpointUrl } from "@/util";
import { pollStore } from "@/store";
import debounce from "lodash.debounce";
import axios from "@/axios";

const emit = defineEmits(["importDone", "importError"]);

const store = pollStore();

const show = ref(false);
const hasChanges = ref(false);
const pollInput = ref("");

// Dynamic poll ID checking / validation

const isChecking = ref(false);
const isValidPoll = ref(false);

const checkPollId = debounce((pId: string) => {
  axios({ url: endpointUrl("api/poll/" + pId + "/exists"), method: "get" })
    .then((x) => {
      isValidPoll.value = x.data.found;
      isChecking.value = false;
    })
    .catch((_x) => {
      isChecking.value = false;
    });
}, 500);

function pollInputChanged() {
  hasChanges.value = true;
  isValidPoll.value = false;

  const pId = pollIdFromInput.value;
  if (pId.length < 1) {
    return;
  }

  isChecking.value = true;
  checkPollId(pId);
}

// Actual import

function importPoll() {
  show.value = false;

  axios({ url: endpointUrl("api/poll/" + pollIdFromInput.value), method: "get" })
    .then((x) => {
      store.reset();
      store.name = x.data.name;
      store.description = x.data.description;
      store.options = x.data.options;
      store.allowNotVoted = x.data.allow_not_voted;

      emit("importDone");
    })
    .catch((x) => {
      store.lastError = x.response.data;
      emit("importError");
    });
}

// Computed helpers

const pollIdFromInput = computed(() => {
  const idx = pollInput.value.lastIndexOf("/");
  if (idx < 0) {
    return pollInput.value;
  }
  return pollInput.value.substring(idx + 1);
});

const invalidId = computed(() => {
  return hasChanges.value && !isValidPoll.value && !isChecking.value;
});

// Public functions

function doShow() {
  show.value = true;
  hasChanges.value = false;
  isValidPoll.value = false;
  isChecking.value = false;
  pollInput.value = "";
}

defineExpose({
  doShow,
});
</script>
