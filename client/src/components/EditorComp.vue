<template>
  <ModalDateRange ref="rangeModal" format-str="EEEEEE'<br>**'dd.MM'**<br>'yyyy" @rangeSelected="insertDateRange" />
  <!-- Name, description, and settings -->
  <div class="card mb-3">
    <label class="card-header">General settings</label>
    <div class="card-body">
      <div class="mb-2">
        <label class="fw-bold user-select-none">Poll name</label>
        <input
          v-model="store.name"
          type="text"
          class="form-control"
          :class="{ 'is-invalid': hasChanges && store.name.length <= 0 }"
          :maxlength="limits.TITLE_LENGTH"
          placeholder="New poll name..."
          @input="hasChanges = true"
        />
        <small class="form-text text-muted user-select-none">
          The name of the poll to create. Markdown syntax is supported.
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
        <label class="form-check-label user-select-none" for="allowCbId"> Allow leaving options unanswered</label>
      </div>

      <hr />

      <label class="fw-bold mb-2 user-select-none">Poll description</label>
      <ul class="nav nav-tabs" role="tablist">
        <li class="nav-item" role="presentation">
          <a class="nav-link active" data-bs-toggle="tab" href="#note-edit" aria-selected="true" role="tab"> Edit </a>
        </li>
        <li class="nav-item" role="presentation">
          <a class="nav-link" data-bs-toggle="tab" href="#note-preview" aria-selected="false" role="tab">Preview</a>
        </li>
      </ul>
      <div id="noteIdContainer" class="tab-content">
        <div class="tab-pane fade active show" id="note-edit" role="tabpanel">
          <textarea
            v-model="store.description"
            rows="4"
            class="form-control mt-1"
            placeholder="An optional descriptive text..."
            @input="hasChanges = true"
          />
          <small class="form-text text-muted user-select-none"
            >Optional description. Markdown syntax is supported.</small
          >
        </div>
        <div class="tab-pane fade card mt-1 mb-2" id="note-preview" role="tabpanel">
          <div class="card-body">
            <div
              class="card-text remove-last-margin"
              :class="{
                'text-muted user-select-none': !store.description.trim(),
              }"
              v-html="markdown(store.description.trim() ? store.description : '*Nothing to preview*')"
            />
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- Options card -->
  <div class="card mb-3" v-if="canEditOptions">
    <label class="card-header">Options</label>

    <!--  - Options buttons -->
    <div class="card-body">
      <div class="mb-3">
        <div class="d-flex flex-row">
          <button @click="newOpt(numOpts)" type="button" class="control-btn col btn btn-success">✚ New option</button>
          <button @click="dateRange()" type="button" class="control-btn col btn btn-primary">
            📅 Insert date range
          </button>
          <button
            @click="
              store.options = [];
              store.ballots = [];
              counter = 1;
              hasChanges = true;
            "
            type="button"
            class="control-btn col btn btn-danger"
          >
            🗑 Clear all options
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
              <th scope="col" class="user-select-none" style="width: 100%">Option name</th>
              <th scope="col" class="user-select-none" style="text-align: right">Controls</th>
            </tr>
          </thead>
          <tr v-if="numOpts == 0">
            <td class="user-select-none text-invisible fs-4">---</td>
            <td>
              <span class="user-select-none text-muted">No options yet...</span>
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
                    :maxlength="limits.NAME_LENGTH"
                    style="z-index: 1000000"
                    placeholder="Option name..."
                    @input="hasChanges = true"
                  />
                </td>

                <td>
                  <div class="btn-group-container">
                    <div class="btn-group control-btn" role="group" aria-label="Basic example">
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
    <div v-if="!canSubmit && hasChanges" class="card text-white mb-2">
      <label class="card-header bg-danger">Unable to submit because:</label>
      <div class="card-body bg-danger" style="--bs-bg-opacity: 0.9">
        <ul class="mb-0">
          <li v-if="store.name.length <= 0">The poll does not have a name!</li>
          <li v-if="store.options.length <= 0">There are no poll options!</li>
          <li v-if="hasEmptyOption">At least one option has no name!</li>
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

<script lang="ts">
import draggable from "vuedraggable";
import { marked } from "marked";
import { sanitize } from "dompurify";
import { defineComponent, ref } from "vue";
import { pollStore } from "@/store";
import { Option } from "@/model";
import { RandomPoll } from "@/randomPoll";
import { LIMITS } from "@/limits";
import ModalDateRange from "./ModalDateRange.vue";

export default defineComponent({
  components: {
    draggable,
    ModalDateRange,
  },

  props: {
    submitMsg: {
      type: String,
    },
    canEditOptions: {
      type: Boolean,
    },
  },

  emits: ["submit"],

  setup() {
    const store = pollStore();
    const rangeModal = ref<typeof ModalDateRange | null>(null);
    const randomPoll = new RandomPoll(false);

    return { store, rangeModal, randomPoll };
  },

  data() {
    return {
      drag: false,
      date: ref(),
      counter: 1,
      hasChanges: false,
    };
  },

  mounted() {
    this.counter = 1;
  },

  methods: {
    markdown(raw: string): string {
      return sanitize(marked.parse(raw, { gfm: true }), { USE_PROFILES: { html: true } });
    },

    newOptAfter(opt: Option) {
      this.newOpt(opt.index + 1);
    },

    newOpt(idx: number) {
      this.store.options.splice(idx, 0, new Option("#" + this.counter++, -1));
      this.optionChangeFixup();
    },

    delOpt(opt: Option) {
      const idx = opt.index;
      this.store.options.splice(idx, 1);
      this.optionChangeFixup();
      this.counter--;
    },

    dateRange() {
      if (this.rangeModal == null) {
        return;
      }
      this.rangeModal.doShow();
    },

    insertDateRange(r: string[]) {
      r.forEach((x) => this.store.options.push(new Option(x, -1)));
      this.optionChangeFixup();
    },

    moveOptRel(opt: Option, diff: number) {
      this.moveOptAbs(opt, opt.index + diff);
    },

    moveOptAbs(opt: Option, to: number) {
      const from = opt.index;
      const el = this.store.options[from];
      this.store.options.splice(from, 1);
      this.store.options.splice(to, 0, el);
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
        disabled: this.drag || opt.index >= this.store.options.length - 1,
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
      this.store.idx_autofix();
      this.store.ballots = this.randomPoll.ballots(this.store.options.length);
      this.hasChanges = true;
    },
  },

  computed: {
    numOpts(): number {
      return this.store.options.length;
    },

    submitBtnCls() {
      return {
        btn: true,
        "btn-lg": true,
        "mb-1": true,
        "btn-success": this.canSubmit,
        "btn-secondary": !this.canSubmit,
        disabled: !this.canSubmit || !this.hasChanges,
        "control-btn": true,
        col: true,
      };
    },

    canSubmit() {
      return this.store.options.length > 0 && this.store.name.length > 0 && !this.hasEmptyOption;
    },

    hasEmptyOption() {
      for (const x of this.store.options) {
        if (x.name.length <= 0) {
          return true;
        }
      }
      return false;
    },

    limits() {
      return LIMITS;
    },
  },
});
</script>

<style lang="scss">
@import "@/theme.scss";
@import "node_modules/@vuepic/vue-datepicker/src/VueDatePicker/style/main.scss";

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
</style>
