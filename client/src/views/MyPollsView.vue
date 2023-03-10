<template>
  <ModalErrorMessage ref="errorModal" />
  <div class="container">
    <h1 class="display-2 text-center mb-4">My polls</h1>
    <div class="card mb-4">
      <label class="card-header">Polls created by me</label>
      <div class="card-body">
        <div v-if="createdByMe.length == 0" class="text-muted">You have not created any polls yet...</div>
        <ul class="mb-0">
          <li v-if="loading" class="text-muted">Loading...</li>
          <li v-for="x in createdByMe" :key="x.id">
            <div><router-link class="remove-last-margin" :to="`/poll/${x.id}`" v-html="markdown(x.name)" /></div>
          </li>
        </ul>
      </div>
    </div>
    <div class="card">
      <label class="card-header">Polls I have voted in</label>
      <div class="card-body">
        <div v-if="votedIn.length == 0" class="text-muted">You have not voted on any polls yet...</div>
        <ul class="mb-0">
          <li v-if="loading" class="text-muted">Loading...</li>
          <li v-for="x in votedIn" :key="x.id">
            <div><router-link class="remove-last-margin" :to="`/poll/${x.id}`" v-html="markdown(x.name)" /></div>
          </li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import axios from "axios";
import { defineComponent, ref } from "vue";
import { marked } from "marked";
import { sanitize } from "dompurify";
import { endpointUrl } from "@/util";
import ModalErrorMessage from "@/components/ModalErrorMessage.vue";

export default defineComponent({
  components: {
    ModalErrorMessage,
  },

  data(): {
    loading: boolean;
    createdByMe: { id: string; name: string }[];
    votedIn: { id: string; name: string }[];
  } {
    return {
      loading: true,
      createdByMe: [],
      votedIn: [],
    };
  },

  setup() {
    const errorModal = ref<typeof ModalErrorMessage | null>(null);

    return { errorModal };
  },

  mounted() {
    this.reload();
  },

  methods: {
    markdown(raw: string): string {
      return sanitize(marked.parse(raw, { gfm: true }), { USE_PROFILES: { html: true } });
    },

    reload() {
      this.loading = true;
      this.createdByMe = [];
      this.votedIn = [];
      axios({
        url: endpointUrl("api/my-polls"),
        method: "get",
      })
        .then((x) => {
          this.createdByMe = x.data.created_by_me;
          this.votedIn = x.data.voted_in;
          this.loading = false;
        })
        .catch((x) => {
          if (this.errorModal == null) {
            return;
          }
          this.errorModal.doShow();
          this.errorModal.data = x.response.data;
        });
    },
  },
});
</script>
