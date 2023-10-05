<template>
  <ModalErrorMessage ref="errorModal" />
  <ModalClose ref="closeModal" @option-picked="(x) => doPollClose(x)" />
  <div v-if="pollstatus == 'loading'">
    <div class="root-display-container text-center">
      <h1 class="display-1 text-muted">{{ $t("main.title") }}</h1>
      <h3 class="mb-5 text-muted">{{ $t("main.subtitle") }}</h3>
      <h1 class="mb-5">{{ $t("main.loading-poll") }}</h1>
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
    <div v-if="!canSubmit && !store.isClosed && hasChanges" class="card mt-3 mb-2">
      <div class="card-header bg-danger text-white">{{ $t("poll.unable-to-submit") }}</div>
      <div class="card-body bg-danger" style="--bs-bg-opacity: 0.15">
        <ul class="mb-0">
          <li v-if="!hasUserName">{{ $t("poll.no-user-name") }}</li>
          <li v-if="!hasVoted && store.allowNotVoted">{{ $t("poll.at-least-one-choice-required") }}</li>
          <li v-if="!hasVoted && !store.allowNotVoted">{{ $t("poll.all-choices-required") }}</li>
        </ul>
      </div>
    </div>
    <!--  - Submit button -->
    <div class="mb-3">
      <div class="vote-button-container">
        <div class="submit-container">
          <button @click="doSubmit" class="btn" :class="submitBtnCls" type="button">
            {{ submitMsg }}
          </button>
        </div>
        <div class="control-container">
          <button
            v-if="store.isOwner"
            @click="$router.push({ name: 'edit', params: { id: $route.params.id } })"
            class="btn btn-info"
            :class="{ disabled: pollstatus == 'updating' || store.isClosed }"
            type="button"
          >
            {{ $t("poll.edit-poll") }}
          </button>
          <button
            v-if="store.isOwner && !store.isClosed"
            @click="closeModal?.doShow()"
            class="btn btn-danger"
            :class="{ disabled: pollstatus == 'updating' || (store.ballots.length == 0 && !store.alreadyVoted) }"
            type="button"
          >
            {{ $t("poll.close-poll") }}
          </button>
          <button
            v-if="store.isOwner && store.isClosed"
            @click="doPollReopen"
            class="btn btn-success"
            :class="{ disabled: pollstatus == 'updating' }"
            type="button"
          >
            {{ $t("poll.reopen-poll") }}
          </button>
          <button @click="doCopyLink" class="btn btn-info" :class="{ disabled: hasJustCopied }" type="button">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="currentColor" viewBox="0 0 16 16">
              <path
                d="M4.715 6.542 3.343 7.914a3 3 0 1 0 4.243 4.243l1.828-1.829A3 3 0 0 0 8.586 5.5L8 6.086a1.002 1.002 0 0 0-.154.199 2 2 0 0 1 .861 3.337L6.88 11.45a2 2 0 1 1-2.83-2.83l.793-.792a4.018 4.018 0 0 1-.128-1.287z"
              />
              <path
                d="M6.586 4.672A3 3 0 0 0 7.414 9.5l.775-.776a2 2 0 0 1-.896-3.346L9.12 3.55a2 2 0 1 1 2.83 2.83l-.793.792c.112.42.155.855.128 1.287l1.372-1.372a3 3 0 1 0-4.243-4.243L6.586 4.672z"
              />
            </svg>
            {{ hasJustCopied ? $t("poll.link-copied") : $t("poll.copy-link") }}
          </button>
        </div>
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
import { endpointUrl, setStoreFromResponse, PollData } from "@/util";
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
      hasJustCopied: false,
    };
  },

  mounted() {
    this.pollstatus = "loading";
    this.hasJustCopied = false;
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
        return this.$t("poll.closed");
      }
      return this.store.alreadyVoted ? this.$t("poll.update-vote") : this.$t("poll.cast-vote");
    },

    submitBtnCls(): { [key: string]: boolean } {
      return {
        "btn-success": !this.submitDisabled,
        "btn-secondary": this.submitDisabled,
        disabled: this.submitDisabled,
      };
    },

    canSubmit(): boolean {
      return this.hasUserName && this.hasVoted && !this.store.isClosed;
    },

    submitDisabled() {
      return !this.canSubmit || this.pollstatus == "updating" || !this.hasChanges;
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
      for (const vote of this.store.myBallot.votes) {
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
      axios<PollData>({
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

    async doCopyLink() {
      if (this.hasJustCopied) {
        return;
      }
      try {
        await navigator.clipboard.writeText(location.origin + this.$route.fullPath);
        this.hasJustCopied = true;
        setTimeout(() => {
          this.hasJustCopied = false;
        }, 5000);
      } catch (_) {
        this.hasJustCopied = false;
      }
    },
  },
});
</script>

<style lang="scss">
.vote-button-container {
  display: flex;
  flex-direction: row;
  flex-wrap: wrap;
  //grid-template-columns: 1fr max-content;
  gap: 10px;

  .submit-container {
    flex-grow: 16;
    display: flex;
    gap: 10px;

    @media (min-width: 280px) {
      min-width: 256px;
    }

    button {
      flex-grow: 1;
    }
  }

  .control-container {
    flex-grow: 1;
    display: flex;
    gap: 10px;
    flex-wrap: wrap;

    button {
      flex-grow: 1;
      min-width: 150px;
      @media (min-width: 256px) {
        width: 150px;
      }
    }
  }
}
</style>
