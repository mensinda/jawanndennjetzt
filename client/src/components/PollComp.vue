<template>
  <h1 class="display-3 text-center mb-5" v-html="markdown(store.name)" />
  <div class="card mb-2">
    <div class="card-header remove-last-margin">{{ $t("poll_comp.voting-overview") }}</div>
    <div class="card-body">
      <div class="poll-root mb-2">
        <div class="poll-container mt-3" :style="gridTemplate">
          <!-- Header -->
          <span class="user-select-none">
            <b>{{ $t("poll_comp.user") }}</b>
          </span>
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
                :maxlength="LIMITS.NAME_LENGTH"
                :placeholder="$t('poll_comp.your-name')"
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
            <span class="mt-3 user-select-none">
              <b>{{ $t("common.total-votes") }}</b>
            </span>
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
              >
                👑
              </span>
            </div>
            <span class="mt-3" />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { pollStore } from "@/store";
import { ref, computed } from "vue";
import VoteComp from "./VoteComp.vue";
import { Ballot } from "@/model";
import { LIMITS } from "@/limits";
import { sumVotesData, markdown } from "@/util";

const store = pollStore();

defineExpose();
defineEmits(["userInputChanged"]);
const prop = defineProps({
  mode: {
    type: String,
    required: true,
  },
});

const hasChanges = ref(false);

function isBestOption(optIdx: number): boolean {
  return sumData.value.maxYes == sumData.value.yes[optIdx] && sumData.value.yes[optIdx] > 0;
}
function isMaybeAnOption(optIdx: number): boolean {
  return sumData.value.maxMaybe == sumData.value.maybe[optIdx] && sumData.value.maybe[optIdx] > 0;
}
function shouldHaveArrow(optIdx: number): boolean {
  if (store.isClosed) {
    return optIdx == store.closedOptionIndex;
  }
  return isBestOption(optIdx);
}
function resultOpacity(optIdx: number): { [d: string]: boolean } {
  return {
    "bg-opacity-75": store.isClosed && optIdx == store.closedOptionIndex,
    "bg-opacity-50": !store.isClosed,
    "bg-opacity-25": store.isClosed && optIdx != store.closedOptionIndex,
  };
}

const gridTemplate = computed(() => {
  const repeatCols = numOpts.value > 0 ? `repeat(${numOpts.value}, minmax(50px, min-content))` : "";
  const repeatRows = numBallots.value > 0 ? `repeat(${numBallots.value}, minmax(50px, min-content))` : "";
  const inputRow = prop.mode == "normal" && !store.isClosed ? "min-content" : "";
  return {
    "grid-template-columns": `minmax(150px, min-content) ${repeatCols} minmax(150px, min-content)`,
    "grid-template-rows": `min-content ${repeatRows} ${inputRow} min-content`,
  };
});

const vueMyBallot = computed(() => {
  const initial_name_raw = store.user?.user?.name;
  const initial_name = initial_name_raw === undefined ? "" : initial_name_raw;
  return store.myBallot == null ? new Ballot(initial_name, [], null) : store.myBallot;
});

const vueDisplayBallots = computed(() => {
  if ((prop.mode == "normal" && !store.isClosed) || (store.isClosed && !store.alreadyVoted) || store.myBallot == null) {
    return store.ballots;
  }
  const res = [...store.ballots];
  res.push(store.myBallot);
  return res;
});

const numOpts = computed(() => store.options.length);
const numBallots = computed(() => vueDisplayBallots.value.length);
const sumData = computed(() => sumVotesData());
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
