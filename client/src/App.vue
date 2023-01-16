<template>
  <div class="app-root d-flex flex-column min-vh-100">
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary mb-4">
      <div class="container-fluid">
        <router-link class="navbar-brand" to="/">JaWannDennJetzt</router-link>
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
              <router-link class="nav-link" :class="{ active: currRoute == 'home' }" to="/">Home</router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" :class="{ active: currRoute == 'new' }" to="/new">Create Poll</router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" :class="{ active: currRoute == 'my-polls' }" to="/my-polls"
                >My Polls</router-link
              >
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

<script lang="ts">
import { defineComponent } from "vue";
import { endpointUrl } from "@/util";
import { pollStore } from "@/store";
import axios from "axios";

export default defineComponent({
  setup() {
    const store = pollStore();
    document.title = "JaWannDennJetzt";

    axios({
      url: endpointUrl("api/session"),
      method: "get",
    })
      .then((_) => {
        // nothing to do
      })
      .catch((_) => {
        // nothing to do
      });

    return { store };
  },

  computed: {
    currRoute() {
      return this.$route.name;
    },
  },
});
</script>

<style lang="scss">
@import "theme.scss";

.navbar {
  z-index: 20;
}

.nav-link.active {
  font-weight: bold;
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
