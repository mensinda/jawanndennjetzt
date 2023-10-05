<template>
  <!-- My note editor -- simpler with "real" preview directly below -->
  <div v-if="!store.isClosed">
    <h4 class="user-select-none">{{ $t("notes.my-note") }}</h4>
    <textarea
      v-model="vueMyBallot.note"
      rows="4"
      class="form-control mt-1"
      :maxlength="limits.DESCRIPTION_LENGTH"
      :placeholder="$t('notes.note-placeholder')"
      @input="$emit('userInputChanged')"
    />
    <small class="form-text text-muted user-select-none">
      {{ $t("notes.help-text") }}
    </small>
  </div>

  <!-- Add a divider between notes and note editor, if both are present at the same time -->
  <hr v-if="hasNotes && !store.isClosed" />

  <!-- Other notes -->
  <div class="note-container mb-3" v-if="hasNotes">
    <span class="fw-bold user-select-none">User</span>
    <span class="fw-bold user-select-none">Note</span>
    <div v-for="ballot in ballotsWithNote" :key="ballot.vid" style="display: contents">
      <span v-html="markdown(ballot.name)" />
      <div class="card">
        <div class="card-body">
          <div class="card-text remove-last-margin" v-html="markdown(ballot.note)" />
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { pollStore } from "@/store";
import { defineComponent } from "vue";
import { Ballot } from "@/model";
import { LIMITS } from "@/limits";
import { markdown } from "@/util";

export default defineComponent({
  setup() {
    const store = pollStore();

    return { store };
  },

  emits: ["userInputChanged"],

  methods: {
    markdown,
  },

  computed: {
    hasNotes(): boolean {
      for (const ballot of this.store.ballots) {
        if (ballot.note.trim()) {
          return true;
        }
      }
      if (this.store.myBallot && this.store.myBallot.note.trim()) {
        return true;
      }
      return false;
    },

    ballotsWithNote(): Ballot[] {
      const res = this.store.ballots.filter((x) => x.note.trim());
      if (this.store.myBallot && this.store.myBallot.note.trim()) {
        res.unshift(this.store.myBallot);
      }
      return res;
    },

    vueMyBallot(): Ballot {
      return this.store.myBallot == null ? new Ballot("", [], null) : this.store.myBallot;
    },

    limits() {
      return LIMITS;
    },
  },
});
</script>

<style lang="scss">
.note-container {
  display: grid;
  grid-template-columns: minmax(125px, min-content) auto;
  gap: 10px 10px;
  grid-gap: 10px 10px;
}
</style>
