import { Ballot, Option, Vote, votesFromStr } from "./model";
import { pollStore } from "./store";
import { JWDJ_SUBPATH } from "@/config";
import { marked } from "marked";
import { sanitize } from "dompurify";

function endpointUrl(url: string): string {
  return JWDJ_SUBPATH + url;
}

function setStoreFromResponse(data: any) {
  const store = pollStore();
  store.name = data.name;
  store.description = data.description;
  store.allowNotVoted = data.allow_not_voted;
  store.isOwner = data.is_owner;
  store.options = data.options.map((x: any) => new Option(x.name, x.index, x.id));
  store.ballots = data.ballots.map((y: any) => new Ballot(y.name, votesFromStr(y.votes), y.note));
  store.isClosed = data.closed != null;
  store.closedOptionIndex = data.closed_option_idx;
  if (data.my_ballot != null) {
    const b = data.my_ballot;
    store.alreadyVoted = true;
    store.myBallot = new Ballot(b.name, votesFromStr(b.votes), b.note);
  } else {
    store.alreadyVoted = false;
    store.myBallot = new Ballot(
      "",
      store.options.map((_: any) => new Vote("-")),
      null
    );
  }
  store.footerInfo = `Poll valid until: ${data.valid_until}`;
}

function sumVotesData() {
  const store = pollStore();

  const sumYes = Array(store.options.length).fill(0);
  const sumMaybe = Array(store.options.length).fill(0);

  const ballots = [...store.ballots];
  if (store.myBallot != null) {
    ballots.push(store.myBallot);
  }

  for (const ballot of ballots) {
    for (let i = 0; i < ballot.votes.length; ++i) {
      const vote = ballot.votes[i].status;
      if (vote == "Y") {
        sumYes[i]++;
        sumMaybe[i]++;
      } else if (vote == "M") {
        sumMaybe[i]++;
      }
    }
  }

  return {
    yes: sumYes,
    maybe: sumMaybe,
    maxYes: Math.max(...sumYes),
    maxMaybe: Math.max(...sumMaybe),
  };
}

function markdown(raw: string): string {
  return sanitize(marked.parse(raw, { gfm: true, mangle: false, headerIds: false }), { USE_PROFILES: { html: true } });
}

export { endpointUrl, sumVotesData, setStoreFromResponse, markdown };
