class Option {
  name: string;
  id: string;
  index: number;
  orig_index: number;
  vid: number; // Make vue happy

  constructor(name: string, index: number, orig_index: number = -1, id = "") {
    this.name = name;
    this.id = id;
    this.index = index;
    this.orig_index = orig_index;
    this.vid = Math.random();
  }
}

const VALID_STATES = ["-", "Y", "M", "N"];

function votesFromStr(raw: string): Vote[] {
  const res = [];

  for (const x of raw) {
    res.push(new Vote(x));
  }

  return res;
}

class Vote {
  status: string;
  vid: number; // Make vue happy

  constructor(status: string) {
    if (VALID_STATES.indexOf(status) < 0) {
      throw Error("Invalid status: " + status);
    }
    this.status = status;
    this.vid = Math.random();
  }

  cycle(reverse: boolean) {
    let idx = VALID_STATES.indexOf(this.status);
    idx += reverse ? -1 : 1;
    if (idx >= VALID_STATES.length) {
      idx = 1; // You can not unset your vote!
    }
    if (idx < 1) {
      idx = VALID_STATES.length - 1;
    }
    this.status = VALID_STATES[idx];
  }
}

class Ballot {
  name: string;
  votes: Vote[];
  orig_votes: Vote[];
  note: string;
  vid: number; // Make vue happy

  constructor(name: string, votes: Vote[], note: string | null) {
    this.name = name;
    this.votes = votes;
    this.orig_votes = Object.assign([], votes);
    this.note = note == null ? "" : note;
    this.vid = Math.random();
  }
}

class UserData {
  username: string;
  name: string;
  email: string;

  constructor(username: string, name: string, email: string) {
    this.username = username;
    this.name = name;
    this.email = email;
  }
}

class UserAuth {
  authorised: boolean;
  authorisation_enabled: boolean;
  user: UserData | null;

  constructor(authorised: boolean, authorisation_enabled: boolean, user: UserData) {
    this.authorised = authorised;
    this.authorisation_enabled = authorisation_enabled;
    this.user = user;
  }
}

export { Option, Vote, Ballot, votesFromStr, UserAuth, VALID_STATES };
