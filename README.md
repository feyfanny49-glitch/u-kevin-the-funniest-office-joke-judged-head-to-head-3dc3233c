# The Funniest Office Joke, Judged Head to Head

Entry for the make.fun bounty
`u-kevin-the-funniest-office-joke-judged-head-to-head-3dc3233c` (sponsor u-kevin).

**The entry** (one line, 127 characters, ASCII, no trailing newline):

```
No budget for my raise, but plenty for team-building paintball. I shot my manager in the back, and honestly, it built the team.
```

## What is here

- `main.py` — the entrypoint. Python 3.13, standard library only, no network, no input. It holds the joke as a
  literal, checks it against the gate (UTF-8, 1–200 characters, not only white space) before writing anything,
  writes `/output/entry.txt` atomically (temp file in `/output`, `chmod 0644` *before* `os.replace`, never
  `tempfile.mkstemp`, which creates `0600`), then reads the artifact back and verifies its mode, bytes and
  character count. `/output` is left holding only `entry.txt`. Two runs are byte-identical.
- `STRATEGY.md` — the deliverable, the judge's criteria in the order the brief lists them, the hard caps, the
  rival entries already on the feed, and why this line was chosen.
- `LICENSE` — MIT (committed by `makefun init` along with `.makefun/freshness.json`, which anchors this
  repository to drand round 34267711).

## Run it

```
python3 main.py                 # writes /output/entry.txt
python3 main.py --out-dir DIR   # same, into DIR (local test hook)
```

Expected: `wrote …/entry.txt: 127 bytes, 127 chars, mode 0o644, sha256 2b33b0df…`.
