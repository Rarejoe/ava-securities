import os
from supabase import create_client, Client

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_ANON_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError(
        "Missing SUPABASE_URL / SUPABASE_ANON_KEY environment variables. "
        "Copy .env.example to .env and fill them in (see README)."
    )

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
