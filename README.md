# Mini Project 4 — Vuln Hub Penetration Test

# INF601 - Advanced Programming in Python
# Alex Crenshaw
# Mini Project 4

Track: A

## What this repo is

An authorized penetration test of **Vuln Hub**, a small, intentionally
vulnerable Flask app provided as the Track A (Cybersecurity) target for
INF601 Mini Project 4. Six planted vulnerabilities were found and
exploited — SQL injection, IDOR, stored XSS, broken authorization, path
traversal, and sensitive data exposure — each yielding a unique
`FLAG{...}` captured via a real exploit, not by reading it off disk.

## Authorization statement

This assessment targeted **only** Vuln Hub, running locally on the
tester's own machine (bound to `127.0.0.1`, never exposed to a network).
It is authorized under the INF601 Mini Project 4 assignment. No other
system was scanned or tested. See [`REPORT.md`](REPORT.md) for the full
statement and findings.

## Repo contents

| Path | What it is |
|---|---|
| [`REPORT.md`](REPORT.md) | The pentest report: scope, methodology, findings, severity, remediation |
| [`poc/`](poc/) | One file per finding with the exact request/payload/response that captured its flag (plus `idor_fix_reference.py` and `screenshots/` from the hands-on IDOR fix exercise — see the AI Usage section) |
| [`submission.txt`](submission.txt) | The 6 captured flags, one per line |
| [`AGENTIC_WORKFLOW.md`](AGENTIC_WORKFLOW.md) | How this engagement was driven through Claude Code (goal → tool calls → review) |
| `app.py`, `templates/`, `static/`, etc. | The unmodified Vuln Hub target app (instructor-provided starter) |
| `check_flags.py` | Instructor-provided script to validate flag format against a username's seed |

## How to reproduce

### 1. Set your seed and run the target

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

export FLAG_SEED=abcrenshaw            # bash/zsh
# or, PowerShell:
$env:FLAG_SEED="abcrenshaw"

python app.py
```

Open <http://127.0.0.1:5000>. There should be **no red "DEFAULT seed"
banner** — if there is, `FLAG_SEED` wasn't picked up and the flags shown
will not match this report.

### 2. Reproduce the exploits

Each file in [`poc/`](poc/) contains the exact `curl` command(s) used
for that finding — run them against your own locally-running instance in
the same order documented there (SQLi → exposure → IDOR → authz →
traversal → stored XSS; order doesn't actually matter except that the
stored-XSS payload needs ~2–4 seconds for the simulated admin bot to
pick it up before checking `/grab`).

### 3. Verify the flags

```bash
python check_flags.py submission.txt --username abcrenshaw
```

Expected: `6/6 flags valid for username abcrenshaw`. This only confirms
flag format/seed match — credit for each flag still depends on the PoC
in `poc/` showing the exploit that produced it, per the assignment rules.

## AI Usage

This project was driven through Claude Code (Anthropic's agentic CLI).
Below is an honest, specific split of what the AI did versus what I did.

**What Claude Code did (autonomously, as the agent):**
- Set up the repo: unzipped the starter files, initialized git, created
  the Python virtual environment, installed dependencies, generated and
  set `FLAG_SEED` from my FHSU username, and started the app.
- Performed all recon and executed every exploit for all 6 findings —
  crafting and sending the SQL injection payload, logging in as `alice`
  and requesting message IDs for the IDOR, decoding and forging the
  `superadmin` cookie for the broken-authorization finding, sending the
  path-traversal request, and posting/polling the stored-XSS payload —
  capturing every flag from a live HTTP response, not from the
  filesystem or database.
- Read `app.py`'s source only after all 6 flags were already captured
  black-box, to write accurate root-cause and remediation explanations.
- Drafted every document in this repo: `REPORT.md`, the six `poc/*.md`
  files, this README, and `AGENTIC_WORKFLOW.md`.
- Ran all `git add` / `git commit` / `git push` commands.
- During my hands-on fix below, explained which line needed an
  ownership check and why, and diagnosed the cause of a server error I
  hit (read the Flask traceback in `restart.log` and identified that my
  edit had two SQL placeholders but only one bound value).

**What I (Alex) did:**
- Chose Track A, provided my FHSU username, and pointed Claude Code to
  the downloaded starter files.
- Created the GitHub repository myself on github.com and gave Claude
  Code the URL to push to.
- Reviewed the captured flags, the report, and the PoC write-ups.
- As additional hands-on practice beyond the required exploitation
  work, I personally wrote and tested a real fix for the IDOR
  vulnerability: I wrote the ownership-check code by hand in my own
  editor (from Claude's explanation of what needed to change, not a
  copy-pasted snippet), ran every restart/login/test command myself,
  and hit a real bug along the way — my first attempt left out one of
  the two values the fixed query needed, which Claude Code helped me
  track down by reading the error log. I corrected it myself and
  re-verified: the exploit now returns 404 instead of the flag, while
  legitimate access to your own messages still works. Two screenshots
  of my own editor (the buggy attempt and the corrected fix) and the
  full before/after test transcript are in
  [`poc/02_idor.md`](poc/02_idor.md#remediation--applied-and-manually-tested).
  I then reverted my local `app.py` back to the original vulnerable
  version so the submitted app still reproduces all 6 flags as
  required — the fix itself is preserved for reference in
  [`poc/idor_fix_reference.py`](poc/idor_fix_reference.py), not applied
  to the live app in this repo.

I can explain every exploit and the IDOR fix in detail at the Week 16
review.
