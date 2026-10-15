#!/usr/bin/env python3
"""📥 desk.py: how your AI helper puts a question on the Desk, and reads your answers back.

WHY THIS EXISTS
    Anything waiting on you ("can I send this?", "which day works?", "is it okay if...?") goes on
    the Desk as a CARD with big buttons, instead of into a file you'd never open. You tap an
    answer. Your helper runs `desk.py answers` and sees what you picked (and any note you added).

USAGE
    python desk.py post "Which day works for the dentist?" "Tuesday 10am or Thursday 2pm." --options "Tuesday" "Thursday" "Neither"
    python desk.py post "Title" "Body" --kind fyi             # just letting you know, no decision needed
    python desk.py post "Title" "Body" --link https://...     # something to open
    python desk.py post "Title" "Body" --later                # not urgent: goes straight to the 🕐 Later tab
    python desk.py answers                                    # which cards have been answered, and how
    python desk.py list                                       # every card, answered or not
    python desk.py done <id>                                  # remove a card once the answer's been acted on

WHERE THE DESK IS
    It reads two settings, from environment variables or from desk.env next to this file:
        DESK_KEY   the same secret key the server uses (required)
        DESK_URL   where the server lives (default http://127.0.0.1:8797)

GOOD CARD MANNERS (for the AI writing the cards)
    🗣️  Plain words. Your person is not an AI: no jargon, no file paths unless they must click one.
    🔎  Check it isn't ALREADY decided first. Asking someone to re-decide something costs them
        the same as asking a new question.
    1️⃣  One question per card. Two to four buttons.
    🕐  Not urgent? Use --later. Today should only hold what actually needs them today.
    🤐  The Desk is a shared screen. Keep private details (health, money, other people's business)
        in their proper place, and just say "needs your say" on the card.

Only uses what comes with Python. No installs.
"""
import argparse
import datetime
import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

KINDS = ("decision", "read", "fyi", "todo")


def settings():
    """DESK_KEY and DESK_URL: environment first, then desk.env next to this file."""
    env = {}
    p = Path(__file__).resolve().parent / "desk.env"
    if p.exists():
        for line in p.read_text(encoding="utf-8").splitlines():
            if "=" in line and not line.strip().startswith("#"):
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip()
    key = os.environ.get("DESK_KEY") or env.get("DESK_KEY", "")
    url = (os.environ.get("DESK_URL") or env.get("DESK_URL") or "http://127.0.0.1:8797").rstrip("/")
    if not key:
        sys.exit("🛑 No DESK_KEY (set it in the environment or in desk.env next to this file).")
    return key, url


def call(path, body=None):
    """Talk to the desk server. GET when there's no body, POST when there is."""
    key, url = settings()
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(url + "/api/" + path, data=data,
                                 headers={"X-Desk-Key": key, "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        try:
            why = json.loads(e.read().decode("utf-8")).get("error", "")
        except Exception:
            why = ""
        sys.exit(f"🛑 the desk said no ({e.code}{': ' + why if why else ''}).")
    except urllib.error.URLError as e:
        sys.exit(f"🛑 couldn't reach the desk at {url} ({e.reason}). Is desk_server.py running?")


def cmd_post(a):
    title, body = a.title.strip(), a.body.strip()
    if not title:
        sys.exit("🛑 a card needs a title.")
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")[:40] or "card"
    cid = f"{slug}-{datetime.datetime.now().strftime('%m%d%H%M%S')}"
    card = {"id": cid, "title": title, "body": body, "kind": a.kind,
            "options": a.options or ["Yes", "No", "Later"], "later": a.later}
    if a.link:
        card["link"] = a.link
    if a.sender:
        card["from"] = a.sender
    call("cards", card)
    # ✅ don't trust "ok" alone: read the desk back and make sure the card is really there
    if not any(c.get("id") == cid for c in call("cards")):
        sys.exit("🛑 the desk said ok, but the card isn't there.")
    print(f"✅ on the desk as [{cid}]" + (" (in 🕐 Later)" if a.later else "") + ". Check back with: python desk.py answers")


def cmd_list(answered_only):
    cards = sorted(call("cards"), key=lambda c: c.get("order", 999))
    shown = [c for c in cards if c.get("answer")] if answered_only else cards
    for c in shown:
        if c.get("answer"):
            state = f"ANSWERED: {c['answer']} ({c.get('answeredAt') or '?'})"
        else:
            state = "waiting" + (" (🕐 Later)" if c.get("later") else "")
        print(f"[{c['id']}] {c.get('title')}  →  {state}")
        if c.get("note"):
            print(f"     note: {c['note']}")
    print(f"({len(shown)} shown of {len(cards)} cards)")


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")   # so the emoji print on Windows too
    except (AttributeError, ValueError):
        pass
    ap = argparse.ArgumentParser(description="Put a question on the Desk, or read the answers.")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("post", help="put a new card on the desk")
    p.add_argument("title")
    p.add_argument("body", nargs="?", default="")
    p.add_argument("--options", nargs="+", help="the button labels (default: Yes No Later)")
    p.add_argument("--kind", choices=KINDS, default="decision")
    p.add_argument("--link")
    p.add_argument("--from", dest="sender", help="who's asking (shown on the card)")
    p.add_argument("--later", action="store_true", help="put the card in the Later tab instead of Today")
    sub.add_parser("answers", help="show answered cards")
    sub.add_parser("list", help="show every card")
    d = sub.add_parser("done", help="remove a card after acting on it")
    d.add_argument("id")
    a = ap.parse_args()
    if a.cmd == "post":
        cmd_post(a)
    elif a.cmd in ("answers", "list"):
        cmd_list(a.cmd == "answers")
    elif a.cmd == "done":
        print(f"🧹 removed [{call('done', {'id': a.id})['removed']}]")


if __name__ == "__main__":
    main()
