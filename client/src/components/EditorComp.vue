<template>
  <ModalDateRange
    ref="rangeModal"
    formatStr="EEEEEE'<br>**'dd.MM'**<br>'yyyy"
    formatStrNoYear="EEEEEE'<br>**'dd.MM'**'"
    @rangeSelected="insertDateRange"
  />
  <!-- Name, description, and settings -->
  <div class="card mb-3">
    <label class="card-header">{{ $t("editor.general-settings") }}</label>
    <div class="card-body">
      <div class="mb-2">
        <label class="fw-bold user-select-none">{{ $t("editor.poll-name") }}</label>
        <input
          v-model="store.name"
          type="text"
          class="form-control"
          :class="{ 'is-invalid': hasChanges && store.name.length <= 0 }"
          :maxlength="LIMITS.TITLE_LENGTH"
          :placeholder="$t('editor.poll-name-placeholder')"
          @input="hasChanges = true"
        />
        <small class="form-text text-muted user-select-none">
          {{ $t("editor.poll-name-hint") }}
        </small>
      </div>
      <div class="form-check mb-3">
        <input
          v-model="store.allowNotVoted"
          @change="hasChanges = true"
          class="form-check-input"
          type="checkbox"
          id="allowCbId"
        />
        <label class="form-check-label user-select-none" for="allowCbId"> {{ $t("editor.allow-unansered") }}</label>
      </div>

      <hr />

      <label class="fw-bold mb-2 user-select-none">{{ $t("editor.poll-description") }}</label>
      <ul class="nav nav-tabs" role="tablist">
        <li class="nav-item" role="presentation">
          <a class="nav-link active" data-bs-toggle="tab" href="#note-edit" aria-selected="true" role="tab">
            {{ $t("editor.edit") }}
          </a>
        </li>
        <li class="nav-item" role="presentation">
          <a class="nav-link" data-bs-toggle="tab" href="#note-preview" aria-selected="false" role="tab">{{
            $t("editor.preview")
          }}</a>
        </li>
      </ul>
      <div id="noteIdContainer" class="tab-content">
        <div class="tab-pane fade active show" id="note-edit" role="tabpanel">
          <textarea
            v-model="store.description"
            rows="4"
            class="form-control mt-1"
            :placeholder="$t('editor.desc-placeholder-2')"
            @input="hasChanges = true"
          />
          <small class="form-text text-muted user-select-none">
            {{ $t("editor.desc-placeholder") }}
          </small>
        </div>
        <div class="tab-pane fade card mt-1 mb-2" id="note-preview" role="tabpanel">
          <div class="card-body">
            <div
              class="card-text remove-last-margin"
              :class="{
                'text-muted user-select-none': !store.description.trim(),
              }"
              v-html="markdown(store.description.trim() ? store.description : $t('editor.nothing-to-preview'))"
            />
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- Options card -->
  <div class="card mb-3" v-if="canEditOptions">
    <label class="card-header">{{ $t("editor.options") }}</label>

    <!--  - Options buttons -->
    <div class="card-body">
      <div class="mb-3">
        <div class="editor-button-row">
          <button @click="newOpt(numOpts)" type="button" class="control-btn btn btn-success">
            {{ $t("editor.new-option") }}
          </button>
          <button @click="dateRange()" type="button" class="control-btn btn btn-primary">
            {{ $t("editor.insert-date-range") }}
          </button>
          <button
            @click="
              store.options = [];
              store.ballots = [];
              counter = 1;
              hasChanges = true;
            "
            type="button"
            class="control-btn btn btn-danger"
          >
            {{ $t("editor.clear-all-options") }}
          </button>
        </div>
      </div>

      <!--  - Option list -->
      <div>
        <table class="table table-hover table-striped">
          <thead>
            <tr>
              <!--<th scope="col">#</th>-->
              <th />
              <th scope="col" class="user-select-none" style="width: 100%">{{ $t("editor.option-name") }}</th>
              <th scope="col" class="user-select-none" style="text-align: right">{{ $t("editor.controls") }}</th>
            </tr>
          </thead>
          <tr v-if="numOpts == 0">
            <td class="user-select-none text-invisible fs-4">---</td>
            <td>
              <span class="user-select-none text-muted">{{ $t("editor.no-options-yet") }}</span>
            </td>
          </tr>
          <draggable
            v-model="store.options"
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
                    :maxlength="LIMITS.NAME_LENGTH"
                    style="z-index: 1000000"
                    :placeholder="$t('editor.option-name-placeholder')"
                    @input="hasChanges = true"
                  />
                </td>

                <td>
                  <div class="btn-group-container">
                    <div class="btn-group control-btn edit-move-btns" role="group" aria-label="Basic example">
                      <button @click="moveOptAbs(element, 0)" type="button" :class="clsBtnUp(element)">⇈</button>
                      <button @click="moveOptRel(element, -1)" type="button" :class="clsBtnUp(element)">↿</button>
                      <button @click="moveOptRel(element, 1)" type="button" :class="clsBtnDown(element)">⇂</button>
                      <button @click="moveOptAbs(element, numOpts - 1)" type="button" :class="clsBtnDown(element)">
                        ⇊
                      </button>
                    </div>
                    <div class="btn-group control-btn" role="group" aria-label="Basic example">
                      <button @click="newOptAfter(element)" type="button" :class="clsBtn('success')">✚</button>
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

  <!-- Submitting -->
  <div class="mb-3">
    <div v-if="!canSubmit && hasChanges" class="card mb-2">
      <label class="card-header text-white bg-danger">{{ $t("editor.unable-to-submit") }}</label>
      <div class="card-body bg-danger" style="--bs-bg-opacity: 0.15">
        <ul class="mb-0">
          <li v-if="store.name.length <= 0">{{ $t("editor.poll-no-name") }}</li>
          <li v-if="store.options.length <= 0">{{ $t("editor.poll-no-options") }}</li>
          <li v-if="hasEmptyOption">{{ $t("editor.poll-empty-option") }}</li>
        </ul>
      </div>
    </div>
    <div class="d-flex flex-row">
      <button @click="$emit('submit')" :class="submitBtnCls" type="button">
        {{ submitMsg }}
      </button>
    </div>
  </div>
</template>

<script lang="ts" setup>
import draggable from "vuedraggable";
import { ref, computed, onMounted } from "vue";
import { pollStore } from "@/store";
import { Option } from "@/model";
import { RandomPoll } from "@/randomPoll";
import { LIMITS } from "@/limits";
import { markdown } from "@/util";
import { JWDJ_PRIMARY_BTN_CLS } from "@/config";
import ModalDateRange from "./ModalDateRange.vue";
import "@vuepic/vue-datepicker/dist/main.css";

defineEmits(["submit"]);
defineExpose({ optionsImported });

defineProps({
  submitMsg: {
    type: String,
  },
  canEditOptions: {
    type: Boolean,
  },
});

const store = pollStore();
const rangeModal = ref<typeof ModalDateRange | null>(null);
const randomPoll = new RandomPoll(false);

const drag = ref(false);
const counter = ref(1);
const hasChanges = ref(false);

onMounted(() => (counter.value = 1));

const numOpts = computed(() => store.options.length);

const submitBtnCls = computed(() => {
  return {
    btn: true,
    "btn-lg": true,
    "mb-1": true,
    [JWDJ_PRIMARY_BTN_CLS]: canSubmit.value,
    "btn-secondary": !canSubmit.value,
    disabled: !canSubmit.value || !hasChanges.value,
    "control-btn": true,
    col: true,
  };
});

const canSubmit = computed(() => store.options.length > 0 && store.name.length > 0 && !hasEmptyOption.value);

const hasEmptyOption = computed(() => {
  for (const x of store.options) {
    if (x.name.length <= 0) {
      return true;
    }
  }
  return false;
});

function newOptAfter(opt: Option) {
  newOpt(opt.index + 1);
}

function newOpt(idx: number) {
  store.options.splice(idx, 0, new Option("#" + counter.value++, -1));
  optionChangeFixup();
}

function delOpt(opt: Option) {
  const idx = opt.index;
  store.options.splice(idx, 1);
  optionChangeFixup();
  counter.value--;
}

function dateRange() {
  if (rangeModal.value == null) {
    return;
  }
  rangeModal.value.doShow();
}

function insertDateRange(r: string[]) {
  r.forEach((x) => store.options.push(new Option(x, -1)));
  optionChangeFixup();
}

function moveOptRel(opt: Option, diff: number) {
  moveOptAbs(opt, opt.index + diff);
}

function moveOptAbs(opt: Option, to: number) {
  const from = opt.index;
  const el = store.options[from];
  store.options.splice(from, 1);
  store.options.splice(to, 0, el);
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
    disabled: drag.value || opt.index >= store.options.length - 1,
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
  store.idx_autofix();
  store.ballots = randomPoll.ballots(store.options.length);
  hasChanges.value = true;
}

function optionsImported() {
  counter.value = store.options.length + 1;

  if (store.options.length > 0) {
    optionChangeFixup();
  }
}
</script>

<style lang="scss">
@import "@/theme.scss";

.control-btn {
  margin: 0 ($spacer * 0.25);
}

.control-btn:first-of-type {
  margin-left: 0;
}

.control-btn:last-of-type {
  margin-right: 0;
}

.btn-group-container {
  display: flex;
  flex-direction: row;
}

.editor-drag-handle {
  cursor: grab;
  font-size: x-large;
  text-align: center;
  vertical-align: middle;
}

.editor-button-row {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 0.5rem;
  @media screen and (max-width: 800px) {
    grid-template-columns: 1fr;
  }
}

.editor-button-row button {
  margin: 0;
}

.edit-move-btns {
  @media screen and (max-width: 800px) {
    display: none;
    margin: 0;
  }
}
</style>
