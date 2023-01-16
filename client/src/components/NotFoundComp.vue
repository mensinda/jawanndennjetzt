<template>
  <div>
    <div class="root-display-container text-center">
      <h1 class="display-1 text-danger">{{ title }}</h1>
      <h3 class="mb-5">{{ desc }}</h3>
      <div class="home-btn-container mb-5">
        <div />
        <button @click="$router.push('/')" class="btn btn-lg btn-success text-nowrap user-select-none">
          ↲ Back to the homepage
        </button>
        <div />
      </div>
      <small class="text-muted">{{ info }}</small>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent } from "vue";

export default defineComponent({
  props: {
    title: {
      type: String,
      default: "404",
    },
    desc: {
      type: String,
      default: "The requested page was not found",
    },
    info: {
      type: String,
      default: "",
    },
  },
});
</script>
