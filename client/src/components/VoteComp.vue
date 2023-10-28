<template>
  <div class="rounded-1 vote-container" :class="containerCls">
    <div class="ballot-box" :class="btnBoxCls" @click="handleClick(false)" @contextmenu.prevent="handleClick(true)">
      <svg height="18" width="18" viewBox="0 0 512 512" v-if="realVote?.status == 'M'">
        <g>
          <path
            d="M396.138,85.295c-13.172-25.037-33.795-45.898-59.342-61.03C311.26,9.2,280.435,0.001,246.98,0.001 c-41.238-0.102-75.5,10.642-101.359,25.521c-25.962,14.826-37.156,32.088-37.156,32.088c-4.363,3.786-6.824,9.294-6.721,15.056 c0.118,5.77,2.775,11.186,7.273,14.784l35.933,28.78c7.324,5.864,17.806,5.644,24.875-0.518c0,0,4.414-7.978,18.247-15.88 c13.91-7.85,31.945-14.173,58.908-14.258c23.517-0.051,44.022,8.725,58.016,20.717c6.952,5.941,12.145,12.594,15.328,18.68 c3.208,6.136,4.379,11.5,4.363,15.574c-0.068,13.766-2.742,22.77-6.603,30.442c-2.945,5.729-6.789,10.813-11.738,15.744 c-7.384,7.384-17.398,14.207-28.634,20.479c-11.245,6.348-23.365,11.932-35.612,18.68c-13.978,7.74-28.77,18.858-39.701,35.544 c-5.449,8.249-9.71,17.686-12.416,27.641c-2.742,9.964-3.98,20.412-3.98,31.071c0,11.372,0,20.708,0,20.708 c0,10.719,8.69,19.41,19.41,19.41h46.762c10.719,0,19.41-8.691,19.41-19.41c0,0,0-9.336,0-20.708c0-4.107,0.467-6.755,0.917-8.436 c0.773-2.512,1.206-3.14,2.47-4.668c1.29-1.452,3.895-3.674,8.698-6.331c7.019-3.946,18.298-9.276,31.07-16.176 c19.121-10.456,42.367-24.646,61.972-48.062c9.752-11.686,18.374-25.758,24.323-41.968c6.001-16.21,9.242-34.431,9.226-53.96 C410.243,120.761,404.879,101.971,396.138,85.295z"
          ></path>
          <path
            d="M228.809,406.44c-29.152,0-52.788,23.644-52.788,52.788c0,29.136,23.637,52.772,52.788,52.772 c29.136,0,52.763-23.636,52.763-52.772C281.572,430.084,257.945,406.44,228.809,406.44z"
          ></path>
        </g>
      </svg>
      <svg viewBox="0 0 352.62 352.62" width="18" height="18" v-if="realVote?.status == 'Y'">
        <g>
          <path
            d="M337.222,22.952c-15.912-8.568-33.66,7.956-44.064,17.748c-23.867,23.256-44.063,50.184-66.708,74.664 c-25.092,26.928-48.348,53.856-74.052,80.173c-14.688,14.688-30.6,30.6-40.392,48.96c-22.032-21.421-41.004-44.677-65.484-63.648 c-17.748-13.464-47.124-23.256-46.512,9.18c1.224,42.229,38.556,87.517,66.096,116.28c11.628,12.24,26.928,25.092,44.676,25.704 c21.42,1.224,43.452-24.48,56.304-38.556c22.645-24.48,41.005-52.021,61.812-77.112c26.928-33.048,54.468-65.485,80.784-99.145 C326.206,96.392,378.226,44.983,337.222,22.952z M26.937,187.581c-0.612,0-1.224,0-2.448,0.611 c-2.448-0.611-4.284-1.224-6.732-2.448l0,0C19.593,184.52,22.653,185.132,26.937,187.581z"
          ></path>
        </g>
      </svg>
      <svg width="18" height="18" viewBox="0 0 1024 1024" stroke-width="50" v-if="realVote?.status == 'N'">
        <g>
          <path
            d="M512.481 421.906L850.682 84.621c25.023-24.964 65.545-24.917 90.51.105s24.917 65.545-.105 90.51L603.03 512.377 940.94 850c25.003 24.984 25.017 65.507.033 90.51s-65.507 25.017-90.51.033L512.397 602.764 174.215 940.03c-25.023 24.964-65.545 24.917-90.51-.105s-24.917-65.545.105-90.51l338.038-337.122L84.14 174.872c-25.003-24.984-25.017-65.507-.033-90.51s65.507-25.017 90.51-.033L512.48 421.906z"
          ></path>
        </g>
      </svg>
    </div>
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
  --bs-bg-opacity: 0.75 !important;
  cursor: pointer;

  border-color: black;
  border-style: solid;
  border-width: 2px;
  border-radius: 8px;
}

.ballot-box-active:hover {
  --bs-bg-opacity: 0.75 !important;
}

.ballot-box {
  svg {
    stroke: var(--bs-body-color);
    fill: var(--bs-body-color);

    path {
      fill: var(--bs-body-color);
    }
  }
}
</style>
