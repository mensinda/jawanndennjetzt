<template>
  <ModalErrorMessage ref="errorModal" />
  <ModalClose ref="closeModal" @option-picked="(x) => doPollClose(x)" />
  <div v-if="pollstatus == 'loading'">
    <div class="root-display-container text-center">
      <h1 class="display-1 text-muted">JaWannDennJetzt</h1>
      <h3 class="mb-5 text-muted">When's it gonna be?</h3>
      <h1 class="mb-5">Loading poll...</h1>
      <small class="text-muted">{ ID = {{ $route.params.id }} }</small>
    </div>
  </div>
  <NotFoundComp
    v-if="pollstatus == '404'"
    desc="The requested poll was not found"
    :info="`{ ID = ${$route.params.id} }`"
  />
  <div v-if="pollstatus == 'ready' || pollstatus == 'updating'" class="container">
    <PollComp mode="normal" @user-input-changed="hasChanges = true" />

    <!-- Main poll area done: Now description / notes and buttons -->

    <!-- First of all, any potential errors -->
    <div v-if="!canSubmit && !store.isClosed && hasChanges" class="card text-white mt-3 mb-2">
      <div class="card-header bg-danger">Unable to submit because:</div>
      <div class="card-body bg-danger" style="--bs-bg-opacity: 0.9">
        <ul class="mb-0">
          <li v-if="!hasUserName">No user name was entered!</li>
          <li v-if="!hasVoted && store.allowNotVoted">At least one choice needs to be voted on!</li>
          <li v-if="!hasVoted && !store.allowNotVoted">Not all choices have been voted on!</li>
        </ul>
      </div>
    </div>
    <!--  - Submit button -->
    <div class="mb-3">
      <div class="d-flex flex-row">
        <button @click="doSubmit" :class="submitBtnCls" type="button">
          {{ submitMsg }}
        </button>
        <button
          v-if="store.isOwner"
          @click="$router.push({ name: 'edit', params: { id: $route.params.id } })"
          class="btn btn-info control-btn ms-2 flex-shrink-2"
          :class="{ disabled: pollstatus == 'updating' || store.isClosed }"
          type="button"
        >
          🛠 Edit poll
        </button>
        <button
          v-if="store.isOwner && !store.isClosed"
          @click="closeModal?.doShow()"
          class="btn btn-danger control-btn ms-2 flex-shrink-2"
          :class="{ disabled: pollstatus == 'updating' || (store.ballots.length == 0 && !store.alreadyVoted) }"
          type="button"
        >
          🔒 Close poll
        </button>
        <button
          v-if="store.isOwner && store.isClosed"
          @click="doPollReopen"
          class="btn btn-success control-btn ms-2 flex-shrink-2"
          :class="{ disabled: pollstatus == 'updating' }"
          type="button"
        >
          🔓 Reopen poll
        </button>
      </div>
    </div>

    <hr />
    <PollDescNote @user-input-changed="hasChanges = true" v-if="store.description.trim()" />
    <PollNotes @user-input-changed="hasChanges = true" v-else />

    <!-- Spacer -->
    <div class="mb-5" />
  </div>
</template>

<script lang="ts">
import PollComp from "@/components/PollComp.vue"; // @ is an alias to /src
import ModalClose from "@/components/ModalClose.vue";
import ModalErrorMessage from "@/components/ModalErrorMessage.vue";
import PollDescNote from "@/components/PollDescNote.vue";
import PollNotes from "@/components/PollNotes.vue";
import NotFoundComp from "@/components/NotFoundComp.vue";
import { pollStore } from "@/store";
import { defineComponent, ref } from "vue";
import { endpointUrl, setStoreFromResponse } from "@/util";
import axios from "axios";

export default defineComponent({
  components: {
    PollComp,
    ModalClose,
    ModalErrorMessage,
    PollDescNote,
    PollNotes,
    NotFoundComp,
  },

  data() {
    return {
      pollstatus: "loading",
      hasChanges: false,
    };
  },

  mounted() {
    this.pollstatus = "loading";
    this.store.reset();
    this.reload();
  },

  beforeUnmount() {
    this.store.footerInfo = "";
  },

  setup() {
    const store = pollStore();
    const errorModal = ref<typeof ModalErrorMessage | null>(null);
    const closeModal = ref<typeof ModalClose | null>(null);

    return { store, closeModal, errorModal };
  },

  computed: {
    submitMsg(): string {
      if (this.store.isClosed) {
        return "The poll is closed";
      }
      return this.store.alreadyVoted ? "↻ Update vote" : "🗳 Cast vote";
    },

    submitBtnCls(): { [key: string]: boolean } {
      return {
        btn: true,
        "btn-success": this.canSubmit,
        "btn-secondary": !this.canSubmit,
        disabled: !this.canSubmit || this.pollstatus == "updating" || !this.hasChanges,
        "control-btn": true,
        col: true,
      };
    },

    canSubmit(): boolean {
      return this.hasUserName && this.hasVoted && !this.store.isClosed;
    },

    hasUserName(): boolean {
      if (this.store.myBallot == null) {
        return false;
      }
      return this.store.myBallot.name.length > 0;
    },

    hasVoted(): boolean {
      if (this.store.myBallot == null) {
        return false;
      }
      let numVoted = 0;
      for (let vote of this.store.myBallot.votes) {
        if (vote.status != "-") {
          numVoted++;
        }
      }
      if (this.store.allowNotVoted && numVoted > 0) {
        return true;
      }
      return numVoted == this.store.myBallot.votes.length;
    },
  },

  methods: {
    reload() {
      axios({
        url: endpointUrl("api/poll/" + this.$route.params.id),
        method: "get",
      })
        .then((x) => {
          setStoreFromResponse(x.data);
          this.pollstatus = "ready";
          this.hasChanges = false;
        })
        .catch((x) => {
          if (x.response.data.code == "POLL_NOT_FOUND") {
            this.pollstatus = "404";
            return;
          }
          if (this.errorModal == null) {
            return;
          }
          this.errorModal.doShow();
          this.errorModal.data = x.response.data;
        });
    },

    doSubmit() {
      const ballot = this.store.myBallot;
      if (ballot == null) {
        return;
      }

      this.pollstatus = "updating";

      axios({
        url: endpointUrl("api/poll/" + this.$route.params.id + "/vote"),
        method: "post",
        data: {
          name: ballot.name,
          votes: ballot.votes.map((x) => x.status).join(""),
          note: ballot.note,
        },
      })
        .then((_) => {
          this.reload();
          this.hasChanges = false;
        })
        .catch((x) => {
          if (this.errorModal == null) {
            return;
          }
          this.errorModal.doShow();
          this.errorModal.data = x.response.data;
          this.reload();
        });
    },

    doPollClose(optionIdx: number) {
      axios({
        url: endpointUrl("api/poll/" + this.$route.params.id + "/close"),
        method: "post",
        data: {
          option_idx: optionIdx,
        },
      })
        .then((_) => {
          this.reload();
        })
        .catch((x) => {
          if (this.errorModal == null) {
            return;
          }
          this.errorModal.doShow();
          this.errorModal.data = x.response.data;
          this.reload();
        });
    },

    doPollReopen() {
      axios({
        url: endpointUrl("api/poll/" + this.$route.params.id + "/reopen"),
        method: "post",
      })
        .then((_) => {
          this.reload();
        })
        .catch((x) => {
          if (this.errorModal == null) {
            return;
          }
          this.errorModal.doShow();
          this.errorModal.data = x.response.data;
          this.reload();
        });
    },
  },
});
</script>
