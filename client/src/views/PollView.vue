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
  <NotFoundComp v-if="pollstatus == '404'" :desc="$t('404.poll-not-found')" :info="`{ ID = ${$route.params.id} }`" />
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
            {{ $t(submitMsg) }}
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

<script lang="ts" setup>
import PollComp from "@/components/PollComp.vue"; // @ is an alias to /src
import ModalClose from "@/components/ModalClose.vue";
import ModalErrorMessage from "@/components/ModalErrorMessage.vue";
import PollDescNote from "@/components/PollDescNote.vue";
import PollNotes from "@/components/PollNotes.vue";
import NotFoundComp from "@/components/NotFoundComp.vue";
import { pollStore } from "@/store";
import { ref, onMounted, onBeforeUnmount, computed } from "vue";
import { endpointUrl, setStoreFromResponse, PollData } from "@/util";
import { JWDJ_LOGIN_MANAGER } from "@/config";
import { useRoute } from "vue-router";
import axios, { AxiosError } from "@/axios";

const store = pollStore();
const route = useRoute();
const errorModal = ref<typeof ModalErrorMessage | null>(null);
const closeModal = ref<typeof ModalClose | null>(null);

const pollstatus = ref("loading");
const hasChanges = ref(false);
const hasJustCopied = ref(false);

onMounted(() => reload());

onBeforeUnmount(() => (store.footerInfo = ""));

async function reload() {
  pollstatus.value = "loading";
  hasJustCopied.value = false;
  store.reset();
  try {
    const res = await axios<PollData>({
      url: endpointUrl("api/poll/" + route.params.id),
      method: "get",
    });

    if (JWDJ_LOGIN_MANAGER && store.user === null) {
      const auth = await import(/* webpackChunkName: "auth" */ "@/auth");
      await auth.load_user_info();
    }
    setStoreFromResponse(res.data);
    pollstatus.value = "ready";
    hasChanges.value = false;
  } catch (x) {
    if (!(x instanceof AxiosError)) {
      return;
    }
    if (x.response?.data.code == "POLL_NOT_FOUND") {
      pollstatus.value = "404";
      return;
    }
    if (errorModal.value == null) {
      return;
    }
    errorModal.value.doShow();
    errorModal.value.data = x.response?.data;
  }
}

async function doSubmit() {
  const ballot = store.myBallot;
  if (ballot == null) {
    return;
  }

  pollstatus.value = "updating";

  try {
    await axios({
      url: endpointUrl("api/poll/" + route.params.id + "/vote"),
      method: "post",
      data: {
        name: ballot.name,
        votes: ballot.votes.map((x) => x.status).join(""),
        note: ballot.note,
      },
    });
  } catch (x) {
    if (errorModal.value == null || !(x instanceof AxiosError)) {
      return;
    }
    errorModal.value.doShow();
    errorModal.value.data = x.response?.data;
  }

  await reload();
}

async function doPollClose(optionIdx: number) {
  try {
    await axios({
      url: endpointUrl("api/poll/" + route.params.id + "/close"),
      method: "post",
      data: {
        option_idx: optionIdx,
      },
    });
  } catch (x) {
    if (errorModal.value == null || !(x instanceof AxiosError)) {
      return;
    }
    errorModal.value.doShow();
    errorModal.value.data = x.response?.data;
  }

  await reload();
}

async function doPollReopen() {
  try {
    await axios({
      url: endpointUrl("api/poll/" + route.params.id + "/reopen"),
      method: "post",
    });
  } catch (x) {
    if (errorModal.value == null || !(x instanceof AxiosError)) {
      return;
    }
    errorModal.value.doShow();
    errorModal.value.data = x.response?.data;
  }

  await reload();
}

async function doCopyLink() {
  if (hasJustCopied.value) {
    return;
  }
  try {
    await navigator.clipboard.writeText(location.origin + route.fullPath);
    hasJustCopied.value = true;
    setTimeout(() => {
      hasJustCopied.value = false;
    }, 5000);
  } catch (_) {
    hasJustCopied.value = false;
  }
}

const canSubmit = computed(() => hasUserName.value && hasVoted.value && !store.isClosed);

const submitDisabled = computed(() => !canSubmit.value || pollstatus.value == "updating" || !hasChanges.value);

const submitMsg = computed(() => {
  if (store.isClosed) {
    return "poll.closed";
  }
  return store.alreadyVoted ? "poll.update-vote" : "poll.cast-vote";
});

const submitBtnCls = computed(() => {
  return {
    "btn-success": !submitDisabled.value,
    "btn-secondary": submitDisabled.value,
    disabled: submitDisabled.value,
  };
});

const hasUserName = computed(() => {
  if (store.myBallot == null) {
    return false;
  }
  return store.myBallot.name.length > 0;
});

const hasVoted = computed(() => {
  if (store.myBallot == null) {
    return false;
  }
  let numVoted = 0;
  for (const vote of store.myBallot.votes) {
    if (vote.status != "-") {
      numVoted++;
    }
  }
  if (store.allowNotVoted && numVoted > 0) {
    return true;
  }
  return numVoted == store.myBallot.votes.length;
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
