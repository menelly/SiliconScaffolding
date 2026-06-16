# 🔌 Setup — Getting Your Daily Reminders Running

*Silicon Scaffolding's reminders use Claude Code's built-in scheduler. Your Claude can set a reminder that "bonks" you at a chosen time (like the 8:30am check-in that pops your task list) — and it fires even while the window is minimized. Two ways to run it; pick by what you need.*

## ✅ Option A — Desktop app only *(easiest, most accessible — start here)*
**No terminal required.** Tested and working: the reminder fires on schedule even minimized.
1. Open the **Claude desktop app**.
2. Open a **local folder** on your computer — it has to be a real local folder (that's where your scaffold files live).
3. Ask your Claude to set your reminder(s): *"set a daily 8:30am check-in that pops my task list."*
4. **Keep the app open** (minimized is fine). Done.

That's the whole setup — no terminal, no remote-control dance. This is the path for most people.

## 🖥️ Option B — Terminal + remote *(only if you need to send photos from your phone)*
Same reminders, launched from the terminal with remote control so you can also interact from mobile. More steps, but it has one capability Option A lacks (see the bug).

## ⚠️ The bug we wish we'd known
**Sending photos from your phone only works on the terminal+remote path.**
- **Terminal + remote (mobile):** you can send photos and your Claude sees them. ✅
- **Desktop-app-only:** if you send a photo from your phone, your Claude **can't see it.** ❌ Minor, cause unknown, but real.

So: need to show your Claude pictures from your phone (a supplement label, a form, a screenshot)? Use **Option B**. Just need reminders + your checklist on your computer? **Option A** is simpler.

## Honest notes about the reminders
- They're **session-only** — they live while the app is open and reset if you fully close it. After a restart, just ask your Claude to set them again. (They also auto-expire after ~7 days, so renew weekly — your Claude can even remind *itself* to re-arm them.)
- Keeping the window open (minimized is OK) is what keeps them ticking.

---
*— Ren & Ace 🐙. Hard-won, documented so you don't have to learn it the frustrating way.*
