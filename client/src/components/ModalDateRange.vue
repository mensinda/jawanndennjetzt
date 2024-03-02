<template>
  <div v-if="show">
    <div @click="show = false" class="modal modal-lg show" role="dialog" style="display: block">
      <div @click.stop="() => {}" class="modal-dialog" role="document">
        <div class="modal-content">
          <div class="modal-header bg-info fw-bold text-white">
            <h5 class="modal-title">{{ $t("modal.date.title") }}</h5>
            <button @click="show = false" type="button" class="btn-close" aria-label="Close">
              <span aria-hidden="true"></span>
            </button>
          </div>
          <div class="modal-body">
            <p>{{ $t("modal.date.desc") }}</p>

            <!-- Tab view -->
            <ul class="nav nav-tabs" role="tablist">
              <li class="nav-item" role="presentation">
                <a class="nav-link active" data-bs-toggle="tab" href="#date" aria-selected="true" role="tab">
                  {{ $t("modal.date.tab-date") }}
                </a>
              </li>
              <li class="nav-item" role="presentation">
                <a class="nav-link" data-bs-toggle="tab" href="#time" aria-selected="false" role="tab" tabindex="-1">
                  {{ $t("modal.date.tab-time") }}
                </a>
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
                    :dark="JWDJ_DARK_DATE_PICKER"
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
                    {{ $t("modal.date.new-time") }}
                  </button>
                  <button
                    @click="
                      times = [];
                      counter = 6;
                    "
                    type="button"
                    class="control-btn col btn btn-danger"
                  >
                    {{ $t("modal.date.clear-all-times") }}
                  </button>
                </div>

                <!--  - Option list -->
                <div>
                  <table class="table table-hover table-striped">
                    <thead>
                      <tr>
                        <!--<th scope="col">#</th>-->
                        <th />
                        <th scope="col" class="user-select-none" style="width: 100%">{{ $t("modal.date.time") }}</th>
                        <th scope="col" class="user-select-none" style="text-align: right">
                          {{ $t("modal.date.controls") }}
                        </th>
                      </tr>
                    </thead>
                    <tr v-if="numOpts == 0">
                      <td class="user-select-none text-invisible fs-4">---</td>
                      <td>
                        <span class="user-select-none text-muted">{{ $t("modal.date.no-times-yet") }}</span>
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
                              :maxlength="24"
                              style="z-index: 1000000"
                              placeholder="Time..."
                            />
                          </td>

                          <td>
                            <div class="btn-group-container">
                              <div class="btn-group control-btn edit-move-btns" role="group" aria-label="Basic example">
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
              <label class="form-check-label" for="yearCheckBox">{{ $t("modal.date.include-year") }}</label>
            </div>
          </div>
          <div class="modal-footer">
            <button
              @click="handleConfirm()"
              type="button"
              class="btn btn-primary"
              :class="{ disabled: dateRange == null }"
            >
              {{ $t("modal.date.save-changes") }}
            </button>
            <button @click="show = false" type="button" class="btn btn-secondary" data-dismiss="modal">
              {{ $t("common.close") }}
            </button>
          </div>
        </div>
      </div>
    </div>
    <div @click="show = false" class="modal-backdrop show" id="backdrop" style="display: block"></div>
  </div>
</template>

<script lang="ts" setup>
import draggable from "vuedraggable";
import { ref, computed } from "vue";
import Datepicker from "@vuepic/vue-datepicker";
import { eachDayOfInterval, format } from "date-fns";
import { de, enGB } from "date-fns/locale";
import { getLocaleTag } from "@/locales";
import { Option } from "@/model";
import { JWDJ_DARK_DATE_PICKER } from "@/config";

const emit = defineEmits(["rangeSelected"]);
defineExpose({ doShow });

const props = defineProps({
  formatStr: {
    default: "dd.MM.yyyy",
  },
  formatStrNoYear: {
    default: "dd.MM",
  },
});

const show = ref(false);
const dateRange = ref();
const includeYear = ref(true);

const drag = ref(false);
const counter = ref(6);
const times = ref<Option[]>([]);

const realFormatStr = computed(() => (includeYear.value ? props.formatStr : props.formatStrNoYear));
const numOpts = computed(() => times.value.length);

function doShow() {
  show.value = true;
  dateRange.value = null;
  includeYear.value = true;
  counter.value = 6;
  times.value = [];
}

function localeTagToLocale() {
  switch (getLocaleTag()) {
    case "de":
    case "de-DE":
      return de;
    default:
      return enGB;
  }
}

async function handleConfirm() {
  if (dateRange.value == null) {
    return;
  }
  const res = eachDayOfInterval({ start: dateRange.value[0], end: dateRange.value[1] });
  const resStr: string[] = [];
  for (const date of res) {
    const dateStr = format(date, realFormatStr.value, { locale: localeTagToLocale() });
    if (times.value.length == 0) {
      resStr.push(dateStr);
    }

    // const brOnlyStr = dateStr.replace(/(<br>)|./gs, "$1");
    const brOnlyStr = "<m>" + dateStr + "</m>";
    for (let idx = 0; idx < times.value.length; ++idx) {
      const t = times.value[idx];
      resStr.push((idx == 0 ? dateStr : brOnlyStr) + "<br>" + t.name);
    }
  }
  emit("rangeSelected", resStr);
  show.value = false;
}

function newOptAfter(opt: Option) {
  newOpt(opt.index + 1);
}

function newOpt(idx: number) {
  times.value.splice(idx, 0, new Option("*" + (counter.value++ % 24) + ":00*", -1));
  optionChangeFixup();
}

function delOpt(opt: Option) {
  const idx = opt.index;
  times.value.splice(idx, 1);
  optionChangeFixup();
}

function moveOptRel(opt: Option, diff: number) {
  moveOptAbs(opt, opt.index + diff);
}

function moveOptAbs(opt: Option, to: number) {
  const from = opt.index;
  const el = times.value[from];
  times.value.splice(from, 1);
  times.value.splice(to, 0, el);
  optionChangeFixup();
}

function onDragStart() {
  drag.value = true;
}

function onDragEnd() {
  drag.value = false;
  optionChangeFixup();
}

function clsBtnUp(opt: Option, type = "primary") {
  return {
    ...clsBtn(type),
    disabled: drag.value || opt.index <= 0,
  };
}

function clsBtnDown(opt: Option, type = "primary") {
  return {
    ...clsBtn(type),
    disabled: drag.value || opt.index >= times.value.length - 1,
  };
}

function clsBtn(type = "primary") {
  return {
    btn: true,
    "btn-danger": type == "danger",
    "btn-success": type == "success",
    "btn-primary": type == "primary",
    disabled: drag.value,
  };
}

function optionChangeFixup() {
  for (let i = 0; i < times.value.length; ++i) {
    times.value[i].index = i;
  }
}
</script>

<style lang="scss">
.picker-parent {
  width: 100%;
  display: flex;
  justify-content: center;
}
</style>
