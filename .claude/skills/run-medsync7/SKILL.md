---
name: run-medsync7
description: Build, run, screenshot, and test MedSync7. Use when asked to start the app, take a screenshot, run the app, verify a UI change, or confirm the calculator works.
---

MedSync7 is a Streamlit app (Python). Drive it via `.claude/skills/run-medsync7/smoke.py` — it handles server launch, Playwright screenshots, and AppTest unit verification. `chromium-cli` is not available; Playwright with the bundled Chromium is used instead.

## Prerequisites

```bash
pip install -r requirements.txt --ignore-installed pyjwt
pip install playwright
```

Chromium is pre-installed at `/opt/pw-browsers/chromium-1194/chrome-linux/chrome`. No `apt-get` needed.

## Run (agent path)

```bash
# Test calculation logic without a browser (fastest — use this for PR verification)
python .claude/skills/run-medsync7/smoke.py test

# Screenshot the calculator (launches a temporary server on :8502, no auth required)
python .claude/skills/run-medsync7/smoke.py screenshot-calc

# Screenshot the login page (requires server already running on :8501)
python .claude/skills/run-medsync7/smoke.py screenshot

# All of the above
python .claude/skills/run-medsync7/smoke.py all
```

Screenshots land in `/tmp/shots/`.

| command | what it does |
|---|---|
| `test` | AppTest smoke: auth bypass → fill Metformin+Lisinopril → calculate → assert "Sync Plan" renders |
| `screenshot-calc` | Launches patched server on :8502, Playwright screenshot of calculator → `/tmp/shots/calculator.png` |
| `screenshot` | Playwright screenshot of login page on live :8501 server → `/tmp/shots/login.png` |
| `all` | `screenshot-calc` + `test` |

### What `test` verifies

Sets `session_state["user"] = True` to bypass Supabase auth, then drives AppTest:
- `number_input[0]` → num existing meds
- `text_input(key="name_0")`, `number_input(key="dose_0")`, `number_input(key="remaining_0")` → med fields
- `text_input(key="new_name")`, `number_input(key="new_dose")` → new med fields
- `date_input[0]` → sync date
- `button[0].click()` → form submit (NOT `form_submit_button` — absent in this Streamlit version)

## Run (human path)

```bash
streamlit run med_sync_app_final.py   # → http://localhost:8501, Ctrl-C to stop
```

## Gotchas

- **`chromium-cli` not available.** Playwright is used instead. Chromium lives at `/opt/pw-browsers/chromium-1194/chrome-linux/chrome` — always pass `executable_path` explicitly.
- **PyJWT system conflict.** `pip install -r requirements.txt` fails on PyJWT 2.7.0 installed by Debian. Fix: `--ignore-installed pyjwt`.
- **`wait-for text=Login` fires too early.** Streamlit renders the page title before the React form mounts. Wait on `input[aria-label='Email']` instead.
- **`AppTest` has no `form_submit_button`.** Use `button[0].click()` to submit the calculator form in Streamlit 1.57.
- **Auth is Supabase-gated.** Real login requires live Supabase credentials. The driver's `test` command and `screenshot-calc` both bypass auth via `session_state["user"] = True` — no credentials needed.
- **`screenshot` needs a running server.** Start one first: `streamlit run med_sync_app_final.py --server.headless true &` and poll `:8501` before calling.
