# AVA — Account & Funds Recovery Case Tracker

A self-service tool for tracking your own account-recovery efforts
(Gmail, iCloud, social media) and filing structured records of money
you believe was lost to a scam. AVA never charges a fee, never asks
for payment in crypto or otherwise, and never claims to recover
anything on your behalf — it's a personal case log, built so the
*data model, forms, and pricing are trivially editable* for whatever
your final-year project brief actually needs.

## Stack
- **Backend:** Flask (Python)
- **Auth + Database + Storage:** Supabase
- **Hosting:** Render

## 1. Set up Supabase
1. Create a project at supabase.com.
2. Go to **SQL Editor** → paste the contents of `supabase/schema.sql` → **Run**.
3. Go to **Storage** → **New bucket** → name it `attachments` → keep it **private**.
4. Add the two storage policies commented at the bottom of `schema.sql`
   (Storage → attachments → Policies → New policy → paste each SQL block).
5. Go to **Project Settings → API** → copy your **Project URL** and **anon public key**.

## 2. Configure locally
```bash
cp .env.example .env
# paste your SUPABASE_URL and SUPABASE_ANON_KEY into .env
```

Install dependencies and run:
```bash
python -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```
Visit `http://localhost:5000`.

## 3. Editing services / pricing
Everything about what's offered — categories, form fields, which
fields are required, minimum-fields-to-submit rule, and price — lives
in **`config/services.py`**. Nothing else needs to change:

- Add a new service → copy an existing dict entry inside `SERVICES`,
  give it a new key, add it to `SERVICE_ORDER`.
- Add/remove a field → edit that service's `"fields"` list.
- Change pricing → edit `"price"` / `"price_note"`.
- Change how many fields must be filled → edit `"min_fields_required"`.

The dashboard, forms, and validation are all generated from this file.

## 4. Deploy to Render
1. Push this project to a GitHub repo.
2. On Render: **New +** → **Web Service** → connect the repo.
3. Render will detect `render.yaml` automatically. If not, set manually:
   - Build command: `pip install -r requirements.txt`
   - Start command: `gunicorn app:app`
4. Under **Environment**, add:
   - `SUPABASE_URL`
   - `SUPABASE_ANON_KEY`
   - `SUPABASE_SECRET_KEY` (only needed for the admin dashboard — see below)
   - `FLASK_SECRET_KEY` (any long random string)
5. Deploy. Render gives you a live `.onrender.com` URL.

## Project structure
```
ava-recovery/
├── app.py                  # routes: auth, dashboard, dynamic service forms, admin
├── supabase_client.py      # Supabase client init
├── config/
│   └── services.py         # <-- EDIT THIS to change services/pricing/fields
├── supabase/
│   └── schema.sql           # run once in Supabase SQL editor
├── templates/               # Jinja2 templates
├── static/css/style.css     # design system
├── static/img/logo.svg      # brand mark
├── requirements.txt
├── render.yaml
└── .env.example
```

## Admin dashboard
`/admin` lists every case filed by every user, with status/service
filters and a way to change a case's status (open / in progress /
closed). It's only reachable by accounts flagged `is_admin` in the
`profiles` table.

**To get access:**
1. Register a normal account in the app first.
2. In Supabase's SQL Editor, run (swap in your email):
   ```sql
   update public.profiles
   set is_admin = true
   where id = (select id from auth.users where email = 'you@example.com');
   ```
3. Get your **secret key**: Supabase → Project Settings → API Keys →
   **Secret keys** tab → copy it, and add it as `SUPABASE_SECRET_KEY`
   in your `.env` (local) and Render's Environment Variables (deployed).
4. Log out and back in (so your session picks up the admin flag), then
   an **Admin** link appears in the top nav.

The admin dashboard uses the secret key specifically because it needs
to see every user's cases — your regular `SUPABASE_ANON_KEY` is
intentionally blocked from doing that by the Row Level Security
policies in `schema.sql`. **Never** put the secret key in any
client-side code, a template, or commit it to GitHub — it bypasses
every security policy on your database.

## Notes for your writeup
- **Data model:** one `cases` table holds every service type; the
  `service_slug` + `data` (JSONB) columns mean adding a new category
  never requires a migration.
- **Security:** Supabase Row Level Security policies ensure a user can
  only ever read/write their own rows — enforced at the database
  layer, not just in app code.
- **Extensibility:** the config-driven form system is the core design
  decision worth writing up — it's what makes the "editable pricing
  and listing file" requirement real rather than superficial.
