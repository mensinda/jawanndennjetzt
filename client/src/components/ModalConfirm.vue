<template>
  <Transition>
    <div v-if="show">
      <div @click="show = false" class="modal modal-lg show" role="dialog" style="display: block">
        <div @click.stop="stop" class="modal-dialog" role="document">
          <div class="modal-content">
            <div class="modal-header bg-danger fw-bold text-white">
              <h5 class="modal-title user-select-none">Delete poll</h5>
              <button @click="show = false" type="button" class="btn-close text-white" aria-label="Close">
                <span aria-hidden="true"></span>
              </button>
            </div>
            <div class="modal-body">
              <span>Are you sure you want to <strong>PERMANENTLY</strong> delete this poll?</span>
            </div>

            <div class="modal-footer">
              <button @click="handleConfirm()" type="button" class="btn btn-danger">Confirm Deletion</button>
              <button @click="show = false" type="button" class="btn btn-info" data-dismiss="modal">Abort</button>
            </div>
          </div>
        </div>
      </div>
      <div @click="show = false" class="modal-backdrop show" id="backdrop" style="display: block"></div>
    </div>
  </Transition>
</template>

<script lang="ts">
import { defineComponent } from "vue";
import { markdown } from "@/util";

export default defineComponent({
  emits: ["confirmedDeletion"],

  data() {
    return {
      show: false,
    };
  },

  methods: {
    doShow() {
      this.show = true;
    },

    markdown,

    handleConfirm() {
      this.$emit("confirmedDeletion");
      this.show = false;
    },
  },
});
</script>
