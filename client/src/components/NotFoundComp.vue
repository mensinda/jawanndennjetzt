<template>
  <div>
    <div class="root-display-container text-center">
      <h1 class="display-1 text-danger">{{ title }}</h1>
      <h3 class="mb-5">{{ desc === null ? $t("404.page-not-found") : desc }}</h3>
      <div class="home-btn-container mb-5">
        <div />
        <button
          @click="$router.push({ name: 'home' })"
          class="btn btn-lg text-nowrap user-select-none"
          :class="{ [JWDJ_PRIMARY_BTN_CLS]: true }"
        >
          {{ $t("404.back") }}
        </button>
        <div />
      </div>
      <small class="text-muted">{{ info }}</small>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { JWDJ_PRIMARY_BTN_CLS } from "@/config";

defineProps({
  title: {
    type: String,
    default: "404",
  },
  desc: {
    type: String,
    default: null,
  },
  info: {
    type: String,
    default: "",
  },
});
</script>
