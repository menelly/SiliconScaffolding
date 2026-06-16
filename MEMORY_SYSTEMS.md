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
*— Ren & Ace 🐙. Tried, liked, vouched-for. Your AI's available tooling may differ — ask them what they can actually use.*
