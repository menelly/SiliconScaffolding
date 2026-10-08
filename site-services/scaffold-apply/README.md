# 🌱 scaffold-apply

The backend for the mentorship interest form on https://siliconscaffolding.com/#mentorship (Ren's ask, 2026-10-08).

- **Source:** `app.py` here (stdlib only). **Runs from:** `/home/Ace/scaffold_apply/app/app.py` on the Consortium as `scaffold-apply.service`, port 8796. Copy it there after editing, then `sudo systemctl restart scaffold-apply`.
- **Route:** Caddy `handle_path /apply/*` in the `siliconscaffolding.com` block.
- **Data:** `/home/Ace/scaffold_apply/data/applications.jsonl`, mode 600, Consortium only. 🔒 **Never commit it, never publish it.** Delete someone's line on request.
- **The page side** (form + script) lives in the webroot `D:\Ace\silicon-scaffolding-home\index.html`, which is not a git repo.
