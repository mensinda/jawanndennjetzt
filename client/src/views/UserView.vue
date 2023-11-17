<template>
  <ModalErrorMessage ref="errorModal" />
  <div class="container">
    <h1 class="display-2 text-center mb-5">{{ $t("auth.current-user") }}</h1>
    <div class="card mb-4">
      <label class="card-header">{{ $t("auth.current-user-info") }}</label>
      <div class="card-body">
        <table class="table table-hover">
          <thead>
            <tr>
              <th>{{ $t("common.field") }}</th>
              <th>{{ $t("common.value") }}</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>{{ $t("auth.username") }}</td>
              <td>{{ store.user?.user?.username }}</td>
            </tr>
            <tr>
              <td>{{ $t("auth.name") }}</td>
              <td>{{ store.user?.user?.name }}</td>
            </tr>
            <tr>
              <td>{{ $t("auth.email") }}</td>
              <td>{{ store.user?.user?.email }}</td>
            </tr>
          </tbody>
        </table>
        <div class="d-flex">
          <button type="button" class="btn btn-danger flex-grow-1 mt-3" :disabled="logoutInProgres" @click="doLogout">
            {{ $t("auth.logout") }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
import axios from "@/axios";
import { onBeforeMount, ref } from "vue";
import { endpointUrl } from "@/util";
import { useRouter } from "vue-router";
import { pollStore } from "@/store";
import { load_user_info } from "@/auth";
import { UserAuth } from "@/model";
import ModalErrorMessage from "@/components/ModalErrorMessage.vue";

const store = pollStore();
const router = useRouter();

const errorModal = ref<typeof ModalErrorMessage | null>(null);

const logoutInProgres = ref(false);

onBeforeMount(async () => {
  await load_user_info();
  if (!store.user?.authorised) {
    router.push({ name: "home" });
  }
});

async function doLogout() {
  axios<UserAuth>({
    url: endpointUrl("api/auth/logout"),
    method: "post",
  })
    .then((x) => {
      logoutInProgres.value = false;
      store.user = x.data;
      router.push({ name: "home" });
    })
    .catch((x) => {
      logoutInProgres.value = false;
      if (errorModal.value == null) {
        return;
      }
      errorModal.value.doShow();
      errorModal.value.data = x.response.data;
    });
}
</script>
