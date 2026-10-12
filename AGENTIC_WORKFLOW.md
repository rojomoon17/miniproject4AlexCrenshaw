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

See the README's [`## AI Usage`](README.md#ai-usage) section for the
explicit split between what Claude Code executed and what the human
directed, reviewed, and decided.
