# INF601 - Advanced Programming in Python
# Alex Crenshaw
# Mini Project 4

# REFERENCE / NOTE-TAKING FILE ONLY.
#
# This is NOT part of the running app and is never imported or executed.
# app.py in this repo is intentionally left in its original, unmodified
# (vulnerable) state so all 6 flags stay reproducible, as required by
# the assignment -- this file does not change that.
#
# It records the hands-on fix I wrote and tested for the IDOR
# vulnerability (finding #2) as additional practice beyond the required
# exploitation work. Full narrative, two editor screenshots (including
# a bug I introduced and fixed), and the before/after test transcript
# are in poc/02_idor.md under "Remediation -- applied and manually
# tested".
#
# Original (vulnerable) version, from app.py:
#
#     row = get_db().execute(
#         "SELECT id, owner, title, body FROM messages WHERE id = ?",
#         (msg_id,),
#     ).fetchone()
#
# Corrected version, as I wrote and tested it:

def message_detail_fixed(msg_id, user, get_db):
    row = get_db().execute(
        "SELECT id, owner, title, body FROM messages WHERE id = ? AND owner = ?",
        (msg_id, user["username"]),
    ).fetchone()
    return row
