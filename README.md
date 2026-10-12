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
| [`poc/`](poc/) | One file per finding with the exact request/payload/response that captured its flag |
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

This project is AI-assisted by design per the assignment, and the goal
is an honest accounting of what the AI (Claude Code) did versus what I
directed and checked myself.

**What Claude Code did:**
- Unzipped the starter files, set up the git repo, created the Python
  virtual environment, installed dependencies, and started the Flask
  app with the correct `FLAG_SEED`.
- Performed recon (home page hints, `robots.txt`, login form inspection)
  and drove every exploit over real HTTP requests (`curl`) — the SQL
  injection payload, the IDOR request as a logged-in low-privilege user,
  the forged `superadmin` cookie, the path-traversal file read, and the
  stored-XSS payload against the guestbook — reading each flag directly
  out of the app's live response, never from the filesystem or database.
- Read `app.py`'s source **after** all six flags were already captured
  black-box, to confirm root cause for the write-up.
- Drafted `REPORT.md`, the six `poc/*.md` files, this README, and
  `AGENTIC_WORKFLOW.md`.

**What I did:**
- Picked Track A, provided my FHSU username to generate the correct
  seed, and supplied the location of the downloaded starter files.
- Directed the overall order of attack (which vulnerability class to
  pursue next) and reviewed every captured flag and every PoC
  request/response before they were written into the report, confirming
  they matched `check_flags.py`'s validation output.
- Reviewed the final report and PoC write-ups for accuracy and can
  explain every exploit (the SQL comment-out trick, the unsigned
  base64 role cookie, the unescaped guestbook render, the unsanitized
  `os.path.join` traversal, the `robots.txt`-advertised backup
  directory, and the sequential-ID message lookup) at the Week 16
  review.
- Decided what belonged in the report vs. the PoC files, and confirmed
  the authorization/scope statement is accurate (local-only, Vuln Hub
  only).
