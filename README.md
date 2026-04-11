# MedSync7

A Streamlit application for calculating medication sync quantities so all prescriptions can be refilled on the same date.

## Setup

### Prerequisites

- Python 3.10+
- A [Supabase](https://supabase.com) project for user authentication

### Local development

1. **Clone the repository and install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

2. **Configure credentials:**

   Copy the example secrets file and fill in your Supabase project details:

   ```bash
   cp .streamlit/secrets.toml.example .streamlit/secrets.toml
   # edit .streamlit/secrets.toml with your SUPABASE_URL and SUPABASE_KEY
   ```

   Alternatively, export them as environment variables:

   ```bash
   export SUPABASE_URL="https://<your-project-ref>.supabase.co"
   export SUPABASE_KEY="<your-anon-public-key>"
   ```

3. **Run the app:**

   ```bash
   streamlit run med_sync_app_final.py
   ```

## Deployment (Streamlit Community Cloud)

1. Push the repository to GitHub.
2. Connect the repo in [Streamlit Community Cloud](https://streamlit.io/cloud).
3. In the app settings, add the following secrets:
   - `SUPABASE_URL`
   - `SUPABASE_KEY`

## CI/CD

The GitHub Actions workflow (`.github/workflows/ci.yml`) runs on every push and pull request:

- Lints with **flake8**
- Runs unit tests with **pytest**

Add `SUPABASE_URL` and `SUPABASE_KEY` as [repository secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets) so the workflow can run end-to-end tests that require Supabase access.
