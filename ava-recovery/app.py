import os
import random
import string
from datetime import datetime
from functools import wraps

from flask import (
    Flask, render_template, request, redirect,
    url_for, session, flash, abort
)

from supabase_client import supabase
from config.services import SERVICES, SERVICE_ORDER, BRAND

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-only-change-me")


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


def generate_case_number(service_slug: str) -> str:
    year = datetime.utcnow().year
    suffix = "".join(random.choices(string.digits, k=6))
    prefix = service_slug[:3].upper()
    return f"AVA-{year}-{prefix}-{suffix}"


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
                session["user"] = {
                    "id": result.user.id,
                    "email": result.user.email,
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


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
