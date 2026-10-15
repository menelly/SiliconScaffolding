# 📥 The Desk

**Questions waiting on you go on cards you can answer with one tap. Nothing gets lost in a file you'll never open.**

When your AI helper needs a decision from you (*"can I send this email?"*, *"which day works for the dentist?"*, *"is it okay if I file this?"*), the easy thing for the AI is to write it down in a notes file. Those files are shaped for the AI, not for you, and on a hard day you won't open them. So the question sits there, and the thing waits forever.

The Desk fixes that. Your helper puts each question on a **card** with big buttons. You open one page on your phone or computer, tap an answer (and add a note if you want), and your helper reads it back. That's the whole thing.

It came from a real household's accommodation: a disabled person who said, more or less, *"I am never going to read those files. Give me one screen I can open and answer things."* This is that screen, with the personal bits taken out.

## 📌 Today and 🕐 Later

There are two tabs:

- **📌 Today** is what actually needs you now.
- **🕐 Later** is where things go when they're real but not today's problem.

Every card has a quiet **"Later →"** button. Tapping it parks the card. It doesn't answer it, delete it, or count against you; it just waits in the Later tab until you bring it back with **"← Today"**. You can still answer a card from either tab.

This is on purpose. A list where everything is due at once is a list you stop opening. Parking something is a decision, and a perfectly good one. **No guilt in the Later tab.**

Your helper can also post a card straight into Later when it isn't urgent, so Today stays calm.

## What's in this folder

| file | what it is |
|---|---|
| `desk_server.py` | the little server that holds the cards and serves the page |
| `index.html` | the page you look at and tap |
| `desk.py` | the tool your AI helper uses to post cards and read answers |
| `cards.json` | your cards (created the first time a card is posted; stays on your computer) |
| `desk.env` | your secret key (you create this; stays on your computer) |

Everything uses plain Python that comes with Python itself. Nothing to install.

## How to run it on your computer

You (or your AI helper; this is a great thing to hand them) do this once:

1. **Install Python** if you don't have it (python.org). Any recent version.
2. **Make up a secret key.** Any long random word, like `pancake-violet-harbor-9172`. It's what keeps other people from seeing your cards.
3. **Make a file called `desk.env`** in this folder, with one line:
   ```
   DESK_KEY=pancake-violet-harbor-9172
   ```
   (Use your own word, not this one.)
4. **Start the server.** Open a terminal in this folder and run:
   ```
   python desk_server.py
   ```
   Leave that window open. (If something else is already using port 8797, add a line `DESK_PORT=8798` to `desk.env`.)
5. **Open the page once with your key on the end:**
   `http://127.0.0.1:8797/?k=pancake-violet-harbor-9172`
   The page remembers the key on that device and tidies it out of the address bar. After that, plain `http://127.0.0.1:8797/` works. Bookmark it.

If the page ever says *"This desk is locked,"* just open the address with `?k=YOUR_KEY` on the end again.

## How your AI helper posts a card

Your helper runs `desk.py` from this folder (it reads the same `desk.env`, so it already knows the key):

```
python desk.py post "Which day works for the dentist?" "They have Tuesday 10am or Thursday 2pm." --options "Tuesday" "Thursday" "Neither"
```

Other handy versions:

```
python desk.py post "Library books are due Friday" --kind fyi      # just letting you know
python desk.py post "Pick a paint colour for the hallway" "No rush." --later   # straight to 🕐 Later
python desk.py post "Read this before Monday" "Two pages." --kind read --link https://example.com
```

Then, to see what you decided:

```
python desk.py answers     # every answered card, with your note
python desk.py list        # everything, answered or not
python desk.py done <id>   # tidy a card away once the answer's been acted on
```

No buttons given? The card gets **Yes / No / Later**.

### A note for the AI reading this 🤖

If you're the helper: this is now where questions for your person go. A few manners that make it work:

- **Plain words.** Your person is not an AI. No jargon, no file paths unless they have to click one.
- **One question per card, two to four buttons.** If it needs an essay, it isn't a card yet.
- **Check it isn't already decided** before you ask. Being asked to re-decide costs the same as a new question.
- **Not urgent? Use `--later`.** Today should only hold what needs them today.
- **Read the answers back, act on them, then `done` the card.** A desk full of answered cards nobody acted on is just a nicer-looking pile.
- **Never stack up nags.** The Desk is a place to *find* things, not a pressure machine.

## Seeing it from your phone

Out of the box the server only answers **this computer** (that's what `127.0.0.1` means). That's the safe default.

To use it from your phone, the simplest safe options are:

- **Same Wi-Fi only:** add `DESK_HOST=0.0.0.0` to `desk.env`, restart, and open `http://<your computer's local address>:8797/?k=YOUR_KEY` on the phone. Anyone on that Wi-Fi who has the key could see the cards, so only do this on a network you trust.
- **From anywhere:** put it behind something that adds HTTPS, like a private network app (Tailscale and similar) or a web server you already run. Don't put the plain server straight on the open internet: the key travels in every request, and without HTTPS it travels unprotected.

If that paragraph is a lot, it's a perfectly good thing to ask your AI helper to set up with you.

## What it deliberately doesn't do

- **No accounts, no cloud, no tracking.** Your cards are one file on your computer.
- **No moving parts on the screen.** Switching tabs just swaps the list; nothing slides, fades or bounces.
- **Easy reading.** It uses Atkinson Hyperlegible (a font made for low-vision readers), big buttons, and follows your device's light or dark setting.

---

*Part of [Silicon Scaffolding](../../README.md). Scaffolding, not medical advice. Use what helps, ignore what doesn't, make it yours.*
