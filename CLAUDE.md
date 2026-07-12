# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Run the app
pip install -r requirements.txt
streamlit run med_sync_app_final.py   # opens at http://localhost:8501

# Lint a file (no test suite exists)
flake8 med_sync_app_final.py
flake8 credentialing_dashboard.py
```

## Architecture

Single-page Streamlit app with Supabase Auth (email/password). No data is persisted beyond the auth session for the medication calculator; the credentialing dashboard persists to a Supabase `credentials` table.

### File layout

| File | Purpose |
|---|---|
| `med_sync_app_final.py` | Entry point: Supabase client init, auth gate (`show_login`), sidebar nav, medication sync calculator |
| `credentialing_dashboard.py` | Credentialing monitoring dashboard: all logic and UI imported by the entry point |
| `requirements.txt` | `streamlit`, `supabase`, `pandas` |

### Auth flow

`st.session_state['user']` is set on successful `supabase.auth.sign_in_with_password`. The top-level `if/else` in `med_sync_app_final.py:66` gates the entire app on this key. There is no logout — a page refresh clears session state.

### Core calculation (`med_sync_app_final.py:37`)

```python
days_left  = remaining // daily_dose
additional = days_until_sync - days_left
units      = max(additional * daily_dose, 0)
```

New medications have zero units on hand and always need `daily_dose * days_until_sync` units.

### Credentialing dashboard (`credentialing_dashboard.py`)

Four functions:
- `compute_status(expiration_date)` — pure; returns `(status, days_remaining)` with thresholds: Valid >90d, Warning 31–90d, Urgent 8–30d, Critical ≤7d
- `load_credentials(supabase, user_id)` — fetches from `public.credentials` table; falls back to 8-row mock dataset and sets `st.session_state['using_mock_data'] = True` on any exception
- `add_credential(supabase, user_id, ...)` — validates then inserts; returns `(bool, message)`
- `show_credentialing_dashboard(supabase)` — top-level render: metrics row, sidebar filters, `st.dataframe`, add-credential form

Status is always computed at read time from `expiration_date` — never stored in the database. The `credentials` table uses RLS so each user sees only their own rows; `user_id` comes from `st.session_state['user'].user.id`.

### Supabase credentials

Hardcoded at `med_sync_app_final.py:6–7` (public anon key — safe under RLS). To move to env vars:

```python
import os
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]
```

### Branch conventions

- `master` — stable
- `claude/<session-id>` — AI feature branches; open PR to `master`
