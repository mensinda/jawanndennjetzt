<!-- HTML and CSS was adapted from https://codepen.io/_Raunaq_/pen/wbRwea -->
<template>
  <div class="wrapper">
    <input type="checkbox" id="hide-checkbox" v-model="lightMode" />
    <label for="hide-checkbox" class="toggle">
      <span class="toggle-button">
        <span class="crater crater-1"></span>
        <span class="crater crater-2"></span>
        <span class="crater crater-3"></span>
        <span class="crater crater-4"></span>
        <span class="crater crater-5"></span>
        <span class="crater crater-6"></span>
        <span class="crater crater-7"></span>
      </span>
      <span class="star star-1"></span>
      <span class="star star-2"></span>
      <span class="star star-3"></span>
      <span class="star star-4"></span>
      <span class="star star-5"></span>
      <span class="star star-6"></span>
      <span class="star star-7"></span>
      <span class="star star-8"></span>
    </label>
  </div>
</template>

<script lang="ts">
import Cookies from "js-cookie";
import { defineComponent, ref, watch } from "vue";

export default defineComponent({
  setup() {
    const storedDarkMode = Cookies.get("dark-mode");
    const lightMode = ref(!(storedDarkMode != null ? storedDarkMode === "true" : false));

    watch(lightMode, (newValue) => {
      document.querySelector("html")?.setAttribute("data-bs-theme", newValue ? "light" : "dark");
      Cookies.set("dark-mode", "" + !newValue, { sameSite: "Lax" });
    });

    document.querySelector("html")?.setAttribute("data-bs-theme", lightMode.value ? "light" : "dark");

    return { lightMode };
  },
});
</script>

<style lang="scss" scoped>
.wrapper {
  width: 60px;
  height: 30px;
}

#hide-checkbox {
  opacity: 0;
  height: 0;
  width: 0;
}

.toggle {
  scale: 0.3;
  position: relative;
  top: -59px;
  left: -70px;
  cursor: pointer;
  display: inline-block;
  width: 200px;
  height: 100px;
  background: #211042;
  border-radius: 50px;
  transition: 500ms;
  overflow: hidden;
}

.toggle-button {
  position: absolute;
  display: inline-block;
  top: 7px;
  left: 6px;
  width: 86px;
  height: 86px;
  border-radius: 50%;
  background: #faeaf1;
  overflow: hidden;
  box-shadow: 0 0 35px 4px rgba(255, 255, 255);
  transition: all 500ms ease-out;
}

.crater {
  position: absolute;
  display: inline-block;
  background: #faeaf1;
  border-radius: 50%;
  transition: 500ms;
}

.crater-1 {
  background: #fffff9;
  width: 86px;
  height: 86px;
  left: 10px;
  bottom: 10px;
}

.crater-2 {
  width: 20px;
  height: 20px;
  top: -7px;
  left: 44px;
}

.crater-3 {
  width: 16px;
  height: 16px;
  top: 20px;
  right: -4px;
}

.crater-4 {
  width: 10px;
  height: 10px;
  top: 24px;
  left: 30px;
}

.crater-5 {
  width: 15px;
  height: 15px;
  top: 40px;
  left: 48px;
}

.crater-6 {
  width: 10px;
  height: 10px;
  top: 48px;
  left: 20px;
}

.crater-7 {
  width: 12px;
  height: 12px;
  bottom: 5px;
  left: 35px;
}

.star {
  position: absolute;
  display: inline-block;
  border-radius: 50%;
  background: #fff;
  box-shadow: 1px 0 2px 2px rgba(255, 255, 255);
}

.star-1 {
  width: 6px;
  height: 6px;
  right: 90px;
  bottom: 40px;
}

.star-2 {
  width: 8px;
  height: 8px;
  right: 70px;
  top: 10px;
}

.star-3 {
  width: 5px;
  height: 5px;
  right: 60px;
  bottom: 15px;
}

.star-4 {
  width: 3px;
  height: 3px;
  right: 40px;
  bottom: 50px;
}

.star-5 {
  width: 4px;
  height: 4px;
  right: 10px;
  bottom: 35px;
}

.star-6,
.star-7,
.star-8 {
  width: 10px;
  height: 2px;
  border-radius: 2px;
  transform: rotate(-45deg);
  box-shadow: 5px 0px 4px 1px #fff;
  animation-name: travel;
  animation-duration: 1.5s;
  animation-timing-function: ease-out;
  animation-iteration-count: infinite;
}

.star-6 {
  right: 30px;
  bottom: 30px;
  animation-delay: -2s;
}

.star-7 {
  right: 50px;
  bottom: 60px;
}

.star-8 {
  right: 90px;
  top: 10px;
  animation-delay: -4s;
}

@keyframes travel {
  0% {
    transform: rotate(-45deg) translateX(70px);
  }

  50% {
    transform: rotate(-45deg) translateX(-20px);
    box-shadow: 5px 0px 6px 1px #fff;
  }

  100% {
    transform: rotate(-45deg) translateX(-30px);
    width: 2px;
    height: 2px;
    opacity: 0;
    box-shadow: none;
  }
}

#hide-checkbox:checked + .toggle {
  background: #24d7f7;
}

#hide-checkbox:checked + .toggle .toggle-button {
  background: #f7ffff;
  transform: translateX(102px);
  box-shadow: 0 0 35px 5px rgba(255, 255, 255);
}

#hide-checkbox:checked + .toggle .toggle-button .crater {
  transform: rotate(-45deg) translateX(70px);
}

#hide-checkbox:checked + .toggle .star {
  animation: move 4s infinite;
  transform: none;
  box-shadow: none;
}

#hide-checkbox:checked + .toggle .star-1 {
  width: 40px;
  height: 10px;
  border-radius: 10px;
  background: #fff;
  left: 20px;
  top: 25px;
  box-shadow: none;
}

#hide-checkbox:checked + .toggle .star-2 {
  width: 12px;
  height: 12px;
  background: #fff;
  left: 26px;
  top: 23px;
  box-shadow: -1px 0 2px 0 rgba(0, 0, 0, 0.1);
}

#hide-checkbox:checked + .toggle .star-3 {
  width: 16px;
  height: 16px;
  background: #fff;
  left: 35px;
  top: 19px;
  box-shadow: -1px 0 2px 0 rgba(0, 0, 0, 0.1);
}

#hide-checkbox:checked + .toggle .star-4 {
  width: 14px;
  height: 14px;
  background: #fff;
  left: 46px;
  top: 21px;
  box-shadow: -1px 0 2px 0 rgba(0, 0, 0, 0.1);
}

#hide-checkbox:checked + .toggle .star-5 {
  width: 60px;
  height: 15px;
  border-radius: 15px;
  background: #fff;
  left: 30px;
  bottom: 20px;
  box-shadow: none;
}

#hide-checkbox:checked + .toggle .star-6 {
  width: 18px;
  height: 18px;
  background: #fff;
  border-radius: 50%;
  left: 38px;
  bottom: 20px;
  box-shadow: -1px 0 2px 0 rgba(0, 0, 0, 0.1);
}

#hide-checkbox:checked + .toggle .star-7 {
  width: 24px;
  height: 24px;
  background: #fff;
  border-radius: 50%;
  left: 52px;
  bottom: 20px;
  box-shadow: -1px 0 2px 0 rgba(0, 0, 0, 0.1);
}

#hide-checkbox:checked + .toggle .star-8 {
  width: 21px;
  height: 21px;
  background: #fff;
  border-radius: 50%;
  left: 70px;
  top: 59px;
  box-shadow: -1px 0 2px 0 rgba(0, 0, 0, 0.1);
}

@keyframes move {
  0% {
    transform: none;
  }

  25% {
    transform: translateX(4px);
  }

  50% {
    transform: translateX(2px);
  }

  75% {
    transform: translateX(1px);
  }

  100% {
    transform: none;
  }
}
</style>
