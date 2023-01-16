import { Ballot, Vote } from "@/model";
import mulberry32 from "@/random";

const NAME_LIST = [
  "James",
  "Robert",
  "John",
  "Michael",
  "David",
  "William",
  "Richard",
  "Joseph",
  "Thomas",
  "Charles",
  "Christopher",
  "Daniel",
  "Matthew",
  "Anthony",
  "Mark",
  "Donald",

  "Mary",
  "Patricia",
  "Jennifer",
  "Linda",
  "Elizabeth",
  "Barbara",
  "Susan",
  "Jessica",
  "Sarah",
  "Karen",
  "Lisa",
  "Nancy",
  "Betty",
  "Margaret",
  "Sandra",
  "Ashley",
];

const RANDOM_STATES = ["-", "Y", "Y", "Y", "Y", "Y", "N", "N", "M"];

class RandomBallot {
  name: string;
  seed: number;
  allowNotVoted: boolean;

  constructor(name: string, allowNotVoted: boolean) {
    this.name = name;
    this.allowNotVoted = allowNotVoted;
    const array = new Uint32Array(1);
    self.crypto.getRandomValues(array);
    this.seed = array[0];
  }

  votes(num: number): Vote[] {
    const rng = mulberry32(this.seed);
    const res = [];
    if (this.allowNotVoted) {
      for (let i = 0; i < num; ++i) {
        res.push(new Vote(RANDOM_STATES[Math.floor(rng() * RANDOM_STATES.length)]));
      }
    } else {
      const max = RANDOM_STATES.length - 1;
      for (let i = 0; i < num; ++i) {
        res.push(new Vote(RANDOM_STATES[Math.floor(rng() * max) + 1]));
      }
    }
    return res;
  }
}

class RandomPoll {
  randBallots: RandomBallot[];

  constructor(allowNotVoted: boolean) {
    const array = new Uint32Array(1);
    self.crypto.getRandomValues(array);
    const rng = mulberry32(array[0]);
    this.randBallots = [];

    const names: string[] = [];
    for (let i = 0; i < 8; ++i) {
      let name = NAME_LIST[Math.floor(rng() * NAME_LIST.length)];
      while (names.indexOf(name) >= 0) {
        name = NAME_LIST[Math.floor(rng() * NAME_LIST.length)];
      }
      names.push(name);
      this.randBallots.push(new RandomBallot(name, allowNotVoted));
    }
  }

  ballots(numOpts: number): Ballot[] {
    return this.randBallots.map((x) => new Ballot(x.name, x.votes(numOpts), null));
  }
}

export { RandomPoll, RandomBallot };
