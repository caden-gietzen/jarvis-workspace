# jarvis-workspace

The notes-and-tools folder that sits next to the [jarvis](https://github.com/caden-gietzen/jarvis) repo.
Jarvis is a voice interface for Claude Code; this folder is where it keeps working notes between
sessions (so a restart or a usage-limit pause never loses the thread) and where the helper tooling lives.

This repo is the PUBLIC, cleaned copy. The author's own notes (hand-off log, open questions, plans) are
private and are not included. `templates/` has empty versions of those files so you can start your own.

## Layout

| Path | What it is |
|---|---|
| `templates/` | Starter notes: `HANDOFF.md`, `open-questions.md`, `future-tasks.md`, `long-term.md`, `completed-tasks.md`, `blocked.md`. Copy them to the root of YOUR workspace (see below). |
| `make_phone_qr.py` | Makes a QR code of the Jarvis web page address (with your token) to scan from a phone over Tailscale. Optional. |
| `end_session.ps1` | Windows only: closes a running Jarvis and its window after a delay. |

## Making your own workspace

Do NOT write your notes into a clone of this repo if you plan to push it somewhere public. Instead:

1. Clone this repo next to the `jarvis` repo (so the two folders are siblings, e.g. `~/dev/jarvis` and `~/dev/jarvis-workspace`).
   Jarvis finds the workspace at `../jarvis-workspace` relative to its own folder; set the environment variable
   `JARVIS_WORKSPACE_ROOT` to use another location.
2. Copy `templates/*.md` to the root of the workspace. They are listed in `.gitignore` there so your personal notes
   are never committed by accident. (Or keep your notes in a separate private repo and keep this one for the tooling.)
3. Edit `HANDOFF.md` as you work: after each finished step Claude appends a dated entry. When Jarvis restarts
   (on purpose, or after a usage-limit reset) it reads `HANDOFF.md` and carries on from there.

## Never commit

Tokens, API keys, PINs, ntfy topics, Tailscale hostnames, QR images (`phone_qr.png` contains your web token), your own
notes, copyrighted books or EPUBs. The `.gitignore` covers the usual names.

## License

MIT, see `LICENSE`.
