<template>
  <Transition>
    <div v-if="show">
      <div @click="show = false" class="modal modal-lg show" role="dialog" style="display: block">
        <div @click.stop="() => {}" class="modal-dialog" role="document">
          <div class="modal-content">
            <div class="modal-header bg-info fw-bold text-white">
              <h5 class="modal-title user-select-none">{{ $t("modal.close.close-poll") }}</h5>
              <button @click="show = false" type="button" class="btn-close text-white" aria-label="Close">
                <span aria-hidden="true"></span>
              </button>
            </div>
            <div class="modal-body">
              <h5 class="mb-4 user-select-none">{{ $t("modal.close.final-choice") }}</h5>

              <!-- Main area where the magic happens -->
              <div class="poll-root mb-4">
                <div class="poll-container" :style="gridTemplate">
                  <!-- Options row -->
                  <span>
                    <b>{{ $t("modal.close.option") }}</b>
                  </span>
                  <span
                    v-for="opt in store.options"
                    :key="opt.vid"
                    class="remove-last-margin text-center"
                    scope="col"
                    v-html="markdown(opt.name)"
                  />

                  <!-- Sum row -->
                  <span class="mt-3 user-select-none">
                    <b>
                      {{ $t("common.total-votes") }}
                    </b>
                  </span>
                  <div
                    class="text-center d-flex flex-column mt-3"
                    v-for="(opt, optIdx) in store.options"
                    :key="opt.vid"
                  >
                    <span
                      :class="{ 'fw-bold bg-success bg-opacity-50': isBestOption(optIdx) }"
                      style="margin-bottom: 3px"
                    >
                      {{ sumData.yes[optIdx] }}
                    </span>
                    <span
                      :class="{ 'fw-bold bg-warning bg-opacity-50': isMaybeAnOption(optIdx) }"
                      style="padding-bottom: 3px"
                    >
                      ({{ sumData.maybe[optIdx] }})
                    </span>
                    <span class="text-arrow fs-2 fw-bold" :class="{ 'text-invisible': optIdx != selectedIdx }">
                      👑
                    </span>
                  </div>

                  <!-- Button row -->
                  <span class="mt-3">
                    <b>{{ $t("modal.close.select-option") }}</b>
                  </span>
                  <button
                    v-for="(opt, optIdx) in store.options"
                    :key="opt.vid"
                    class="btn text-center fs-4"
                    :class="{
                      'btn-success': isBestOption(optIdx),
                      'btn-warning': !isBestOption(optIdx) && isMaybeAnOption(optIdx),
                      'btn-secondary': !isBestOption(optIdx) && !isMaybeAnOption(optIdx),
                      'opacity-50': selectedIdx != optIdx,
                    }"
                    @click="selectedIdx = optIdx"
                  >
                    ↑
                  </button>
                </div>
              </div>
              <small class="text-muted">{{ $t("modal.close.note-can-be-reopened") }}</small>
            </div>

            <div class="modal-footer">
              <button
                @click="selectedIdx = -1"
                type="button"
                class="btn btn-warning me-auto"
                :class="{ disabled: selectedIdx < 0 }"
              >
                {{ $t("modal.close.clear-selection") }}
              </button>
              <button
                @click="handleConfirm()"
                type="button"
                class="btn"
                :class="{ 'btn-primary': selectedIdx >= 0, 'btn-warning': selectedIdx < 0 }"
              >
                {{ $t("modal.close.close-the-poll") }}
              </button>
              <button @click="show = false" type="button" class="btn btn-danger" data-dismiss="modal">
                {{ $t("modal.close.cancel") }}
              </button>
            </div>
          </div>
        </div>
      </div>
      <div @click="show = false" class="modal-backdrop show" id="backdrop" style="display: block"></div>
    </div>
  </Transition>
</template>

<script lang="ts" setup>
import { ref, computed } from "vue";
import { pollStore } from "@/store";
import { sumVotesData, markdown } from "@/util";

const emit = defineEmits(["optionPicked"]);
defineExpose({ doShow });

const store = pollStore();

const show = ref(false);
const selectedIdx = ref(-1);

const numOpts = computed(() => store.options.length);
const sumData = computed(() => sumVotesData());

const gridTemplate = computed(() => {
  return {
    "grid-template-columns": `135px repeat(${numOpts.value}, minmax(50px, min-content))`,
  };
});

function doShow() {
  show.value = true;
  selectedIdx.value = -1;
  if (sumData.value.maxYes > 0) {
    for (let i = 0; i < sumData.value.yes.length; ++i) {
      if (sumData.value.maxYes == sumData.value.yes[i]) {
        selectedIdx.value = i;
        break;
      }
    }
  }
}

function isBestOption(optIdx: number): boolean {
  return sumData.value.maxYes == sumData.value.yes[optIdx] && sumData.value.yes[optIdx] > 0;
}

function isMaybeAnOption(optIdx: number): boolean {
  return sumData.value.maxMaybe == sumData.value.maybe[optIdx] && sumData.value.maybe[optIdx] > 0;
}

function handleConfirm() {
  emit("optionPicked", selectedIdx.value);
  show.value = false;
}
</script>

<style lang="scss">
.poll-root {
  display: flex;
  flex-direction: row;
}

.poll-root::before,
.poll-root::after {
  content: "";
  margin: auto;
}

.poll-container {
  overflow-x: auto;
  display: grid;
  grid-template-rows: min-content min-content min-content;
  grid-auto-flow: row;
  gap: 3px 3px;
  grid-gap: 3px 3px;
}
</style>
