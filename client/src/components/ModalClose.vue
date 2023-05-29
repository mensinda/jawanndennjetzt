<template>
  <Transition>
    <div v-if="show">
      <div @click="show = false" class="modal modal-lg show" role="dialog" style="display: block">
        <div @click.stop="stop" class="modal-dialog" role="document">
          <div class="modal-content">
            <div class="modal-header bg-info fw-bold text-white">
              <h5 class="modal-title user-select-none">Close poll</h5>
              <button @click="show = false" type="button" class="btn-close text-white" aria-label="Close">
                <span aria-hidden="true"></span>
              </button>
            </div>
            <div class="modal-body">
              <h5 class="mb-4 user-select-none">Please select your final choice for this poll:</h5>

              <!-- Main area where the magic happens -->
              <div class="poll-root mb-4">
                <div class="poll-container" :style="gridTemplate">
                  <!-- Options row -->
                  <span><b>Option</b></span>
                  <span
                    v-for="opt in store.options"
                    :key="opt.vid"
                    class="remove-last-margin text-center"
                    scope="col"
                    v-html="markdown(opt.name)"
                  />

                  <!-- Sum row -->
                  <span class="mt-3 user-select-none"><b>Total Votes</b></span>
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
                  <span class="mt-3"><b>Select option</b></span>
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
              <small class="text-muted">Closed polls can be reopened at any time by their creator.</small>
            </div>

            <div class="modal-footer">
              <button
                @click="selectedIdx = -1"
                type="button"
                class="btn btn-warning me-auto"
                :class="{ disabled: selectedIdx < 0 }"
              >
                ✗ Clear selection
              </button>
              <button
                @click="handleConfirm()"
                type="button"
                class="btn"
                :class="{ 'btn-primary': selectedIdx >= 0, 'btn-warning': selectedIdx < 0 }"
              >
                🔒 Close the poll
              </button>
              <button @click="show = false" type="button" class="btn btn-danger" data-dismiss="modal">Cancel</button>
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
import { pollStore } from "@/store";
import { sumVotesData, markdown } from "@/util";

export default defineComponent({
  emits: ["optionPicked"],

  data() {
    return {
      show: false,
      selectedIdx: -1,
    };
  },

  setup() {
    const store = pollStore();

    return { store };
  },

  computed: {
    numOpts(): number {
      return this.store.options.length;
    },

    gridTemplate(): { "grid-template-columns": string } {
      return {
        "grid-template-columns": `125px repeat(${this.numOpts}, minmax(50px, min-content))`,
      };
    },

    sumData() {
      return sumVotesData();
    },
  },

  methods: {
    doShow() {
      this.show = true;
      this.selectedIdx = -1;
      if (this.sumData.maxYes > 0) {
        for (let i = 0; i < this.sumData.yes.length; ++i) {
          if (this.sumData.maxYes == this.sumData.yes[i]) {
            this.selectedIdx = i;
            break;
          }
        }
      }
    },

    isBestOption(optIdx: number): boolean {
      return this.sumData.maxYes == this.sumData.yes[optIdx] && this.sumData.yes[optIdx] > 0;
    },

    isMaybeAnOption(optIdx: number): boolean {
      return this.sumData.maxMaybe == this.sumData.maybe[optIdx] && this.sumData.maybe[optIdx] > 0;
    },

    markdown,

    handleConfirm() {
      this.$emit("optionPicked", this.selectedIdx);
      this.show = false;
    },
  },
});
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
