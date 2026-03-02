# CLAUDE.md — MedSync7

## Project Overview

MedSync7 is a single-page Streamlit web application that helps patients synchronize medication refill dates. Given a set of existing medications (each with a daily dose and remaining units) and a new medication being added, the app calculates how many additional units of each medication are needed so that everything can be refilled on the same target date.

Authentication is handled via Supabase Auth (email/password). No data is persisted to the database beyond the auth session — the calculator operates entirely in-memory on the client side.

---

## Repository Structure

```
MedSync7/
├── med_sync_app_final.py   # Entire application: auth UI + calculator logic
├── requirements.txt        # Python dependencies (streamlit, supabase)
└── README.md               # Minimal project stub
```

This is a single-file application. All business logic, UI, and Supabase client initialization live in `med_sync_app_final.py`.

---

## Tech Stack

| Layer | Technology |
|---|---|
| UI framework | [Streamlit](https://streamlit.io/) |
| Backend / Auth | [Supabase](https://supabase.com/) (Python client) |
| Language | Python 3 |

---

## Running the App

```bash
pip install -r requirements.txt
streamlit run med_sync_app_final.py
```

The app opens in the browser at `http://localhost:8501` by default.

---

## Key Conventions

### Application flow

1. On first load, `st.session_state` does not contain `'user'`, so `show_login()` is rendered.
2. After a successful `sign_in_with_password` call, the Supabase session object is stored in `st.session_state['user']`. Streamlit reruns and the calculator is shown.
3. There is no explicit logout button in the current implementation.

### Core calculation logic (`calculate_sync_quantities`)

Located at `med_sync_app_final.py:37`.

```
days_left  = remaining // daily_dose          # integer days of supply remaining
additional = days_until_sync - days_left      # gap to fill
units      = max(additional * daily_dose, 0)  # never negative
```

The new medication is assumed to have zero units on hand; it always needs `daily_dose * days_until_sync` units.

The function returns an empty list (and shows a Streamlit error) when the sync date is in the past.

### Supabase credentials

`SUPABASE_URL` and `SUPABASE_KEY` are hardcoded at the top of `med_sync_app_final.py` (lines 6–7). The key is the public `anon` key, which is safe to expose client-side under Supabase's Row Level Security model. If credentials need to rotate or the app is deployed to multiple environments, move them to environment variables or Streamlit secrets:

```python
import os
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]
```

### Streamlit form pattern

The medication input form uses `st.form` with a single submit button (`Calculate`). All widget keys inside the form are namespaced with an index (`name_{i}`, `dose_{i}`, `remaining_{i}`) to avoid key collisions when `num_meds` changes.

---

## Development Workflow

### Branch conventions

- `master` — stable/production branch
- `claude/<session-id>` — AI-assisted feature/fix branches; always push to the designated branch and open a PR to `master`

### Making changes

1. Work on the feature branch (never commit directly to `master`).
2. Edit `med_sync_app_final.py` — it is the only source file.
3. Test locally with `streamlit run med_sync_app_final.py`.
4. Commit with a descriptive message, then push:
   ```bash
   git push -u origin <branch-name>
   ```

### Dependencies

Add new packages to `requirements.txt` (one per line, unpinned unless a specific version is required). The file currently contains:

```
streamlit
supabase
```

---

## Known Limitations / Areas for Improvement

- **No session persistence across browser reloads** — refreshing the page logs the user out because `st.session_state` is reset.
- **No logout** — a `supabase.auth.sign_out()` button should be added.
- **Credentials hardcoded** — should be moved to environment variables or Streamlit secrets for production deployments.
- **Integer-only quantities** — the calculator uses integer division (`//`) and integer multiplication; fractional doses (e.g., 0.5 tablets/day) are not supported.
- **No input validation** — empty medication names and zero-dose medications are not caught before the calculation runs.
- **No persistent medication records** — all data is entered fresh each session; Supabase database tables are not used.
