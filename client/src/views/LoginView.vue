<template>
  <ModalErrorMessage ref="errorModal" />
  <div class="container">
    <h1 class="display-2 text-center mb-5">{{ $t("auth.login") }}</h1>
    <div class="card mb-4">
      <label class="card-header">{{ $t("auth.required") }}</label>
      <div class="card-body">
        <h3 class="text-center mb-3">{{ $t("auth.login-info", { type: JWDJ_LOGIN_SYSTEM_NAME }) }}</h3>
        <form>
          <div class="form-group">
            <label for="i-username" class="form-label mt-4">{{ $t("auth.username") }}</label>
            <input
              type="email"
              class="form-control"
              id="i-username"
              :placeholder="$t('auth.enter-username')"
              :disabled="loginInProgress"
              @keydown="handleKeydown"
              v-model="username"
            />
          </div>
          <div class="form-group">
            <label for="i-pw" class="form-label mt-4">{{ $t("auth.password") }}</label>
            <input
              type="password"
              class="form-control"
              id="i-pw"
              :placeholder="$t('auth.enter-password')"
              :disabled="loginInProgress"
              @keydown="handleKeydown"
              v-model="password"
            />
          </div>
          <div class="d-flex">
            <button
              type="button"
              class="btn btn-success mt-3 flex-grow-1"
              @click="doLogin"
              :disabled="loginInProgress || password.length == 0 || username.trim().length == 0"
            >
              {{ $t("auth.login") }}
            </button>
          </div>
          <h5 class="text-center text-danger mt-4" v-if="failedOnce">
            {{ $t("auth.failed") }}
          </h5>
        </form>
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
import axios from "@/axios";
import { ref } from "vue";
import { endpointUrl } from "@/util";
import { pollStore } from "@/store";
import { JWDJ_LOGIN_SYSTEM_NAME } from "@/config";
import { UserAuth } from "@/model";
import ModalErrorMessage from "@/components/ModalErrorMessage.vue";
import router from "@/router";

const store = pollStore();
const errorModal = ref<typeof ModalErrorMessage | null>(null);

const username = ref("");
const password = ref("");

const loginInProgress = ref(false);
const failedOnce = ref(false);

function handleKeydown(e: KeyboardEvent) {
  if (e.key === "Enter") {
    doLogin();
  }
}

function doLogin() {
  if (username.value.trim().length == 0 || password.value.length == 0) {
    return;
  }
  loginInProgress.value = true;
  axios<UserAuth>({
    url: endpointUrl("api/auth/login"),
    method: "post",
    data: {
      username: username.value,
      password: password.value,
    },
  })
    .then((x) => {
      loginInProgress.value = false;
      store.user = x.data;
      if (store.user.authorised) {
        router.push({ name: "new" });
      } else {
        failedOnce.value = true;
      }
    })
    .catch((x) => {
      loginInProgress.value = false;
      if (errorModal.value == null) {
        return;
      }
      errorModal.value.doShow();
      errorModal.value.data = x.response.data;
    });
}
</script>
