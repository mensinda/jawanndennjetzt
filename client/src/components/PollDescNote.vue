<template>
  <div class="mb-3">
    <ul class="nav nav-tabs" role="tablist">
      <li class="nav-item" role="presentation">
        <a class="nav-link active" data-bs-toggle="tab" href="#poll-description" aria-selected="true" role="tab">
          {{ $t("poll-desc.description") }}
        </a>
      </li>
      <li class="nav-item" role="presentation">
        <a class="nav-link" data-bs-toggle="tab" href="#poll-notes" aria-selected="false" role="tab">
          {{ $t("poll-desc.notes") }} ({{ numNotes }})
        </a>
      </li>
    </ul>
  </div>

  <!--  - Description -->
  <div class="tab-content mb-3">
    <div id="poll-description" class="tab-pane fade active show">
      <PollDescription />
    </div>

    <!--  - Notes -->
    <div id="poll-notes" class="tab-pane fade">
      <PollNotes @user-input-changed="$emit('userInputChanged')" />
    </div>
  </div>
</template>

<script lang="ts">
import { pollStore } from "@/store";
import { defineComponent } from "vue";

import PollDescription from "./PollDescription.vue";
import PollNotes from "./PollNotes.vue";

export default defineComponent({
  components: {
    PollDescription,
    PollNotes,
  },

  emits: ["userInputChanged"],

  setup() {
    const store = pollStore();

    return { store };
  },

  computed: {
    numNotes(): number {
      let res = this.store.ballots.filter((x) => x.note.trim()).length;
      if (this.store.myBallot && this.store.myBallot.note.trim()) {
        res++;
      }
      return res;
    },
  },
});
</script>
