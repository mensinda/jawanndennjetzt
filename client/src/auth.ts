import { endpointUrl } from "@/util";
import { pollStore } from "@/store";

const store = pollStore();

async function load_user_info() {
  const response = await window.fetch(endpointUrl("api/auth/is_authorised"));

  if (response.ok) {
    store.user = await response.json();
  }
}

export { load_user_info };
