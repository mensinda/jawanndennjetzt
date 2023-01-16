<template>
  <div class="card">
    <div v-if="store.description != null && store.description.trim().length > 0" class="form-group">
      <div class="card-body">
        <div class="card-text remove-last-margin" v-html="markdown(store.description)"></div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { pollStore } from "@/store";
import { marked } from "marked";
import { defineComponent } from "vue";
import { sanitize } from "dompurify";

export default defineComponent({
  setup() {
    const store = pollStore();

    return { store };
  },

  methods: {
    markdown(raw: string): string {
      return sanitize(marked.parse(raw, { gfm: true }), { USE_PROFILES: { html: true } });
    },
  },
});
</script>
