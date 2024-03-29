import { defineStore } from "pinia";
import { Ballot, Option, UserAuth } from "@/model";

export const pollStore = defineStore("poll", {
  state() {
    return {
      name: "",
      description: "",
      user: null as UserAuth | null,
      options: [] as Option[],
      ballots: [] as Ballot[],
      myBallot: null as Ballot | null,
      allowNotVoted: false,
      alreadyVoted: false,
      isOwner: false,
      isClosed: false,
      closedOptionIndex: -1,
      footerInfo: "",
      lastError: {
        msg: "",
        code: "",
      },
    };
  },

  actions: {
    reset() {
      this.name = "";
      this.description = "";
      this.options = [];
      this.ballots = [];
      this.myBallot = null;
      this.allowNotVoted = false;
      this.alreadyVoted = false;
      this.isOwner = false;
      this.isClosed = false;
      this.closedOptionIndex = -1;
      this.lastError = {
        msg: "",
        code: "",
      };
    },

    idx_autofix() {
      for (let i = 0; i < this.options.length; ++i) {
        this.options[i].index = i;
      }
    },
  },
});
