<!-- HTML and CSS was adapted from https://codepen.io/fydsa/pen/abwdpep -->
<template>
  <div class="toggle-switch">
    <label>
      <input type="checkbox" v-model="lightMode" />
      <span class="slider"></span>
    </label>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, watch } from "vue";

export default defineComponent({
  setup() {
    const storedDarkMode = window.localStorage.getItem("dark-mode");
    const lightMode = ref(!(storedDarkMode != null ? storedDarkMode === "true" : false));

    watch(lightMode, (newValue) => {
      document.querySelector("html")?.setAttribute("data-bs-theme", newValue ? "light" : "dark");
      window.localStorage.setItem("dark-mode", "" + !newValue);
    });

    document.querySelector("html")?.setAttribute("data-bs-theme", lightMode.value ? "light" : "dark");

    return { lightMode };
  },
});
</script>

<style lang="scss" scoped>
.toggle-switch {
  --light: #ffffff;
  --dark: #000000;

  width: 60px;
  height: 30px;
}

label {
  position: relative;
  display: inline-block;
  scale: 0.3;
  width: 200px;
  height: 100px;
  background-color: var(--dark);
  border-radius: 50px;
  cursor: pointer;
  top: -33px;
  left: -70px;
}

input {
  display: none;
}

.slider {
  position: relative;
  display: inline-block;
  width: 100%;
  height: 100%;
  border-radius: 50px;
  transition: 0.3s;
}

input:checked ~ .slider {
  background-color: var(--light);
}

.slider::before {
  content: "";
  position: relative;
  display: inline-block;
  top: 13px;
  left: 16px;
  width: 75px;
  height: 75px;
  border-radius: 50%;
  box-shadow: inset 28px -4px 0px 0px var(--light);
  background-color: var(--dark);
  transition: 0.3s;
}

input:checked ~ .slider::before {
  transform: translateX(95px);
  background-color: var(--dark);
  box-shadow: none;
}
</style>
