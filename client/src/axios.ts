import axios, { AxiosError } from "axios";

axios.defaults.xsrfHeaderName = "X-CSRFTOKEN";
axios.defaults.xsrfCookieName = "csrftoken";

export { AxiosError };

export default axios;
