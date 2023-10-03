import { createApp } from "vue";
import App from "./App.vue";
import router from "./router";
import "bootstrap/js/dist/collapse";
import "bootstrap/js/dist/tab";
import { createPinia } from "pinia";
import axios from "axios";

axios.defaults.xsrfHeaderName = "X-CSRFTOKEN";
axios.defaults.xsrfCookieName = "csrftoken";

const app = createApp(App);
app.use(router);

// Pinia
const pinia = createPinia();
app.use(pinia);

app.mount("#app");

export { app };
