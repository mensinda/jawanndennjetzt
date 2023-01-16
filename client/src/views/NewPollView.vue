<template>
  <ModalErrorMessage ref="errorModal" />
  <div class="container">
    <div class="row mb-3">
      <h1 class="text-center">Create a new poll</h1>
    </div>
    <EditorComp submitMsg="🚀 Publish Poll 🚀" :canEditOptions="true" @submit="createPoll" />
    <hr class="mt-4 mb-4" />
    <div class="card mb-5">
      <div class="card-header">Preview</div>
      <div class="card-body">
        <span v-if="store.options.length == 0" class="text-muted user-select-none"
          >Add an option to see a preview of your poll...</span
        >
        <div v-if="store.options.length > 0">
          <PollComp mode="preview" />
          <hr v-if="store.description.trim()" />
          <PollDescription v-if="store.description.trim()" />
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import PollComp from "@/components/PollComp.vue"; // @ is an alias to /src
import EditorComp from "@/components/EditorComp.vue";
import ModalErrorMessage from "@/components/ModalErrorMessage.vue";
import axios from "axios";
import { defineComponent, ref } from "vue";
import { pollStore } from "@/store";
import { endpointUrl } from "@/util";
import PollDescription from "@/components/PollDescription.vue";

export default defineComponent({
  components: {
    PollComp,
    EditorComp,
    ModalErrorMessage,
    PollDescription,
  },

  setup() {
    const store = pollStore();
    const errorModal = ref<typeof ModalErrorMessage | null>(null);

    return { store, errorModal };
  },

  mounted() {
    this.store.reset();
  },

  methods: {
    createPoll() {
      axios({
        url: endpointUrl("api/new"),
        method: "post",
        data: {
          name: this.store.name,
          description: this.store.description,
          allow_not_voted: this.store.allowNotVoted,
          options: this.store.options.map((x) => {
            return {
              index: x.index,
              name: x.name,
            };
          }),
        },
      })
        .then((x) => {
          this.$router.push({ name: "poll", params: { id: x.data.id } });
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
