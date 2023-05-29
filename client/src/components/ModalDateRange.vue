<template>
  <Transition>
    <div v-if="show">
      <div @click="show = false" class="modal show" role="dialog" style="display: block">
        <div @click.stop="stop" class="modal-dialog" role="document">
          <div class="modal-content">
            <div class="modal-header bg-info fw-bold text-white">
              <h5 class="modal-title">Date range inserter</h5>
              <button @click="show = false" type="button" class="btn-close" aria-label="Close">
                <span aria-hidden="true"></span>
              </button>
            </div>
            <div class="modal-body">
              <p>Please select the date range to append to the options</p>
              <div class="picker-parent">
                <Datepicker
                  v-model="dateRange"
                  range
                  inline
                  style="width: auto !important"
                  :partial-range="false"
                  :max-range="64"
                  :hide-navigation="['time']"
                  :enable-time-picker="false"
                  :auto-apply="true"
                  format="dd.MM.yyyy"
                />
              </div>
              <div class="form-check mt-3">
                <input class="form-check-input" type="checkbox" id="yearCheckBox" v-model="includeYear" />
                <label class="form-check-label" for="yearCheckBox">Include the year in the generated options</label>
              </div>
            </div>
            <div class="modal-footer">
              <button
                @click="handleConfirm()"
                type="button"
                class="btn btn-primary"
                :class="{ disabled: dateRange == null }"
              >
                Save changes
              </button>
              <button @click="show = false" type="button" class="btn btn-secondary" data-dismiss="modal">Close</button>
            </div>
          </div>
        </div>
      </div>
      <div @click="show = false" class="modal-backdrop show" id="backdrop" style="display: block"></div>
    </div>
  </Transition>
</template>

<script lang="ts">
import { defineComponent, ref } from "vue";
import Datepicker from "@vuepic/vue-datepicker";
import { eachDayOfInterval, format } from "date-fns";

export default defineComponent({
  components: {
    Datepicker,
  },

  emits: ["rangeSelected"],

  props: {
    formatStr: {
      default: "dd.MM.yyyy",
    },
    formatStrNoYear: {
      default: "dd.MM",
    },
  },

  data() {
    return {
      show: false,
      dateRange: ref(),
      includeYear: true,
    };
  },

  computed: {
    realFormatStr() {
      return this.includeYear ? this.formatStr : this.formatStrNoYear;
    },
  },

  methods: {
    doShow() {
      this.show = true;
      this.dateRange = null;
      this.includeYear = true;
    },

    handleConfirm() {
      if (this.dateRange == null) {
        return;
      }
      const res = eachDayOfInterval({ start: this.dateRange[0], end: this.dateRange[1] });
      const resStr = res.map((x) => format(x, this.realFormatStr));
      this.$emit("rangeSelected", resStr);
      this.show = false;
    },
  },
});
</script>

<style lang="scss">
.picker-parent {
  width: 100%;
  display: flex;
  justify-content: center;
}
</style>
