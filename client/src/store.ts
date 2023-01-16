import { defineStore } from "pinia";
import { Ballot, Option } from "@/model";

export const pollStore = defineStore("poll", {
  state() {
    return {
      name: "",
      description: "",
      options: [] as Option[],
      ballots: [] as Ballot[],
      myBallot: null as Ballot | null,
      allowNotVoted: false,
      alreadyVoted: false,
      isOwner: false,
      isClosed: false,
      closedOptionIndex: -1,
      footerInfo: "",
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
    },

    idx_autofix() {
      for (let i = 0; i < this.options.length; ++i) {
        this.options[i].index = i;
      }
    },
  },
});
