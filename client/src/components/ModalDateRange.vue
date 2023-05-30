<template>
  <Transition>
    <div v-if="show">
      <div @click="show = false" class="modal modal-lg show" role="dialog" style="display: block">
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

              <!-- Tab view -->
              <ul class="nav nav-tabs" role="tablist">
                <li class="nav-item" role="presentation">
                  <a class="nav-link active" data-bs-toggle="tab" href="#date" aria-selected="true" role="tab"
                    >Date range</a
                  >
                </li>
                <li class="nav-item" role="presentation">
                  <a class="nav-link" data-bs-toggle="tab" href="#time" aria-selected="false" role="tab" tabindex="-1"
                    >Times for each day</a
                  >
                </li>
              </ul>
              <div id="myTabContent" class="tab-content">
                <!-- Date range tab -->
                <div class="tab-pane fade active show mt-2" id="date" role="tabpanel">
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
                </div>

                <!-- Time for each day -->
                <div class="tab-pane fade mt-2" id="time" role="tabpanel">
                  <div class="d-flex flex-row">
                    <button @click="newOpt(numOpts)" type="button" class="control-btn col btn btn-success">
                      ✚ New Time
                    </button>
                    <button
                      @click="
                        times = [];
                        counter = 6;
                      "
                      type="button"
                      class="control-btn col btn btn-danger"
                    >
                      🗑 Clear all times
                    </button>
                  </div>

                  <!--  - Option list -->
                  <div>
                    <table class="table table-hover table-striped">
                      <thead>
                        <tr>
                          <!--<th scope="col">#</th>-->
                          <th />
                          <th scope="col" class="user-select-none" style="width: 100%">Time</th>
                          <th scope="col" class="user-select-none" style="text-align: right">Controls</th>
                        </tr>
                      </thead>
                      <tr v-if="numOpts == 0">
                        <td class="user-select-none text-invisible fs-4">---</td>
                        <td>
                          <span class="user-select-none text-muted">No times yet...</span>
                        </td>
                      </tr>
                      <draggable
                        v-model="times"
                        tag="tbody"
                        handle=".editor-drag-handle"
                        item-key="index"
                        @start="onDragStart()"
                        @end="onDragEnd()"
                      >
                        <template #item="{ element }">
                          <tr>
                            <!--<th scope="row">{{ element.index }}</th>-->
                            <td class="editor-drag-handle">⥮</td>
                            <td>
                              <input
                                v-model="element.name"
                                type="text"
                                class="form-control"
                                :class="{ 'is-invalid': element.name.length <= 0 }"
                                :maxlength="8"
                                style="z-index: 1000000"
                                placeholder="Time..."
                              />
                            </td>

                            <td>
                              <div class="btn-group-container">
                                <div class="btn-group control-btn" role="group" aria-label="Basic example">
                                  <button @click="moveOptAbs(element, 0)" type="button" :class="clsBtnUp(element)">
                                    ⇈
                                  </button>
                                  <button @click="moveOptRel(element, -1)" type="button" :class="clsBtnUp(element)">
                                    ↿
                                  </button>
                                  <button @click="moveOptRel(element, 1)" type="button" :class="clsBtnDown(element)">
                                    ⇂
                                  </button>
                                  <button
                                    @click="moveOptAbs(element, numOpts - 1)"
                                    type="button"
                                    :class="clsBtnDown(element)"
                                  >
                                    ⇊
                                  </button>
                                </div>
                                <div class="btn-group control-btn" role="group" aria-label="Basic example">
                                  <button @click="newOptAfter(element)" type="button" :class="clsBtn('success')">
                                    ✚
                                  </button>
                                  <button @click="delOpt(element)" type="button" :class="clsBtn('danger')">🗑</button>
                                </div>
                              </div>
                            </td>
                          </tr>
                        </template>
                      </draggable>
                    </table>
                  </div>
                </div>
              </div>

              <!-- Misc. options -->
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
import draggable from "vuedraggable";
import { defineComponent, ref } from "vue";
import Datepicker from "@vuepic/vue-datepicker";
import { eachDayOfInterval, format } from "date-fns";
import { Option } from "@/model";

export default defineComponent({
  components: {
    Datepicker,
    draggable,
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

      drag: false,
      counter: 6,
      times: [] as Option[],
    };
  },

  computed: {
    realFormatStr() {
      return this.includeYear ? this.formatStr : this.formatStrNoYear;
    },

    numOpts() {
      return this.times.length;
    },
  },

  methods: {
    doShow() {
      this.show = true;
      this.dateRange = null;
      this.includeYear = true;
      this.counter = 6;
      this.times = [];
    },

    handleConfirm() {
      if (this.dateRange == null) {
        return;
      }
      const res = eachDayOfInterval({ start: this.dateRange[0], end: this.dateRange[1] });
      const resStr: string[] = [];
      for (const date of res) {
        const dateStr = format(date, this.realFormatStr);
        if (this.times.length == 0) {
          resStr.push(dateStr);
        }

        // const brOnlyStr = dateStr.replace(/(<br>)|./gs, "$1");
        const brOnlyStr = "<m>" + dateStr + "</m>";
        for (let idx = 0; idx < this.times.length; ++idx) {
          const t = this.times[idx];
          resStr.push((idx == 0 ? dateStr : brOnlyStr) + "<br>" + t.name);
        }
      }
      this.$emit("rangeSelected", resStr);
      this.show = false;
    },

    newOptAfter(opt: Option) {
      this.newOpt(opt.index + 1);
    },

    newOpt(idx: number) {
      this.times.splice(idx, 0, new Option("*" + (this.counter++ % 24) + ":00*", -1));
      this.optionChangeFixup();
    },

    delOpt(opt: Option) {
      const idx = opt.index;
      this.times.splice(idx, 1);
      this.optionChangeFixup();
    },

    moveOptRel(opt: Option, diff: number) {
      this.moveOptAbs(opt, opt.index + diff);
    },

    moveOptAbs(opt: Option, to: number) {
      const from = opt.index;
      const el = this.times[from];
      this.times.splice(from, 1);
      this.times.splice(to, 0, el);
      this.optionChangeFixup();
    },

    onDragStart() {
      this.drag = true;
    },

    onDragEnd() {
      this.drag = false;
      this.optionChangeFixup();
    },

    clsBtnUp(opt: Option, type = "primary") {
      return {
        ...this.clsBtn(type),
        disabled: this.drag || opt.index <= 0,
      };
    },

    clsBtnDown(opt: Option, type = "primary") {
      return {
        ...this.clsBtn(type),
        disabled: this.drag || opt.index >= this.times.length - 1,
      };
    },

    clsBtn(type = "primary") {
      return {
        btn: true,
        "btn-danger": type == "danger",
        "btn-success": type == "success",
        "btn-primary": type == "primary",
        disabled: this.drag,
      };
    },

    optionChangeFixup() {
      for (let i = 0; i < this.times.length; ++i) {
        this.times[i].index = i;
      }
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
