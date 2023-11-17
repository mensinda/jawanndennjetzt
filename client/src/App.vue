<template>
  <div class="app-root d-flex flex-column min-vh-100">
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary mb-4" data-bs-theme="dark">
      <div class="container-fluid">
        <router-link class="navbar-brand d-flex flex-rows align-items-center" to="/">
          <img v-if="hasIcon" :src="logoPath" :style="logoStyle" />
          <div :class="{ 'ms-2': hasIcon }">{{ $t("main.title") }}</div>
        </router-link>
        <button
          class="navbar-toggler collapsed"
          type="button"
          data-bs-toggle="collapse"
          data-bs-target="#navbar"
          aria-controls="navbar"
          aria-expanded="false"
          aria-label="Toggle navigation"
        >
          <span class="navbar-toggler-icon"></span>
        </button>
        <div class="navbar-collapse collapse" id="navbar" style="">
          <ul class="navbar-nav me-auto">
            <li class="nav-item">
              <router-link class="nav-link" :class="{ active: route.name == 'home' }" to="/">{{
                $t("root.home")
              }}</router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" :class="{ active: route.name == 'new' }" to="/new">{{
                $t("root.create-poll")
              }}</router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" :class="{ active: route.name == 'my-polls' }" to="/my-polls">{{
                $t("root.my-polls")
              }}</router-link>
            </li>
          </ul>
          <ul class="navbar-nav">
            <li v-if="JWDJ_LOGIN_MANAGER && store.user?.authorised">
              <router-link class="nav-link" :class="{ active: route.name == 'user' }" to="/user">{{
                store.user?.user?.name
              }}</router-link>
            </li>
            <li class="nav-item me-3 d-flex align-items-center dark-mode-container">
              <DarkModeToggle />
            </li>
            <li class="nav-item me-3 d-flex">
              <select class="form-select" :value="$i18n.locale" @change="(ev) => switchLocale(ev.target?.value)">
                <option v-for="(v, k) in ALL_LOCALES" :key="k" :value="k">{{ v.name }}</option>
              </select>
            </li>
            <li class="nav-item" style="cursor: pointer" @click="openGitHub">
              <div class="nav-link d-flex flex-rows">
                <svg viewBox="0 0 98 96" width="24" height="24" xmlns="http://www.w3.org/2000/svg">
                  <path
                    fill-rule="evenodd"
                    clip-rule="evenodd"
                    d="M48.854 0C21.839 0 0 22 0 49.217c0 21.756 13.993 40.172 33.405 46.69 2.427.49 3.316-1.059 3.316-2.362 0-1.141-.08-5.052-.08-9.127-13.59 2.934-16.42-5.867-16.42-5.867-2.184-5.704-5.42-7.17-5.42-7.17-4.448-3.015.324-3.015.324-3.015 4.934.326 7.523 5.052 7.523 5.052 4.367 7.496 11.404 5.378 14.235 4.074.404-3.178 1.699-5.378 3.074-6.6-10.839-1.141-22.243-5.378-22.243-24.283 0-5.378 1.94-9.778 5.014-13.2-.485-1.222-2.184-6.275.486-13.038 0 0 4.125-1.304 13.426 5.052a46.97 46.97 0 0 1 12.214-1.63c4.125 0 8.33.571 12.213 1.63 9.302-6.356 13.427-5.052 13.427-5.052 2.67 6.763.97 11.816.485 13.038 3.155 3.422 5.015 7.822 5.015 13.2 0 18.905-11.404 23.06-22.324 24.283 1.78 1.548 3.316 4.481 3.316 9.126 0 6.6-.08 11.897-.08 13.526 0 1.304.89 2.853 3.316 2.364 19.412-6.52 33.405-24.935 33.405-46.691C97.707 22 75.788 0 48.854 0z"
                    fill="#fff"
                  />
                </svg>
                <div class="ms-2">GitHub</div>
              </div>
            </li>
          </ul>
        </div>
      </div>
    </nav>
    <div class="main-area mr-auto">
      <router-view />
    </div>
    <footer class="footer mt-auto">
      <div class="container text-muted mb-1">{{ store.footerInfo }}</div>
    </footer>
  </div>
</template>

<script lang="ts" setup>
import { computed } from "vue";
import { pollStore } from "@/store";
import {
  JWDJ_LOGO,
  JWDJ_LOGO_WIDTH,
  JWDJ_LOGO_HEIGHT,
  JWDJ_LOGO_VERTICAL_MARGIN,
  JWDJ_LOGIN_MANAGER,
  DarkModeToggle,
} from "@/config";
import { ALL_LOCALES, updateLocale } from "@/locales";
import { useRoute } from "vue-router";

const store = pollStore();
const route = useRoute();
document.title = "JaWannDennJetzt";

function openGitHub() {
  window.open("https://github.com/mensinda/jawanndennjetzt", "_blank", "noreferrer");
}

function switchLocale(locale: string | null) {
  if (locale != null) {
    updateLocale(locale);
  }
}

// User auth management
async function initialUserLoad() {
  const auth = await import(/* webpackChunkName: "auth" */ "@/auth");
  auth.load_user_info();
}

if (JWDJ_LOGIN_MANAGER) {
  initialUserLoad();
}

const hasIcon = computed(() => {
  return JWDJ_LOGO.trim().length > 0;
});

const logoPath = computed(() => {
  return JWDJ_LOGO.startsWith("/") ? JWDJ_LOGO : "/" + JWDJ_LOGO;
});

const logoStyle = computed(() => {
  return {
    width: JWDJ_LOGO_WIDTH,
    height: JWDJ_LOGO_HEIGHT,
    "margin-top": JWDJ_LOGO_VERTICAL_MARGIN,
    "margin-bottom": JWDJ_LOGO_VERTICAL_MARGIN,
  };
});
</script>

<style lang="scss">
@use "sass:map";
@import "theme.scss";

.navbar {
  z-index: 20;
}

.nav-link.active {
  font-weight: bold;
}

.dark-mode-container {
  @media (max-width: map.get($grid-breakpoints, "lg") - 1px) {
    margin-top: 5px;
    margin-bottom: 10px;
  }
}

.remove-last-margin p:last-child {
  margin-bottom: 0;
}

.root-display-container {
  position: fixed;
  bottom: 0;
  right: 0;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-content: center;
  height: 100vh;
  width: 100vw;
  z-index: 10;
}

.text-invisible {
  color: rgba(0, 0, 0, 0) !important;
  text-shadow: none !important;
  user-select: none;
}

.home-btn-container {
  display: grid;
  grid-template-columns: 1fr min-content 1fr;
}

.card-header {
  user-select: none;
  font-weight: bold;
}
</style>
