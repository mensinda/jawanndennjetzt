import { Ballot, Option, Vote, votesFromStr } from "./model";
import { pollStore } from "./store";
import { JWDJ_SUBPATH } from "@/config";
import { marked } from "marked";
import { gfmHeadingId } from "marked-gfm-heading-id";
import DOMPurify from "dompurify";
import { i18n } from "./locales";

marked.use(gfmHeadingId());

function endpointUrl(url: string): string {
  return JWDJ_SUBPATH + url;
}

interface PollDataOption {
  id: string;
  index: number;
  name: string;
}

interface PollDataBallot {
  name: string;
  votes: string;
  note: string | null;
}

interface PollData {
  name: string;
  description: string;
  allow_not_voted: boolean;
  is_owner: boolean;
  closed: string | null;
  valid_until: string;
  closed_option_idx: number;
  options: PollDataOption[];
  ballots: PollDataBallot[];
  my_ballot: PollDataBallot | null;
}

function setStoreFromResponse(data: PollData) {
  const store = pollStore();
  store.name = data.name;
  store.description = data.description;
  store.allowNotVoted = data.allow_not_voted;
  store.isOwner = data.is_owner;
  store.options = data.options.map((x) => new Option(x.name, x.index, x.id));
  store.ballots = data.ballots.map((y) => new Ballot(y.name, votesFromStr(y.votes), y.note));
  store.isClosed = data.closed != null;
  store.closedOptionIndex = data.closed_option_idx;
  if (data.my_ballot != null) {
    const b = data.my_ballot;
    store.alreadyVoted = true;
    store.myBallot = new Ballot(b.name, votesFromStr(b.votes), b.note);
  } else {
    store.alreadyVoted = false;
    const initial_name = store.user?.user?.name;
    store.myBallot = new Ballot(
      initial_name === undefined ? "" : initial_name,
      store.options.map(() => new Vote("-")),
      null,
    );
  }
  store.footerInfo = `${i18n.global.t("poll.valid-until")}: ${data.valid_until}`;
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
  raw = raw.replaceAll("<m>", '<span class="text-muted">');
  raw = raw.replaceAll("<w>", '<span class="text-warning">');
  raw = raw.replaceAll("<d>", '<span class="text-danger">');
  raw = raw.replaceAll("<s>", '<span class="text-success">');
  raw = raw.replaceAll("<i>", '<span class="text-info">');
  raw = raw.replaceAll("</m>", "</span>");
  raw = raw.replaceAll("</w>", "</span>");
  raw = raw.replaceAll("</d>", "</span>");
  raw = raw.replaceAll("</s>", "</span>");
  raw = raw.replaceAll("</i>", "</span>");
  return DOMPurify.sanitize(marked.parse(raw, { gfm: true, async: false }) as string, { USE_PROFILES: { html: true } });
}

function fetchHeaders(): { [id: string]: string } {
  if (!document.cookie.includes("csrftoken")) {
    return {};
  }

  const csrftoken = document.cookie.replace(/.*csrftoken\s*=\s*([^;]+).*/, "$1");
  return {
    "X-CSRFTOKEN": csrftoken,
  };
}

export { PollData, endpointUrl, sumVotesData, setStoreFromResponse, markdown, fetchHeaders };
