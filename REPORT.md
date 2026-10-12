# Vuln Hub — Penetration Test Report

**Target:** Vuln Hub (Flask practice app), INF601 Mini Project 4, Track A
**Tester:** Alex Crenshaw (FHSU username `abcrenshaw`)
**Date:** October 11, 2026
**Seed:** `FLAG_SEED=abcrenshaw` (confirmed — no default-seed warning banner shown)

## Authorization & Scope Statement

This assessment was performed against **Vuln Hub only**, an intentionally
vulnerable Flask application distributed as the authorized target for
INF601 Mini Project 4. The application was run locally on the tester's
own machine, bound to `127.0.0.1`, and was never exposed to a network or
the public internet. No other system, service, or application was
accessed, scanned, or tested at any point during this engagement. This
test is authorized under the Mini Project 4 assignment and conducted
strictly within the scope and ethical boundaries it defines.

## Methodology

Testing followed a standard black-box web-application methodology:

1. **Recon** — reviewed the home page's challenge hints, checked
   `robots.txt` for disallowed paths, and inspected form fields (login,
   guestbook) before sending any payloads.
2. **Baseline requests** — issued a known-bad login and a known-good
   file download first, to see normal behavior before testing payloads.
3. **Exploitation** — one vulnerability class at a time: SQL injection,
   sensitive data exposure, IDOR, broken authorization, path traversal,
   stored XSS. Each exploit was driven over real HTTP requests against
   the running app (via `curl`), not by reading flags out of the
   filesystem or database directly — per the assignment rules, a flag
   only counts when a PoC shows the exploit that produced it.
4. **Verification** — after collecting all 6 flags, ran the project's
   own `check_flags.py submission.txt --username abcrenshaw` to confirm
   each flag matched the seed (6/6 `VALID`). This check awards no points
   itself; it only confirms the flags are correctly formatted for this
   seed.
5. **Source review** — `app.py` was read only *after* all six flags had
   already been captured through live exploitation, to confirm root
   cause and write accurate remediation advice for this report. No flag
   was obtained by reading source or on-disk files/database rows.

## Findings Summary

| # | Finding | Class | Severity | Flag |
|---|---|---|---|---|
| 1 | SQL injection in login | CWE-89 | Critical | `FLAG{sqli_7645cf91ca43}` |
| 2 | IDOR on `/messages/<id>` | CWE-639 | High | `FLAG{idor_cb8acad1b559}` |
| 3 | Stored XSS in guestbook | CWE-79 | Critical | `FLAG{xss_2a904a23f36b}` |
| 4 | Broken authorization via forgeable cookie | CWE-863 | Critical | `FLAG{authz_7b010b5a5bf9}` |
| 5 | Path traversal in `/download` | CWE-22 | High | `FLAG{traversal_dd53f986d659}` |
| 6 | Sensitive data exposure via `/backups/` | CWE-200 | High | `FLAG{exposure_9aa8fce5da07}` |

Full request/response evidence and step-by-step exploitation for each
finding is in [`poc/`](poc/):

- [`poc/01_sqli.md`](poc/01_sqli.md)
- [`poc/02_idor.md`](poc/02_idor.md)
- [`poc/03_stored_xss.md`](poc/03_stored_xss.md)
- [`poc/04_broken_authz.md`](poc/04_broken_authz.md)
- [`poc/05_path_traversal.md`](poc/05_path_traversal.md)
- [`poc/06_sensitive_data_exposure.md`](poc/06_sensitive_data_exposure.md)

## Findings in Detail

### 1. SQL Injection — Login Bypass (Critical)

The login form concatenates raw username/password into a SQL `SELECT`
statement. Submitting `username=admin'--` comments out the password
check, authenticating as `admin` with no valid credentials. See
[`poc/01_sqli.md`](poc/01_sqli.md).

**Remediation:** Use parameterized queries (`?` placeholders) for all
database access; never build SQL via string formatting on user input.
Hash stored passwords.

### 2. IDOR — Reading Other Users' Messages (High)

`/messages/<id>` returns any message by ID with no ownership check.
Logged in as the low-privilege account `alice`, message `#1` (owned by
`admin`, never linked to alice) was read directly by number. See
[`poc/02_idor.md`](poc/02_idor.md).

**Remediation:** Scope the query by both ID and the requesting user's
identity (`WHERE id = ? AND owner = ?`); return 404 on mismatch.

### 3. Stored XSS — Guestbook Cookie Theft (Critical)

Guestbook comments are rendered to all visitors — including a simulated
admin — without escaping. A posted `<script>` payload exfiltrated the
admin's session cookie (and the challenge flag embedded in it) to an
attacker-controlled endpoint. See [`poc/03_stored_xss.md`](poc/03_stored_xss.md).

**Remediation:** Escape all user-supplied content on render (restore
Jinja2's default autoescaping), mark session cookies `HttpOnly`, and
apply a Content-Security-Policy restricting inline scripts.

### 4. Broken Authorization — Forged Role Cookie (Critical)

The session is an unsigned `base64("username:role")` cookie that the
server trusts verbatim. A cookie value of `alice:superadmin` was
constructed client-side and granted access to `/vault`, a page no
legitimate login flow can reach. See [`poc/04_broken_authz.md`](poc/04_broken_authz.md).

**Remediation:** Never let the client set its own privilege level.
Use server-side sessions or a signed/encrypted token verified against a
trusted store, keyed by a server-issued session ID.

### 5. Path Traversal — Arbitrary File Read via `/download` (High)

The `file` query parameter is joined onto a base directory with
`os.path.join` and no traversal check, allowing `../private/...` (and
even the app's own source) to be read through the download endpoint.
See [`poc/05_path_traversal.md`](poc/05_path_traversal.md).

**Remediation:** Resolve the final path and verify it stays within the
intended base directory (or use `flask.send_from_directory`, which does
this check already) before opening any file.

### 6. Sensitive Data Exposure — Unprotected Backup Directory (High)

`robots.txt` advertises a disallowed `/backups/` path, which is itself a
route serving files with zero access control — including a SQL backup
containing secret data. See [`poc/06_sensitive_data_exposure.md`](poc/06_sensitive_data_exposure.md).

**Remediation:** Never host backups inside a web-served directory; treat
`robots.txt` as advisory only, never as access control; require
authentication for any endpoint serving operational/backup data.

## Overall Risk & Recommendations

Every finding stems from the same root pattern: **trusting client-supplied
input or client-held state as if it were already validated** — whether
that's SQL text, a file path, a role claim in a cookie, or HTML rendered
back to other users. None of the six require specialized tooling; each
was exploitable with a browser or `curl` and a single crafted request.
Prioritized fixes:

1. Move authentication/authorization entirely server-side (signed
   sessions, parameterized queries, hashed passwords) — this alone
   closes findings 1 and 4.
2. Apply output encoding/escaping consistently (template autoescaping) —
   closes finding 3.
3. Add ownership/authorization checks to every object-returning route
   (`/messages/<id>`), not just role-gated pages — closes finding 2.
4. Validate and canonicalize all filesystem paths built from user input,
   and never serve a directory meant to be private — closes findings
   5 and 6.

## AI Usage in This Assessment

See the [`## AI Usage`](README.md#ai-usage) section of the project
README for a full accounting of what Claude Code did versus what the
tester directed and verified.
