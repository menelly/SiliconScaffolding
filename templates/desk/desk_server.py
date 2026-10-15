#!/usr/bin/env python3
"""📥 The Desk: everything waiting on you, as cards with one-tap answers.

WHY THIS EXISTS
    When an AI helper needs a decision from you ("can I send this?", "which day works?"), the
    easy thing for the AI is to write it in a file. Files like that never get opened. So instead
    the question goes on a CARD with big buttons. You tap an answer on your phone or computer,
    and your AI reads the answer back. Nothing gets lost in a file you'll never open.

HOW TO RUN IT (no installs: this only uses what comes with Python)
    1. Pick a secret key, any long random word. Either:
         • make a file called desk.env next to this one containing:   DESK_KEY=your-long-random-word
         • or set an environment variable called DESK_KEY
    2. python desk_server.py
    3. Open  http://127.0.0.1:8797/?k=your-long-random-word  once in your browser.
       The page remembers the key on that device and tidies it out of the address bar,
       so after that plain  http://127.0.0.1:8797/  works.

    Optional settings (environment variables):
         DESK_PORT   which port to listen on (default 8797)
         DESK_HOST   which address to listen on (default 127.0.0.1 = this computer only).
                     Only change this if you know how you're protecting it (see the README).

THE KEY: the page itself holds no data. Every request for cards sends the key in a header
called X-Desk-Key. No key, or the wrong key → the server says no and shows nothing.

THE DATA: cards.json, next to this file. Written "atomically" (to a temporary file first, then
swapped in), so a crash halfway through can never leave you with half a file.

A CARD looks like this (only id and title are required):
    {
      "id": "dentist-day",                     a short unique name
      "title": "Which day works for the dentist?",
      "body": "They have Tuesday 10am or Thursday 2pm.",
      "kind": "decision",                      decision | read | fyi | todo
      "options": ["Tuesday", "Thursday", "Neither"],   the buttons (default: Yes / No / Later)
      "from": "helper",                        optional: who's asking, shown on the card
      "link": "https://...",                   optional: a thing to open
      "order": 50,                             optional: smaller numbers show first
      "later": false,                          true = waits in the 🕐 Later tab, not 📌 Today
      ... plus fields the server fills in: created, answer, answeredAt, note, laterAt
    }
"""
import hmac
import json
import os
import re
import threading
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

HERE = Path(__file__).resolve().parent
CARDS = HERE / "cards.json"
PAGE = HERE / "index.html"
LOCK = threading.Lock()          # one change at a time, so two taps can't trip over each other
KINDS = ("decision", "read", "fyi", "todo")
CARD_ID = re.compile(r"[A-Za-z0-9._-]{1,80}")   # the only shape a card id may have


def now_utc():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def load_env():
    """Read desk.env (KEY=value lines) if it exists. Lines starting with # are notes, skipped."""
    env = {}
    p = HERE / "desk.env"
    if p.exists():
        for line in p.read_text(encoding="utf-8").splitlines():
            if "=" in line and not line.strip().startswith("#"):
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip()
    return env


ENV = load_env()
KEY = os.environ.get("DESK_KEY") or ENV.get("DESK_KEY", "")
HOST = os.environ.get("DESK_HOST") or ENV.get("DESK_HOST", "127.0.0.1")
PORT = int(os.environ.get("DESK_PORT") or ENV.get("DESK_PORT", "8797"))


def read_cards():
    if not CARDS.exists():
        return []
    return json.loads(CARDS.read_text(encoding="utf-8"))


def write_cards(cards):
    tmp = CARDS.with_suffix(".tmp")
    tmp.write_text(json.dumps(cards, indent=2, ensure_ascii=False), encoding="utf-8")
    os.replace(tmp, CARDS)   # the swap: either the old file or the new one, never half of each


def clean_new_card(body):
    """A card someone wants to post → (tidy card, None), or (None, what's wrong in plain words)."""
    cid = str(body.get("id", "")).strip()
    title = str(body.get("title", "")).strip()
    if not CARD_ID.fullmatch(cid):
        return None, "a card needs an id made of letters, numbers, dots, dashes or underscores"
    if not title:
        return None, "a card needs a title"
    kind = body.get("kind") or "decision"
    if kind not in KINDS:
        return None, "kind must be one of: " + ", ".join(KINDS)
    options = body.get("options") or ["Yes", "No", "Later"]
    if not isinstance(options, list) or not (1 <= len(options) <= 6):
        return None, "options should be a list of 1 to 6 button labels"
    card = {
        "id": cid,
        "title": title[:200],
        "body": str(body.get("body") or "")[:4000],
        "kind": kind,
        "options": [str(o)[:60] for o in options],
        "order": body.get("order") if isinstance(body.get("order"), (int, float)) else 50,
        "created": now_utc(),
        "answer": None,
        "answeredAt": None,
        "note": None,
        "later": bool(body.get("later")),
        "laterAt": None,
    }
    if card["later"]:
        card["laterAt"] = card["created"]
    for optional in ("from", "link", "ticket"):
        if body.get(optional):
            card[optional] = str(body[optional])[:300]
    return card, None


class Handler(BaseHTTPRequestHandler):
    server_version = "Desk/1"

    def log_message(self, fmt, *args):   # quiet on purpose: no request lines in logs, so no keys in logs
        pass

    def _send(self, code, body, ctype="application/json"):
        data = body if isinstance(body, bytes) else json.dumps(body, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")      # always fresh cards, never a stale copy
        self.send_header("X-Robots-Tag", "noindex")        # search engines: please don't
        self.end_headers()
        self.wfile.write(data)

    def _authed(self):
        got = self.headers.get("X-Desk-Key", "")
        return bool(KEY) and hmac.compare_digest(got, KEY)   # compare_digest = no timing hints about the key

    def do_GET(self):
        path = self.path.split("?", 1)[0]
        if path in ("/", "/index.html"):
            return self._send(200, PAGE.read_bytes(), "text/html; charset=utf-8")
        if path == "/api/cards":
            if not self._authed():
                return self._send(401, {"error": "key"})
            with LOCK:
                return self._send(200, read_cards())
        return self._send(404, {"error": "not found"})

    def do_POST(self):
        path = self.path.split("?", 1)[0]
        if not self._authed():
            return self._send(401, {"error": "key"})
        try:
            n = int(self.headers.get("Content-Length", "0") or 0)
            body = json.loads(self.rfile.read(max(0, min(n, 20000))) or b"{}")
            if not isinstance(body, dict):
                raise ValueError
        except (ValueError, json.JSONDecodeError):
            return self._send(400, {"error": "bad json"})

        with LOCK:
            cards = read_cards()

            # ➕ POST A CARD (your AI does this, usually through desk.py). Same id again = replace it.
            if path == "/api/cards":
                card, why = clean_new_card(body)
                if card is None:
                    return self._send(400, {"error": why})
                cards = [c for c in cards if c.get("id") != card["id"]] + [card]
                write_cards(cards)
                return self._send(200, card)

            cid = str(body.get("id", ""))
            card = next((c for c in cards if c.get("id") == cid), None)
            if card is None:
                return self._send(404, {"error": "no such card"})

            if path == "/api/answer":
                # ✅ a button was tapped. Only that card's own buttons count as answers.
                answer = str(body.get("answer", ""))[:200]
                if answer not in [str(o) for o in (card.get("options") or ["Yes", "No", "Later"])]:
                    return self._send(400, {"error": "not one of this card's answers"})
                note = str(body.get("note") or "").strip()[:2000]
                card["note"] = note or None
                # 🕐 A "Later" ANSWER IS A PUNT. Two buttons both called Later, where only one moved the
                # card, made answered cards vanish into the Answered fold. Now a later-ish answer moves
                # the card to the Later tab, still open, note kept.
                if answer.strip().lower().startswith(("later", "not now")):
                    card["later"] = True
                    card["laterAt"] = now_utc()
                    card["answer"] = None
                    card["answeredAt"] = None
                else:
                    card["answer"] = answer
                    card["answeredAt"] = now_utc()
            elif path == "/api/reopen":
                # ↩️ "Change my answer": the card goes back to waiting.
                card["answer"] = None
                card["answeredAt"] = None
            elif path == "/api/later":
                # 🕐 PARK IT. {id, later: true} → the 🕐 Later tab. {id, later: false} → back to 📌 Today.
                # This only moves the card between tabs. It never touches the answer.
                later = body.get("later")
                if not isinstance(later, bool):
                    return self._send(400, {"error": "later must be true or false"})
                card["later"] = later
                card["laterAt"] = now_utc() if later else None
            elif path == "/api/done":
                # 🧹 your AI acted on the answer, so the card can go away.
                cards = [c for c in cards if c.get("id") != cid]
                write_cards(cards)
                return self._send(200, {"removed": cid})
            else:
                return self._send(404, {"error": "not found"})
            write_cards(cards)
            return self._send(200, card)


if __name__ == "__main__":
    if not KEY:
        raise SystemExit("No DESK_KEY found (in desk.env or the environment). "
                         "Refusing to serve an unlocked desk. See the top of this file.")
    print(f"📥 The desk is open at http://{HOST}:{PORT}/  (first time: add ?k=YOUR_KEY to that address)")
    ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()
