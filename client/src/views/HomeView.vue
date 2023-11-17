<template>
  <div class="root-display-container">
    <div class="text-center mb-5">
      <h1 class="display-1">{{ $t("main.title") }}</h1>
      <h3>{{ $t("main.subtitle") }}</h3>
    </div>
    <div class="home-btn-container">
      <div />
      <button @click="$router.push({ name: 'new' })" class="btn btn-lg btn-success text-nowrap user-select-none">
        {{ $t("main.create-a-new-poll") }}
      </button>
      <div />
    </div>
  </div>
</template>
