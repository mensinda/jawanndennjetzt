import { defineStore } from "pinia";
import { Vote, Ballot, Option, UserAuth } from "@/model";

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

    ballot_autofix() {
      // Create the ballot update plan
      const update_plan: Array<(x: Vote[]) => Vote> = [];
      for (let i = 0; i < this.options.length; ++i) {
        const opt = this.options[i];
        if (opt.orig_index < 0) {
          update_plan.push((x: Vote[]) => new Vote("-"));
        } else {
          update_plan.push((x: Vote[]) => x[opt.orig_index]);
        }
      }

      const update_ballot = (ballot: Ballot) => {
        const orig = ballot.orig_votes;
        ballot.votes = [];
        for (let j = 0; j < update_plan.length; ++j) {
          const vote = update_plan[j](orig);
          ballot.votes.push(vote);
        }
      };

      // Use the update plan to update the ballots
      for (let i = 0; i < this.ballots.length; ++i) {
        update_ballot(this.ballots[i]);
      }

      // My poll is seperate
      if (this.myBallot) {
        update_ballot(this.myBallot);
      }
    },
  },
});
