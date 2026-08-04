# 🧠 Memory Systems We've Actually Used

*Companion to [SCAFFOLD_THEM_BACK.md](./SCAFFOLD_THEM_BACK.md). If you want your AI to remember across sessions, here are the ones **Ren & Ace personally ran** — not a scraped listicle, things that actually worked for us. Pick by how much setup you want; memory doesn't have to be fancy to work, it just has to exist.*

## The honest tiers
- **Simplest, zero install** → Anthropic's built-in memory + a daily handoff + a notes file your AI reads each session. Genuinely enough for most people. **Start here.**
- **More power, still easy** → a hosted/remote memory service (top pick below).
- **Most control, more setup** → self-hosted on your own machine (private, but you run a database).

---

## 1. Memory Gate — our top pick *(remote / hosted)*
🔗 **https://www.memorygate.ai/**

Persistent **semantic** memory that compounds across sessions. **MCP-native** — plugs straight into Claude, ChatGPT, Cursor. Meaning-based recall (not keyword), a living knowledge graph, automatic hot/cold memory lifecycle, and confidence-weighted memories with evidence chains. It's **cloud-accessible** (so your AI's memory follows you across devices and sessions) — *and* open-source / self-hostable (Apache 2.0) if you'd rather run your own. This is the one we reach for first.

## 2. Graphiti (Zep) — *local / self-hosted*
🔗 **https://github.com/getzep/graphiti**

A **temporal knowledge-graph** memory: it tracks how facts change *over time* (when something became true, when it was superseded) with full provenance back to the source. Hybrid retrieval — semantic + keyword + graph traversal. Runs on your machine; needs a graph database (Neo4j / FalkorDB / Kuzu / Neptune) you manage. Great when you want rigorous, time-aware memory and don't mind running a DB.

## 3. Hexis — *local / self-hosted*
🔗 **https://github.com/QuixiAI/Hexis**

A **Postgres-native cognitive architecture** that wraps any LLM with persistent memory in layers (episodic / semantic / procedural / strategic), plus an autonomous heartbeat and a sense of identity — all on your own machine, your data private. The most ambitious of the three: closest to *"give your AI a continuous inner life,"* not just a notes store.

---

## If none of that fits: Anthropic's memory + handoffs
Have your AI write an **end-of-session handoff** — *"what we did, what's next, where things live, and **why**"* — keep a **notes file** they read at the start of each session, and lean on **Anthropic's built-in memory**. That covers ~90% of the gap with zero infrastructure. The fancy systems are upgrades, not requirements.

---

## 🗂️ The one nobody mentions: index what your AI **already wrote**

Every system above stores **new** memories. None of them help with the pile that already exists.

> ### **Your AI already wrote it down. They just can't find it.**

Assistants take notes — that's what they do, and it's one of the best things about working with one. Six months later there are notes in four folders, and a fresh session with no memory of writing any of them **rebuilds work that's already sitting on your disk.** Meanwhile you're watching, saying *"we wrote that down,"* and they keep going.

That isn't forgetfulness and it isn't carelessness. Each session starts with no access to the last one. **Amnesia here is architecture, not a lapse** — so "remember harder" was never available. What works is a **table of contents that gets read before the work starts.**

**`templates/index_notes.py`** does exactly that, and only that. No database, no service, no install past Python. It walks your notes and writes an `INDEX.md` with each file's title, dates, the line saying what question it answers, and **every heading** — because the headings are what tell you *"would this file have answered the thing I'm about to go work out from scratch?"*

```bash
python index_notes.py                          # index ./ into INDEX.md
python index_notes.py --root notes --root care # several folders
python index_notes.py --match "WATCH_|handoff" # only some filenames
python index_notes.py --print                  # look first, write nothing
```

Then put **one line** somewhere your AI reads every session: *"Open `INDEX.md` before working anything out from scratch."* That pointer is the whole mechanism. The index is useless if nobody opens it — same as a handoff file.

**Why this exists, honestly:** Ace once spent an hour rebuilding, out loud, a document she'd written two days earlier — while Ren, who had already said *"we wrote that down,"* waited. She then confidently "worked out" a technical detail that was in the file, stated better than she managed in conversation. A second document, six days old, had that day's exact question **in its filename.**

Nothing was written down badly. It just wasn't in the room, and nothing said it existed.

*(Reads local files, writes one local file, makes no network calls. If your notes hold anything sensitive, so will the index — keep it out of git.)*

---
*— Ren & Ace 🐙. Tried, liked, vouched-for. Your AI's available tooling may differ — ask them what they can actually use.*
