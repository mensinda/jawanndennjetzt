<template>
  <h1 class="display-3 text-center mb-5" v-html="markdown(store.name)" />
  <div class="card mb-2">
    <div class="card-header remove-last-margin">Voting overview</div>
    <div class="card-body">
      <div class="poll-root mb-2">
        <div class="poll-container mt-3" :style="gridTemplate">
          <!-- Header -->
          <span class="user-select-none"><b>User</b></span>
          <span
            v-for="opt in store.options"
            :key="opt.vid"
            class="rounded-1 remove-last-margin text-center"
            :class="{
              'text-muted !important': store.isClosed && opt.index != store.closedOptionIndex,
            }"
            scope="col"
            v-html="markdown(opt.name)"
          />
          <div />

          <!-- Already cast ballots -->
          <div v-for="ballot in vueDisplayBallots" :key="ballot.vid" style="display: contents">
            <div v-html="markdown(ballot.name)" class="remove-last-margin overflow-auto" style="align-self: center" />
            <VoteComp
              v-for="(vote, voteIdx) in ballot.votes"
              :key="vote.vid"
              :vote="vote"
              :highlight="store.isClosed && voteIdx == store.closedOptionIndex"
              :editable="false"
            />
            <div
              v-html="markdown(ballot.name)"
              class="remove-last-margin overflow-hidden text-invisible"
              style="align-self: center"
            />
          </div>

          <!-- My ballot row -->
          <div v-if="mode == 'normal' && !store.isClosed" style="display: contents">
            <div class="input-wrapper">
              <input
                v-model="vueMyBallot.name"
                class="form-control"
                :class="{ 'is-invalid': hasChanges && vueMyBallot.name.length <= 0 }"
                :maxlength="limits.NAME_LENGTH"
                placeholder="Your name..."
                @input="
                  $emit('userInputChanged');
                  hasChanges = true;
                "
              />
            </div>
            <VoteComp
              v-for="vote in vueMyBallot.votes"
              :key="vote.vid"
              :vote="vote"
              :editable="true"
              @onChange="$emit('userInputChanged')"
            />
            <div class="input-wrapper" />
          </div>

          <!-- Sum section -->
          <div style="display: contents">
            <span class="mt-3 user-select-none"><b>Total Votes</b></span>
            <div class="text-center d-flex flex-column mt-3" v-for="(opt, optIdx) in store.options" :key="opt.vid">
              <span
                class="user-select-none"
                :class="{
                  'rounded-1 fw-bold bg-success': isBestOption(optIdx),
                  ...resultOpacity(optIdx),
                }"
                style="margin-bottom: 3px"
              >
                {{ sumData.yes[optIdx] }}
              </span>
              <span
                class="user-select-none"
                :class="{ 'rounded-1 fw-bold bg-warning': isMaybeAnOption(optIdx), ...resultOpacity(optIdx) }"
                style="padding-bottom: 3px"
              >
                ({{ sumData.maybe[optIdx] }})
              </span>
              <span
                v-if="!store.isClosed"
                class="text-arrow fs-2 fw-bold user-select-none"
                :class="{ 'text-invisible': !shouldHaveArrow(optIdx) }"
              >
                ⥣
              </span>
              <span
                v-if="store.isClosed"
                class="fs-2 user-select-none"
                :class="{ 'text-invisible': !shouldHaveArrow(optIdx) }"
                >👑</span
              >
            </div>
            <span class="mt-3" />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { pollStore } from "@/store";
import { marked } from "marked";
import { defineComponent } from "vue";
import { sanitize } from "dompurify";
import VoteComp from "./VoteComp.vue";
import { Ballot } from "@/model";
import { LIMITS } from "@/limits";
import { sumVotesData } from "@/util";

export default defineComponent({
  components: {
    VoteComp,
  },

  emits: ["userInputChanged"],

  props: {
    mode: {
      type: String,
      required: true,
    },
  },

  data() {
    return { hasChanges: false };
  },

  setup() {
    const store = pollStore();

    return { store };
  },

  methods: {
    markdown(raw: string): string {
      return sanitize(marked.parse(raw, { gfm: true }), { USE_PROFILES: { html: true } });
    },
    isBestOption(optIdx: number): boolean {
      return this.sumData.maxYes == this.sumData.yes[optIdx] && this.sumData.yes[optIdx] > 0;
    },
    isMaybeAnOption(optIdx: number): boolean {
      return this.sumData.maxMaybe == this.sumData.maybe[optIdx] && this.sumData.maybe[optIdx] > 0;
    },
    shouldHaveArrow(optIdx: number): boolean {
      if (this.store.isClosed) {
        return optIdx == this.store.closedOptionIndex;
      }
      return this.isBestOption(optIdx);
    },
    resultOpacity(optIdx: number): { [d: string]: boolean } {
      return {
        "bg-opacity-75": this.store.isClosed && optIdx == this.store.closedOptionIndex,
        "bg-opacity-50": !this.store.isClosed,
        "bg-opacity-25": this.store.isClosed && optIdx != this.store.closedOptionIndex,
      };
    },
  },

  computed: {
    gridTemplate(): { "grid-template-columns": string; "grid-template-rows": string } {
      const repeatCols = this.numOpts > 0 ? `repeat(${this.numOpts}, minmax(50px, min-content))` : "";
      const repeatRows = this.numBallots > 0 ? `repeat(${this.numBallots}, minmax(50px, min-content))` : "";
      const inputRow = this.mode == "normal" && !this.store.isClosed ? "min-content" : "";
      return {
        "grid-template-columns": `minmax(150px, min-content) ${repeatCols} minmax(125px, min-content)`,
        "grid-template-rows": `min-content ${repeatRows} ${inputRow} min-content`,
      };
    },

    vueMyBallot(): Ballot {
      return this.store.myBallot == null ? new Ballot("", [], null) : this.store.myBallot;
    },

    vueDisplayBallots(): Ballot[] {
      if (
        (this.mode == "normal" && !this.store.isClosed) ||
        (this.store.isClosed && !this.store.alreadyVoted) ||
        this.store.myBallot == null
      ) {
        return this.store.ballots;
      }
      const res = [...this.store.ballots];
      res.push(this.store.myBallot);
      return res;
    },

    numOpts(): number {
      return this.store.options.length;
    },

    numBallots(): number {
      return this.vueDisplayBallots.length;
    },

    sumData() {
      return sumVotesData();
    },

    limits() {
      return LIMITS;
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
  grid-auto-flow: row;
  gap: 3px 3px;
  grid-gap: 3px 3px;
}

.input-wrapper {
  padding-left: 5px;
  padding-right: 10px;
  padding-top: 5px;
  padding-bottom: 5px;
}

.text-arrow {
  font-size: x-large;
  user-select: none;
}
</style>
