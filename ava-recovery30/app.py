import os
import random
import string
import requests
from decimal import Decimal
from datetime import datetime
from functools import wraps

from flask import (
    Flask, render_template, request, redirect,
    url_for, session, flash, abort
)
from supabase import create_client

from supabase_client import supabase
from config.services import SERVICES, SERVICE_ORDER, BRAND

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-only-change-me")

# Admin client — uses the SECRET key (bypasses Row Level Security).
# Only ever used server-side, only inside admin-gated routes below.
# If SUPABASE_SECRET_KEY isn't set, admin routes are simply unavailable.
_SECRET_KEY = os.environ.get("SUPABASE_SECRET_KEY")
_SUPABASE_URL = os.environ.get("SUPABASE_URL")
supabase_admin = create_client(_SUPABASE_URL, _SECRET_KEY) if _SECRET_KEY else None


# ---------------------------------------------------------------------
# Auth helpers
# ---------------------------------------------------------------------
def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("user"):
            flash("Please log in to continue.", "error")
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapped


def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("user"):
            flash("Please log in to continue.", "error")
            return redirect(url_for("login"))
        if not session["user"].get("is_admin"):
            abort(403)
        if supabase_admin is None:
            flash("Admin access isn't configured on this server (missing SUPABASE_SECRET_KEY).", "error")
            return redirect(url_for("dashboard"))
        return view(*args, **kwargs)
    return wrapped


def generate_case_number(service_slug: str) -> str:
    year = datetime.utcnow().year
    suffix = "".join(random.choices(string.digits, k=6))
    prefix = service_slug[:3].upper()
    return f"AVA-{year}-{prefix}-{suffix}"
    
def get_btc_price():
     r = requests.get("https://mempool.space/api/v1/prices", timeout=10)
     r.raise_for_status()
     return Decimal(str(r.json()["USD"]))


def verify_btc_payment(amount_btc):
     address = os.environ["BTC_WALLET_ADDRESS"]

     r = requests.get(
         f"https://mempool.space/api/address/{address}/txs",
         timeout=10
     )
     r.raise_for_status()

     for tx in r.json():
         if not tx.get("status", {}).get("confirmed"):
             continue

         for output in tx.get("vout", []):
             if output.get("scriptpubkey_address") != address:
                 continue

             received = Decimal(output.get("value", 0)) / Decimal(100_000_000)

             if received >= Decimal(str(amount_btc)):
                 return tx["txid"]

return None

# ---------------------------------------------------------------------
# Auth routes
# ---------------------------------------------------------------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        if not email or not password:
            flash("Email and password are required.", "error")
            return render_template("register.html", brand=BRAND)

        try:
            result = supabase.auth.sign_up({
                "email": email,
                "password": password,
                "options": {"data": {"full_name": full_name}},
            })
            if result.user:
                flash("Account created. Check your email to confirm, then log in.", "success")
                return redirect(url_for("login"))
        except Exception as e:
            flash(f"Could not create account: {e}", "error")

    return render_template("register.html", brand=BRAND)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        try:
            result = supabase.auth.sign_in_with_password({
                "email": email,
                "password": password,
            })
            if result.user:
                profile_resp = (
                    supabase.table("profiles")
                    .select("is_admin")
                    .eq("id", result.user.id)
                    .single()
                    .execute()
                )
                is_admin = bool(profile_resp.data and profile_resp.data.get("is_admin"))

                session["user"] = {
                    "id": result.user.id,
                    "email": result.user.email,
                    "is_admin": is_admin,
                }
                session["access_token"] = result.session.access_token
                flash("Welcome back.", "success")
                return redirect(url_for("dashboard"))
        except Exception as e:
            flash("Invalid email or password.", "error")

    return render_template("login.html", brand=BRAND)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# ---------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------
@app.route("/")
def index():
    if session.get("user"):
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/dashboard")
@login_required
def dashboard():
    services = [SERVICES[slug] for slug in SERVICE_ORDER]

    cases_resp = (
        supabase.table("cases")
        .select("*")
        .eq("user_id", session["user"]["id"])
        .order("created_at", desc=True)
        .execute()
    )
    cases = cases_resp.data or []

    return render_template(
        "dashboard.html",
        brand=BRAND,
        services=services,
        cases=cases,
    )


# ---------------------------------------------------------------------
# Dynamic service form (one route handles every service in config)
# ---------------------------------------------------------------------
@app.route("/service/<slug>", methods=["GET", "POST"])
@login_required
def service_form(slug):
    service = SERVICES.get(slug)
    if not service:
        abort(404)

    if request.method == "POST":
        filled = {}
        for field in service["fields"]:
            if field["type"] == "file":
                continue  # handled separately below
            value = request.form.get(field["key"], "").strip()
            if value:
                filled[field["key"]] = value

        min_required = service.get("min_fields_required", 0)
        if len(filled) < min_required:
            flash(
                f"Please fill in at least {min_required} field"
                f"{'s' if min_required != 1 else ''} before submitting.",
                "error",
            )
            return render_template("service_form.html", brand=BRAND, service=service)

        # Handle file upload(s) -> Supabase Storage, private bucket "attachments"
        uploaded_paths = []
        files = request.files.getlist("evidence")
        for f in files:
            if f and f.filename:
                path = f"{session['user']['id']}/{slug}/{f.filename}"
                try:
                    supabase.storage.from_("attachments").upload(
                        path, f.read(), {"content-type": f.content_type}
                    )
                    uploaded_paths.append(path)
                except Exception as e:
                    flash(f"Could not upload {f.filename}: {e}", "error")
        if uploaded_paths:
            filled["evidence_paths"] = uploaded_paths

        case_number = generate_case_number(slug)
        try:
            supabase.table("cases").insert({
                "user_id": session["user"]["id"],
                "service_slug": slug,
                "case_number": case_number,
                "data": filled,
                "status": "open",
            }).execute()
            flash(f"Case {case_number} filed successfully.", "success")
            return redirect(url_for("dashboard"))
        except Exception as e:
            flash(f"Could not file case: {e}", "error")

    return render_template("service_form.html", brand=BRAND, service=service)


@app.route("/case/<case_id>")
@login_required
def case_detail(case_id):
    resp = (
        supabase.table("cases")
        .select("*")
        .eq("id", case_id)
        .eq("user_id", session["user"]["id"])
        .single()
        .execute()
    )
    case = resp.data
    if not case:
        abort(404)
    service = SERVICES.get(case["service_slug"])
    return render_template("case_detail.html", brand=BRAND, case=case, service=service)


# ---------------------------------------------------------------------
# Admin — visible only to profiles.is_admin accounts. Uses supabase_admin
# (the secret key) so it can see every user's cases, since normal RLS
# policies intentionally restrict everyone to their own rows only.
# ---------------------------------------------------------------------
@app.route("/admin")
@admin_required
def admin_dashboard():
    status_filter = request.args.get("status", "all")
    service_filter = request.args.get("service", "all")

    query = supabase_admin.table("cases").select("*").order("created_at", desc=True)
    if status_filter != "all":
        query = query.eq("status", status_filter)
    if service_filter != "all":
        query = query.eq("service_slug", service_filter)
    cases = query.execute().data or []

    all_cases = supabase_admin.table("cases").select("status").execute().data or []
    counts = {"open": 0, "in_progress": 0, "closed": 0}
    for c in all_cases:
        counts[c["status"]] = counts.get(c["status"], 0) + 1

    return render_template(
        "admin_dashboard.html",
        brand=BRAND,
        cases=cases,
        counts=counts,
        total=len(all_cases),
        services=[SERVICES[s] for s in SERVICE_ORDER],
        status_filter=status_filter,
        service_filter=service_filter,
    )


@app.route("/admin/case/<case_id>")
@admin_required
def admin_case_detail(case_id):
    resp = supabase_admin.table("cases").select("*").eq("id", case_id).single().execute()
    case = resp.data
    if not case:
        abort(404)
    service = SERVICES.get(case["service_slug"])
    return render_template("admin_case_detail.html", brand=BRAND, case=case, service=service)


@app.route("/admin/case/<case_id>/status", methods=["POST"])
@admin_required
def admin_update_status(case_id):
    new_status = request.form.get("status")
    if new_status not in ("open", "in_progress", "closed"):
        abort(400)
    supabase_admin.table("cases").update({
        "status": new_status,
        "updated_at": datetime.utcnow().isoformat(),
    }).eq("id", case_id).execute()
    flash("Case status updated.", "success")
    return redirect(url_for("admin_case_detail", case_id=case_id))


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
