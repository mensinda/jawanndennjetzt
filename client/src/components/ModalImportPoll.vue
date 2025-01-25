<template>
  <Transition>
    <div v-if="show">
      <div @click="show = false" class="modal show" role="dialog" style="display: block">
        <div @click.stop="() => {}" class="modal-dialog" role="document">
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
                {{ isChecking ? $t("modal.import.import-checking") : $t("modal.import.import-btn") }}
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

const emit = defineEmits(["importDone", "importError"]);
defineExpose({ doShow });

const store = pollStore();

const show = ref(false);
const hasChanges = ref(false);
const pollInput = ref("");

// Dynamic poll ID checking / validation

const isChecking = ref(false);
const isValidPoll = ref(false);

const checkPollId = debounce(async (pId: string) => {
  const response = await window.fetch(endpointUrl("api/poll/" + pId + "/exists"));
  isChecking.value = false;
  if (response.ok) {
    isValidPoll.value = (await response.json()).found;
  }
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

async function importPoll() {
  show.value = false;

  const response = await window.fetch(endpointUrl("api/poll/" + pollIdFromInput.value));
  if (!response.ok) {
    // May throw --> exception
    try {
      store.lastError = await response.json();
    } catch {
      store.lastError = {
        msg: "Import failed!",
        code: "INTERNAL_CLIENT_ERROR",
      };
    }
    emit("importError");
  }

  const data = await response.json();

  store.reset();
  store.name = data.name;
  store.description = data.description;
  store.options = data.options;
  store.allowNotVoted = data.allow_not_voted;

  emit("importDone");
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
</script>
