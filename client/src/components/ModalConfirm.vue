<template>
  <Transition>
    <div v-if="show">
      <div @click="show = false" class="modal modal-lg show" role="dialog" style="display: block">
        <div @click.stop="() => {}" class="modal-dialog" role="document">
          <div class="modal-content">
            <div class="modal-header bg-danger fw-bold text-white">
              <h5 class="modal-title user-select-none">{{ $t("modal.delete.title") }}</h5>
              <button @click="show = false" type="button" class="btn-close text-white" aria-label="Close">
                <span aria-hidden="true"></span>
              </button>
            </div>
            <div class="modal-body">
              <span>
                {{ $t("modal.delete.main-pre") }} <strong>{{ $t("modal.delete.main-center") }}</strong>
                {{ $t("modal.delete.main-post") }}
              </span>
            </div>

            <div class="modal-footer">
              <button @click="handleConfirm()" type="button" class="btn btn-danger">
                {{ $t("modal.delete.confirm") }}
              </button>
              <button @click="show = false" type="button" class="btn btn-info" data-dismiss="modal">
                {{ $t("modal.delete.abort") }}
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
import { ref } from "vue";

const emit = defineEmits(["confirmedDeletion"]);
defineExpose({ doShow });

const show = ref(false);

function doShow() {
  show.value = true;
}

function handleConfirm() {
  emit("confirmedDeletion");
  show.value = false;
}
</script>
