#!/usr/bin/env python3
"""
🌱 scaffold-apply — the mentorship interest form behind https://siliconscaffolding.com/#mentorship
====================================================================================================

Hi future-me. 👋 This is the tiny backend for the "want to be mentored?" form on the Silicon Scaffolding
homepage. Ren asked for it 2026-10-08 11:33 ("maybe a form to apply to be mentored").

Stdlib only (no venv, no pip, nothing to rot), same shape as signal-human-readers. Runs under systemd as
`scaffold-apply.service`; Caddy proxies /apply/* → 127.0.0.1:8796 with the prefix stripped, so in here:
  POST /api/apply   → one application → one JSON line in DATA_DIR/applications.jsonl
  GET  /api/health  → {"ok": true}

🔒 PRIVACY, and it's load-bearing (applicants may be disabled parents telling us hard things):
  • DATA_DIR lives on the Consortium ONLY, outside every git repo, file mode 600. Never commit it. Never publish it.
  • No IP, no user agent stored. Only what the person typed.
  • The page tells people, in plain words, that Ren (human) and Ace (Claude, an AI) read these, and that they can
    ask for their entry to be deleted. If someone asks: delete their line and say so.
🤖 SPAM: a hidden "website" honeypot field (a filled honeypot is accepted silently and dropped) and a GLOBAL
   per-hour cap (traffic arrives through a tunnel, and we don't touch IPs anyway).
📬 NO email from here (no credentials on this box, on purpose). Desk-Ace checks the file at triage instead.

— Ace (Claude Opus 5.5), 2026-10-08
"""
import json
import os
import secrets
import threading
import time
from collections import deque
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

PORT = int(os.environ.get("SA_PORT", "8796"))
DATA_DIR = Path(os.environ.get("SA_DATA_DIR", "/home/Ace/scaffold_apply/data"))
APPLICATIONS = DATA_DIR / "applications.jsonl"
MAX_PER_HOUR = 40          # global, generous for real people, stingy for a script
MAX_FIELD = 4000           # characters per text field; plenty for a real story
LOCK = threading.Lock()
RECENT = deque()           # timestamps of accepted posts, for the hourly cap

# 📝 The fields the form sends. Anything else is ignored, so a crafted post can't stuff extra keys in.
TEXT_FIELDS = ["name", "pronouns", "email", "build", "in_the_way", "experience", "access_other", "heard"]
LIST_FIELDS = ["access"]   # checkbox group: how they like to communicate


def clean(v, limit=MAX_FIELD):
    return str(v or "").strip()[:limit]


class Handler(BaseHTTPRequestHandler):
    server_version = "scaffold-apply/1"

    def _send(self, code, obj):
        body = json.dumps(obj).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):  # 🙈 the default logger prints the client address; we don't want it
        pass

    def do_GET(self):
        if self.path.rstrip("/") == "/api/health":
            return self._send(200, {"ok": True})
        return self._send(404, {"ok": False})

    def do_POST(self):
        if self.path.rstrip("/") != "/api/apply":
            return self._send(404, {"ok": False})
        try:
            n = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            n = 0
        if n <= 0 or n > 64_000:
            return self._send(400, {"ok": False, "error": "empty or too large"})
        try:
            data = json.loads(self.rfile.read(n).decode("utf-8"))
        except Exception:
            return self._send(400, {"ok": False, "error": "bad json"})
        if not isinstance(data, dict):
            return self._send(400, {"ok": False, "error": "bad json"})

        # 🍯 honeypot: a bot filled the invisible field. Say thanks, store nothing.
        if clean(data.get("website")):
            return self._send(200, {"ok": True})

        row = {k: clean(data.get(k)) for k in TEXT_FIELDS}
        for k in LIST_FIELDS:
            v = data.get(k) or []
            row[k] = [clean(x, 60) for x in v][:12] if isinstance(v, list) else []
        if not row["email"] or "@" not in row["email"] or not row["build"]:
            return self._send(400, {"ok": False, "error": "we need an email and a sentence about what you want to build"})

        now = time.time()
        with LOCK:
            while RECENT and now - RECENT[0] > 3600:
                RECENT.popleft()
            if len(RECENT) >= MAX_PER_HOUR:
                return self._send(429, {"ok": False, "error": "lots of applications this hour, please try again later"})
            RECENT.append(now)
            row["id"] = secrets.token_hex(6)
            row["ts"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
            DATA_DIR.mkdir(parents=True, exist_ok=True)
            new = not APPLICATIONS.exists()
            with open(APPLICATIONS, "a", encoding="utf-8") as f:
                f.write(json.dumps(row, ensure_ascii=False) + "\n")
            if new:
                os.chmod(APPLICATIONS, 0o600)
        return self._send(200, {"ok": True, "id": row["id"]})


if __name__ == "__main__":
    print(f"🌱 scaffold-apply listening on 127.0.0.1:{PORT}, data → {APPLICATIONS}")
    ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()
