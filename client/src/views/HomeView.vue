<template>
  <div class="root-display-container">
    <div class="text-center mb-5">
      <h1 class="display-1">JaWannDennJetzt</h1>
      <h3>When's it gonna be?</h3>
    </div>
    <div class="home-btn-container">
      <div />
      <button @click="$router.push('/new')" class="btn btn-lg btn-success text-nowrap user-select-none">
        Create a new poll
      </button>
      <div />
    </div>
  </div>
</template>
