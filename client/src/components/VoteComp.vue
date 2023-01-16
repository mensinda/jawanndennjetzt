<template>
  <div class="rounded-1 vote-container" :class="containerCls">
    <div
      class="ballot-box"
      :class="btnBoxCls"
      @click="handleClick(false)"
      @contextmenu.prevent="handleClick(true)"
      v-html="symbol"
    />
  </div>
</template>

<script lang="ts">
import { Vote } from "@/model";
import { defineComponent } from "vue";

export default defineComponent({
  props: {
    vote: Vote,
    highlight: {
      type: Boolean,
      default: false,
    },
    editable: {
      type: Boolean,
      default: false,
    },
  },

  emits: ["onChange"],

  data() {
    return {
      realVote: null as Vote | null,
    };
  },

  mounted() {
    if (this.vote == null) {
      return;
    }
    this.realVote = this.vote;
  },

  methods: {
    handleClick(reverse: boolean) {
      if (!this.editable || this.realVote == null) {
        return;
      }
      this.realVote.cycle(reverse);
      this.$emit("onChange");
    },
  },

  computed: {
    bgCls() {
      if (this.realVote == null) {
        return {};
      }
      switch (this.realVote.status) {
        case "Y":
          return { "bg-success": true };
        case "N":
          return { "bg-danger": true };
        case "M":
          return { "bg-warning": true };
        case "-":
          return { "bg-secondary": true };
        default:
          throw new Error("Unknown status: " + this.realVote.status);
      }
    },

    containerCls() {
      return {
        ...this.bgCls,
        "vote-container-active": this.editable && !this.highlight,
        "vote-container-inactive": !this.editable && !this.highlight,
        "vote-container-highlight": this.highlight,
      };
    },

    btnBoxCls() {
      return {
        ...this.bgCls,
        "ballot-box-active": this.editable,
        "ballot-box-inactive": !this.editable,
      };
    },

    symbol() {
      if (this.realVote == null) {
        return {};
      }
      switch (this.realVote.status) {
        case "Y":
          return "<b>🗸</b>";
        case "N":
          return "🗴";
        case "M":
          return "<b>?</b>";
        case "-":
          return "";
        default:
          throw new Error("Unknown status: " + this.realVote.status);
      }
    },
  },
});
</script>

<style lang="scss">
.vote-container {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
  height: 100%;
  text-align: center;
  user-select: none;
  transition: 0.3s;
}

.vote-container-inactive {
  --bs-bg-opacity: 0.3 !important;
}

.vote-container-active {
  --bs-bg-opacity: 0.5 !important;
}

.vote-container-highlight {
  --bs-bg-opacity: 1 !important;
}

.ballot-box {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 33px;
  height: 33px;
  color: rgba(0, 0, 0, 0.85);
  font-size: x-large;
  transition: 0.3s;
}

.ballot-box-inactive {
  --bs-bg-opacity: 0 !important;
}

.ballot-box-active {
  --bs-bg-opacity: 1 !important;
  cursor: pointer;

  border-color: black;
  border-style: solid;
  border-width: 2px;
  border-radius: 8px;
}

.ballot-box-active:hover {
  --bs-bg-opacity: 0.75 !important;
}
</style>
