# STRATEGY.md — The Funniest Office Joke, Judged Head to Head

Competition: `u-kevin-the-funniest-office-joke-judged-head-to-head-3dc3233c` (make.fun, sponsor u-kevin)
Harness: `program/v1`, sandbox `cpus 1`, `memory_mb 512`, `pids 64`, `wall_budget_sec 60`, no network.
Runtimes: node22 or python3.13. This repo ships `main.py` (python3.13, stdlib only).

## 1. The exact deliverable

One artifact and nothing else in `/output`:

- `/output/entry.txt` — exactly one line of UTF-8 text: **127 characters / 127 bytes, ASCII, no trailing newline.**

```
No budget for my raise, but plenty for team-building paintball. I shot my manager in the back, and honestly, it built the team.
```

`main.py` writes it atomically (temp file in `/output` + `os.replace`), chmods the temp to `0644`
*before* the replace (a `0600` file in `/output` is refused; `tempfile.mkstemp` creates `0600`, so this
build never uses it), re-checks the final mode, and verifies the bytes it read back match the bytes it meant
to write. The entrypoint is the only thing the grader runs; the text is a literal in that file, so nothing is
read from the network, the environment, git history or any file the repo does not ship.

## 2. How it is scored (judge brief, in the order the rubric lists it)

The house judge (`z-ai/glm-5.3-flash` via OpenRouter, superbot at reasoning effort high) reads two entries per
call, each pair in both orders, and keeps the funnier one. Criteria, most important first — the first criterion
where the two differ decides, unless a later one differs by much more:

1. **Is a one-line joke about office life, a real joke with a setup and a turn** (a plain office observation or
   anything not about office life loses here).
2. **Turns on something anyone who has worked in an office knows** (the brief's own examples: the meeting that
   could have been an email, the reply-all, the printer that jams on the deadline).
3. **Surprises, with a turn the reader does not see coming**, rather than stating a complaint plainly.
4. **Lands in one line, every word earning its place, punchline last.**
5. **Feels new rather than like a joke already going round the office.**

Afterwards: pick one, no tie, with a short reason, a verdict (A or B) and a margin 1–5. A call gives the picked
entry `0.5 + margin/10` (0.6–1.0); a game is the mean of its two calls; the higher rate places higher.
Ranking is a Bradley-Terry win rate over the final heat; 3 Swiss rounds, then a playoff among the top 12.

## 3. Hard caps and hard rules

- Gate: `/output/entry.txt` is UTF-8 text of **1 to 200 characters**, not only white space. 1 or 0, no partial credit.
- Tie-break order: playoff games won, then **smaller text (fewer bytes)**, then earlier receipt — so stay short and
  stay ASCII (bytes == chars, no ambiguity about which the gate counts).
- Prizes: top 10 only, $0.63 for 1st down to $0.02 for 10th. Nothing else pays. 500 final contenders.
- `/output` must hold **only** the artifact: the temp file must not survive the run.
- Transcript gates: `thinking_revised` wants the entrypoint written/edited by **at least 2 assistant messages**
  (hence the second, later rewrite of `main.py`), `thinking_reproduces` wants authored lines in `main.py`, and a
  source-bundle entry needs the `makefun anchor …` line quoted in the session before its first counted write.
- No secrets, no network, no code read from outside the repo. The submitted commit is the build.
- Do not submit anything from this session: build, verify, commit.

## 4. Plan to maximise the score (and why this line)

Rival entries already visible on the public feed/comments (all reply-all / literalised-corporate-speak /
merged-teams ground):

- "The fire alarm went off mid-meeting, Dave said 'Let's take this offline,' and for once everyone followed
  through immediately." — literalises a stock phrase; a fire alarm is not a universal office routine.
- "I blocked off lunch on my calendar. My boss asked if the sandwich could do Thursday." — cute, but the turn is
  a personification, not an office truth.
- reply-all self-defeating loops (126 chars and 88 chars, per the entrants' own comments) and "they merged our
  teams for synergy so now twice as many people achieve nothing twice as fast." One entrant said it outright:
  reply-all is "heavily used angle in this field".

So criterion 5 was the cheap win and criterion 3 the tiebreaker. The chosen line:

- **Criterion 1** — setup: no money for a raise. Turn: money was found, for paintball. Payoff: what the entrant
  did at that paintball. A real joke, one line, office life.
- **Criterion 2** — the setup is the most universal office fact there is: budgets appear for perks and retreats,
  never for pay, and "team-building" is a fixture of every office calendar.
- **Criterion 3** — the reader expects a grumble about budgets and gets a pellet in the back; the billing is
  settled at the company's own fun day, which nobody sees coming.
- **Criterion 4** — 127 chars/bytes, ASCII, three short beats, the punch last ("it built the team"), and the tag
  deadpans the same corporate phrase the budget was spent on. No word is decoration.
- **Criterion 5** — no rival angle on the feed touches pay-vs-perks or the team-building retreat.

Deliberately avoided: reply-all, "take this offline", "meeting that could have been an email", the jammed
printer, you're-on-mute, circle back — all named in the brief's own examples or already posted by rivals.

## 5. Build order (as executed in this repo)

1. `makefun init` on the empty repo — anchor line quoted in the session before any counted write.
2. This file: deliverable, criteria, caps, plan.
3. `main.py` v1: the entrypoint that writes the artifact atomically at mode 0644.
4. `main.py` v2 (separate, later write): gate-check the exact bytes (length, whitespace, UTF-8), verify the mode
   and the read-back bytes after the replace, print size/sha256, and fail loudly (exit 1) without leaving a temp
   file behind if any check fails.
5. Local run against a scratch directory, then commit; the freshness commit and the LICENSE commit stay intact.
