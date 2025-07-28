<template>
  <ModalErrorMessage ref="errorModal" />
  <ModalInvalidToken ref="errorInvalid" />
  <div class="container">
    <h1 class="display-2 text-center mb-4">{{ $t("root.session") }}</h1>

    <!-- Help -->
    <div class="card mb-4">
      <label class="card-header">{{ $t("session.help-title") }}</label>
      <div class="card-body">
        <p>{{ $t("session.help-body") }}</p>
        <p>{{ $t("session.help-body-2") }}</p>

        <h5>{{ $t("session.stepps") }}</h5>

        <ol>
          <li>{{ $t("session.stepp-1") }}</li>
          <li>{{ $t("session.stepp-2") }}</li>
          <li>{{ $t("session.stepp-3") }}</li>
        </ol>
      </div>
    </div>

    <div class="card mb-4">
      <label class="card-header">{{ $t("session.merge-title") }}</label>
      <div class="card-body">
        <!-- Select buttons-->
        <div class="select-btns" v-if="state == 'select'">
          <button type="button" class="btn btn-primary btn-lg" style="grid-area: btn1" @click="generate_otp">
            {{ $t("session.btn-generate-otp") }}
          </button>
          <button type="button" class="btn btn-primary btn-lg" style="grid-area: btn2" @click="state = 'enter'">
            {{ $t("session.btn-enter-otp") }}
          </button>
        </div>

        <!-- Request OTP -->
        <div class="generate-otp" v-if="state == 'generate'">
          <h1 style="grid-area: otp">
            <code style="white-space: pre-wrap">{{ display_otp }}</code>
          </h1>
          <button type="button" class="btn btn-secondary" @click="state = 'select'" style="grid-area: b">
            {{ $t("session.btn-back") }}
          </button>
          <button type="button" class="btn btn-primary" @click="generate_otp" style="grid-area: gen">
            {{ $t("session.btn-regenerate") }}
          </button>
          <span style="grid-area: l1"
            ><b>{{ $t("session.do-not-share") }}</b></span
          >
          <span
            style="grid-area: l2"
            v-html="$t('session.token-valid-until', { valid_until: display_valid_until }, { escapeParameter: false })"
          ></span>
        </div>

        <!-- Submit OTP -->
        <div class="enter-otp" v-if="state == 'enter'">
          <button type="button" class="btn btn-secondary" @click="state = 'select'" style="grid-area: back">
            {{ $t("session.btn-back") }}
          </button>
          <button
            type="button"
            class="btn btn-primary"
            :disabled="enter_otp.replace(/\s/g, '').length != 8"
            @click="submit"
            style="grid-area: exec"
          >
            {{ $t("session.submit") }}
          </button>
          <label for="inputLarge" class="col-form-label col-form-label-lg" style="grid-area: l1">{{
            $t("session.submit-help")
          }}</label>
          <input
            id="inputLarge"
            :class="input_classes"
            type="text"
            placeholder="X X X X   X X X X"
            style="grid-area: input"
            v-model="enter_otp"
            @keyup.enter="submit"
          />
        </div>
      </div>

      <!-- Request OTP -->
      <div class="done mb-4" v-if="state == 'done'">
        <button type="button" class="btn btn-success" @click="state = 'select'" style="grid-area: back">
          {{ $t("session.btn-success") }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { endpointUrl, fetchHeaders } from "@/util";
import { ref, onMounted, onBeforeUnmount, computed } from "vue";
import ModalErrorMessage from "@/components/ModalErrorMessage.vue";
import ModalInvalidToken from "@/components/ModalInvalidToken.vue";

const errorModal = ref<typeof ModalErrorMessage | null>(null);
const errorInvalid = ref<typeof ModalInvalidToken | null>(null);

const state = ref("select");
const display_otp = ref("_ _ _ _   _ _ _ _");
const display_valid_until = ref("<N/A>");
const enter_otp = ref("");

async function generate_otp() {
  state.value = "generate";
  display_otp.value = "_ _ _ _   _ _ _ _";
  display_valid_until.value = "<N/A>";

  const response = await window.fetch(endpointUrl("api/session/gen_otp"), {
    method: "post",
    headers: fetchHeaders(),
    body: JSON.stringify({}),
  });

  if (!response.ok) {
    await errorModal.value?.showError(response);
    return;
  }

  const data = await response.json();
  const otp: string = data.otp;
  const valid_until: string = data.valid_until;
  display_otp.value = `${otp[0]} ${otp[1]} ${otp[2]} ${otp[3]}   ${otp[4]} ${otp[5]} ${otp[6]} ${otp[7]}`;
  display_valid_until.value = new Date(valid_until).toLocaleTimeString();
}

async function submit() {
  const response = await window.fetch(endpointUrl("api/session/submit"), {
    method: "post",
    headers: fetchHeaders(),
    body: JSON.stringify({
      otp: enter_otp.value.replace(/\s*/g, "").toUpperCase(),
    }),
  });

  if (!response.ok) {
    try {
      const data = await response.json();
      if (data.code == "INVALID_DATA") {
        errorInvalid.value?.doShow();
        return;
      }
    } catch {
      // Do nothing
    }
    await errorModal.value?.showError(response);
    return;
  }

  state.value = "done";
  enter_otp.value = "";
}

const input_classes = computed(() => {
  const s = enter_otp.value.replace(/\s*/g, "");
  return {
    "form-control": true,
    "form-control-lg": true,
    "is-valid": s.length > 0 && s.length == 8,
    "is-invalid": s.length > 0 && s.length != 8,
  };
});
</script>

<style lang="scss" scoped>
.select-btns {
  display: grid;
  @media screen and (min-width: 992px) {
    grid-template-rows: max-content;
    grid-template-columns: 1fr 1fr 1fr 1fr 1fr;
    grid-template-areas: ". btn1 . btn2 .";

    @media screen and (min-width: 1200px) {
      grid-template-columns: 2fr 1fr 1fr 1fr 2fr;
    }
  }
  @media screen and (max-width: 992px) {
    grid-template-rows: max-content 30px max-content;
    grid-template-columns: 1fr;
    grid-template-areas:
      "btn1"
      "."
      "btn2";
  }
}

.generate-otp {
  display: grid;
  gap: 10px;
  grid-template-rows: auto;
  grid-template-columns: 1fr max-content 1fr;
  grid-template-areas:
    ". l1  ."
    ". otp ."
    ". l2  ."
    "b gen .";

  .btn-secondary {
    justify-self: start;
  }

  @media screen and (max-width: 992px) {
    grid-template-areas:
      ". l1  ."
      ". otp ."
      ". l2  ."
      ". gen ."
      ". b   .";

    .btn-secondary {
      justify-self: stretch;
    }
  }

  span,
  h1 {
    justify-self: center;
    text-align: center;
  }
}

.enter-otp {
  display: grid;
  gap: 20px;
  grid-template-rows: auto;
  grid-template-columns: 1fr max-content 1fr;
  grid-template-areas:
    ".    l1    ."
    ".    input ."
    "back exec  .";

  input {
    font-family: monospace;
  }

  label {
    margin: 0;
    padding: 0;
  }

  .btn-secondary {
    justify-self: start;
  }

  @media screen and (max-width: 992px) {
    grid-template-areas:
      ". l1    ."
      ". input ."
      ". exec  ."
      ". back  .";

    .btn-secondary {
      justify-self: stretch;
    }
  }
}

.done {
  display: grid;
  grid-template-rows: auto;
  grid-template-columns: 1fr max-content 1fr;
  grid-template-areas: ". back  .";
}
</style>
