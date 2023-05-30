<template>
  <Transition>
    <div v-if="show">
      <div @click="show = false" class="modal show" role="dialog" style="display: block">
        <div @click.stop="stop" class="modal-dialog" role="document">
          <div class="modal-content">
            <div class="modal-header bg-danger fw-bold text-white">
              <h5 class="modal-title"><b>An error occurred!</b></h5>
              <button @click="show = false" type="button" class="btn-close" aria-label="Close">
                <span aria-hidden="true"></span>
              </button>
            </div>
            <div class="modal-body d-flex flex-column">
              <p>
                Error code: <b>{{ data.code }}</b>
              </p>
              <code class="mb-3">{{ data.msg }}</code>
              <span class="text-center w-100">Please contact the site administrator</span>
            </div>
            <div class="modal-footer">
              <button @click="show = false" type="button" class="btn btn-danger" data-dismiss="modal">Close</button>
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

export default defineComponent({
  data(): {
    show: boolean;
    data: {
      msg: string;
      code: string;
    };
  } {
    return {
      show: false,
      data: {
        msg: "",
        code: "",
      },
    };
  },

  mounted(): void {
    this.show = false;
  },

  methods: {
    doShow(): void {
      this.show = true;
    },

    updateData(data: { msg: string; code: string }) {
      this.data = data;
    },
  },

  computed: {},
});
</script>
