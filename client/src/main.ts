import { createApp } from "vue";
import App from "./App.vue";
import router from "./router";
import { i18n, updateLocale } from "./locales";
import { createPinia } from "pinia";
import doInitParticles from "./particles";

// Load only the required bootstrap JS code
import "bootstrap/js/dist/collapse";

// Load the current locale as soon as possible
const updateLocalePromise = updateLocale(i18n.global.locale.value);

// Pinia
const pinia = createPinia();

const app = createApp(App);
app.use(pinia);
app.use(router);

// Use seperate file, so we can disable particles at build time
doInitParticles(app);

// Finish setup after locale has loaded
updateLocalePromise.then(() => {
  app.use(i18n);
  app.mount("#app");
});
