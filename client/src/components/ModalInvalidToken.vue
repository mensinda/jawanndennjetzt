<template>
  <Transition>
    <div v-if="show">
      <div @click="show = false" class="modal show" role="dialog" style="display: block">
        <div @click.stop="() => {}" class="modal-dialog" role="document">
          <div class="modal-content">
            <div class="modal-header bg-danger fw-bold text-white">
              <h5 class="modal-title">
                <b>{{ $t("modal.error.title") }}</b>
              </h5>
              <button @click="show = false" type="button" class="btn-close" aria-label="Close">
                <span aria-hidden="true"></span>
              </button>
            </div>
            <div class="modal-body d-flex flex-column">
              <p>
                {{ $t("modal.error.invalid-otp") }}
              </p>
            </div>
            <div class="modal-footer">
              <button @click="show = false" type="button" class="btn btn-danger" data-dismiss="modal">
                {{ $t("common.close") }}
              </button>
            </div>
          </div>
        </div>
      </div>
      <div @click="show = false" class="modal-backdrop show" id="backdrop" style="display: block"></div>
    </div>
  </Transition>
</template>

<script lang="ts" setup>
import { ref, onMounted } from "vue";

defineExpose({ doShow });

const show = ref(false);

onMounted(() => (show.value = false));

function doShow() {
  show.value = true;
}
</script>
