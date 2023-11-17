import axios from "@/axios";
import { UserAuth } from "./model";
import { endpointUrl } from "@/util";
import { pollStore } from "@/store";

const store = pollStore();

async function load_user_info() {
  await axios<UserAuth>({
    url: endpointUrl("api/auth/is_authorised"),
    method: "get",
  })
    .then((x) => {
      store.user = x.data;
    })
    .catch((_) => {
      return;
    });
}

export { load_user_info };
