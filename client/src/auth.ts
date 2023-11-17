import axios from "@/axios";
import { UserAuth } from "./model";
import { endpointUrl } from "@/util";
import { pollStore } from "@/store";

const store = pollStore();

async function load_user_info() {
  try {
    console.log("DATA SET START");
    const x = await axios<UserAuth>({
      url: endpointUrl("api/auth/is_authorised"),
      method: "get",
    });
    store.user = x.data;
    console.log("DATA SET");
  } catch (error) {
    // Do noting
  }
}

export { load_user_info };
