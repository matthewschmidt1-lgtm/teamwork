// Every line of copy in Teamwork lives here. Plain voice. No em dashes (a test checks).

export const COPY = {
  name: "Teamwork",
  tagline: "Think it through with someone who has made room for you.",

  privacy: "Your words stay in this browser. They go to the advisor only when you ask for a read, and are not kept there.",

  home: {
    question: "What's happening at work that's making it hard to work well with someone?",
    help: "Say it the way you'd tell a friend. You don't need to know what the problem is yet.",
    placeholder: "Start anywhere. One sentence is enough.",
    go: "Help me think it through",
    tooShort: "A sentence or two gives me something to work with.",
    openTitle: "Open",
    dueTitle: "Ready to look back",
    lookBack: "Look back",
    lookBackEarly: "It already happened",
    continueOne: "Pick up where you left off",
    recordTitle: "Your record",
    recordNote: "Counts from your own situations. Not a score.",
    deleteAll: "Delete everything here",
    deleteAllConfirm: "This removes every situation from this browser. There is no copy anywhere else.",
  },

  loading: {
    reflect: "Reading what you wrote",
    question: "Checking whether one thing would change the advice",
    read: "Working through it",
    lookback: "Comparing then with now",
  },

  error: {
    generic: "The advisor did not answer. Your words are still here.",
    retry: "Try again",
    later: "Save it and come back later",
  },

  reflect: {
    title: "Did I get that right?",
    help: "Move anything that's in the wrong place. Change any line. Add what I missed.",
    happened: "What happened",
    happenedHelp: "Things said or done. These carry the most weight.",
    told: "What you were told",
    toldHelp: "What other people said about it.",
    concluded: "What you've concluded",
    concludedHelp: "Your read of it. We'll test these, not assume them.",
    add: "Add a line",
    remove: "Remove this line",
    moveLabel: "Where this belongs",
    short: { happened: "Happened", told: "Told", concluded: "Concluded" },
    next: "That's right",
    back: "Back",
  },

  want: {
    title: "If this went well, what would be different a month from now?",
    help: "Not what you'd do. What you'd see.",
    placeholder: "For example: we'd agree on who decides, and I'd stop being surprised in meetings.",
    next: "Continue",
    skip: "I'm not sure yet",
  },

  question: {
    eyebrow: "One thing would change what I'd suggest.",
    placeholder: "Or answer in your own words",
    next: "Continue",
    skip: "I don't know",
  },

  read: {
    title: "Two ways to read this",
    help: "The facts so far fit more than one story. Here they are side by side, with the one thing that would tell them apart.",
    kinds: { person: "About them", self: "About your part", system: "About the setup" },
    supports: "What fits this",
    distinguishing: "What would tell",
    selfTitle: "One thing worth asking yourself",
    influenceTitle: "What you can and can't move",
    tensionTitle: "Two good things pulling against each other",
    next: "What to do",
  },

  step: {
    title: "One next step",
    why: "Why this one",
    assumes: "It assumes",
    backfires: "How it could go wrong",
    alternative: "If not this",
    wordsTitle: "Words you could use",
    wordsHelp: "Edit them until they sound like you.",
    managerTitle: "Before the conversation, since you manage them",
    next: "Decide what you'd look for",
  },

  post: {
    title: "Before you go: what would you see if this worked?",
    help: "One sentence, something you could observe. Then a date to check.",
    dateLabel: "When will you check?",
    next: "Keep this",
  },

  done: {
    title: "Your page",
    help: "Everything above, on one page you can copy. Come back on the date and we'll look at it together.",
    copy: "Copy the page",
    copied: "Copied",
    calendar: "Add the date to my calendar",
    feelTitle: "How do you feel about it now?",
    feelings: ["Clearer", "Steadier", "Still stuck", "Worse"],
    stuckHelp: "That's a fair answer. Three ways from here.",
    exits: {
      differently: "Talk it through differently",
      save: "Just save it for now",
      conduct: "This isn't a conversation problem",
    },
    home: "Back to the start",
    okay: "That's good to hear. It's saved.",
    worse: "Then this didn't help yet. It's saved, and you can come back to it, or let it be.",
  },

  conduct: {
    title: "This is a different kind of situation",
    lead: "What you've described is not a problem of saying the right thing better. It is conduct, and there are people whose job it is to act on it. Teamwork stops giving conversation advice here, on purpose.",
    stepsTitle: "Three things worth doing now",
    steps: [
      "Write down what happened, with dates and the words used, while it is fresh. Plain facts, no interpretation.",
      "Keep a copy somewhere that is not a work system: your own email, a note on your phone, paper.",
      "Find who holds the duty to act where you work: an HR partner, a manager above the person, an ombuds office, a union representative, or an employment lawyer. If there is a policy, read it before you decide.",
    ],
    outsideTitle: "Outside your organization",
    outside: "In the United States, the Equal Employment Opportunity Commission takes complaints about harassment, discrimination and retaliation, and most countries have an equivalent body. An employee assistance program, if you have one, is confidential. If you are in danger, call local emergency services.",
    keep: "Keep what I wrote",
    delete: "Delete what I wrote",
    deleted: "Deleted. Nothing from this remains in the browser.",
  },

  lookback: {
    title: "Looking back",
    blindHelp: "Before you see what you wrote then, two questions from memory.",
    expected: "What did you expect would happen?",
    happened: "What actually happened?",
    reveal: "Show me what I wrote",
    thenTitle: "What you wrote then",
    nowTitle: "What you say now",
    matched: { yes: "It happened.", partly: "Part of it happened.", no: "It didn't happen.", cant_tell: "Can't tell yet." },
    inferenceTitle: "What one outcome can tell you",
    lessonHelp: "One line, in your words. It will come back the next time something like this happens.",
    lessonPlaceholder: "Next time I'll...",
    save: "Keep the lesson",
    skipLesson: "Nothing to add",
    done: "Saved. That's the loop closed on this one.",
    earlierLessons: "You've written this before",
  },

  record: {
    situations: "situations thought through",
    lookbacks: "looked back on",
    matched: "where what you wrote happened",
    lessons: "lessons in your own words",
  },

  nav: { back: "Back", stop: "Save and stop", home: "Start" },
  page: {
    heading: "Teamwork page",
    account: "In your words",
    want: "What would be different",
    happened: "What happened",
    told: "What you were told",
    concluded: "What you concluded",
    explanations: "Two readings",
    step: "Next step",
    words: "Words",
    post: "What I'll look for",
    by: "Check on",
  },
};
