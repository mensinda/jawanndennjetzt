<template>
  <div class="card">
    <div v-if="store.description != null && store.description.trim().length > 0" class="form-group">
      <div class="card-body">
        <div class="card-text remove-last-margin" v-html="markdown(store.description)"></div>
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { pollStore } from "@/store";
import { markdown } from "@/util";

const store = pollStore();
</script>
