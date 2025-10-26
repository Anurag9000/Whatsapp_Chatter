Whatsapp Chatter
=================

Python automation that replies on WhatsApp Web using your personal tone and style, powered by Llama 3.2 (3B) via Ollama.

Quick Start
-----------
- Requirements: Python 3.10+, Chrome, Selenium (auto-manages driver), and Ollama with `llama3.2:3b` pulled.
- Create a `contexts/` folder locally (ignored by Git). Add one file per person, e.g. `contexts/srishti.txt`.
- Install deps in a venv, then run the CLI (examples below).

Features
--------
- Context-driven replies (per-contact text files) and your name via `--me`.
- Full conversation context considered; model outputs only the next reply.
- Continuous auto-reply loop with optional dry-run.
- Selenium automation to select a contact and send messages.
- Basic tests for context loading and prompt building.

Setup
-----
1) Create and activate a virtual environment (Windows PowerShell):
   - `python -m venv .venv`
   - `.\.venv\Scripts\Activate.ps1`
   - `python -m pip install --upgrade pip`
   - `pip install -r requirements.txt`

2) Prepare Ollama and model:
   - Install/start Ollama
   - `ollama pull llama3.2:3b`

3) Add context file:
   - `contexts/<person>.txt` (ignored by Git). Put examples of how you text, tone, phrases, and boundaries for that person.

Running
-------
- Dry-run continuous (recommended first):
  - `python -m whatsapp_chatter.cli "<Contact Name>" --me "<Your Name>" --dry-run`

- Persistent login across runs (optional): create a folder like `C:\WhatsAppProfile` and pass it:
  - `python -m whatsapp_chatter.cli "<Contact Name>" --me "<Your Name>" --user-data-dir "C:\\WhatsAppProfile" --dry-run`

- Send real replies (remove `--dry-run`):
  - `python -m whatsapp_chatter.cli "<Contact Name>" --me "<Your Name>" --user-data-dir "C:\\WhatsAppProfile"`

- One-shot reply then exit (dry-run):
  - `python -m whatsapp_chatter.cli "<Contact Name>" --me "<Your Name>" --once --dry-run`

New Modes
---------
- Preview typing (no send): add `--preview` to type the generated message into the composer without pressing Enter. Useful to review before sending.
  - Example: `python -m whatsapp_chatter.cli "<Contact Name>" --me "<Your Name>" --preview`

- Initiator mode: add `--initiate` to compose an opener proactively using your context and conversation history.
  - Dry-run/preview/send all apply here as well.
  - Example: `python -m whatsapp_chatter.cli "<Contact Name>" --me "<Your Name>" --initiate --preview`

CLI Flags
---------
- `--me`: Your name for the model context.
- `--context`: Specific context filename under `contexts/` (defaults to `<person>.txt`).
- `--dry-run`: Print reply to terminal instead of sending (default recommended while testing).
- `--interval`: Polling interval in seconds for continuous mode (default 6).
- `--headless`: Run Chrome headless (login QR requires non-headless initially).
- `--once`: Generate one reply and exit.

Troubleshooting
---------------
- Stuck on WhatsApp Web: ensure you scan the QR in the Selenium window on first run.
- Contact not selected: use the exact name as shown in WhatsApp.
- No messages read/sent: with `--dry-run`, the app will not type/send, it only prints.
- UI changes: the app tries multiple selectors for the search box and waits for the composer.

Logging
-------
- The CLI logs step-by-step actions and exceptions to the terminal.

Notes
-----
- The `contexts/` directory is ignored by Git per `.gitignore`.
- This project is for educational/automation purposes. Use responsibly and respect WhatsApp terms of service.
