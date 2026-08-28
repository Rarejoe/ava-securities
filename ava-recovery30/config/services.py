"""
AVA — Services & Pricing Configuration
========================================
This is the ONLY file you should need to edit to add, remove, rename,
reprice, or reshape a service category. Nothing in app.py needs to
change when you edit this file — routes and forms are all generated
from SERVICES below.

Field types available:
    "text"      -> single-line text input
    "email"     -> email input (browser-validated)
    "date"      -> date picker
    "textarea"  -> multi-line box (use for descriptions)
    "select"    -> dropdown; requires "options": [...]
    "file"      -> file upload (screenshots / receipts), stored in
                   Supabase Storage bucket "attachments"

Each field:
    "key"         -> internal name, saved as this column key in the
                      submissions JSON (use snake_case, no spaces)
    "label"       -> what the user sees
    "type"        -> one of the types above]
    "required"    -> True / False (per-field requirement)
    "options"     -> only for "select" fields

Service-level:
    "min_fields_required" -> how many of this service's fields must
                              be filled before the form can submit,
                              REGARDLESS of individual "required" flags.
                              Set to 0 to disable this rule.
    "price"       -> shown on the pricing/summary step. Set to 0 or
                      None for "Free" / "No fee".
    "price_note"  -> small text under the price, e.g. "billed once"
"""

SERVICES = {
    "gmail": {
        "slug": "gmail",
        "name": "Gmail Account Recovery",
        "icon": "mail",  # maps to an icon in static/js or template
        "description": "Track and organize the steps you're taking to regain access to a Gmail account.",
        "min_fields_required": 1,
        "fields": [
            {"key": "account_email", "label": "Account email", "type": "email", "required": False},
            {"key": "last_access_date", "label": "Last known access date", "type": "date", "required": False},
            {"key": "issue_description", "label": "What happened? (brief description)", "type": "textarea", "required": False},
            {"key": "evidence", "label": "Screenshots / confirmation emails", "type": "file", "required": False},
        ],
        "price": 0,
        "price_note": "Tracking is free — this is your personal case log.",
    },
    "icloud": {
        "slug": "icloud",
        "name": "iCloud Account Recovery",
        "icon": "cloud",
        "description": "Track and organize the steps you're taking to regain access to an iCloud / Apple ID account.",
        "min_fields_required": 1,
        "fields": [
            {"key": "account_email", "label": "Apple ID email", "type": "email", "required": False},
            {"key": "last_access_date", "label": "Last known access date", "type": "date", "required": False},
            {"key": "issue_description", "label": "What happened? (brief description)", "type": "textarea", "required": False},
            {"key": "evidence", "label": "Screenshots / confirmation emails", "type": "file", "required": False},
        ],
        "price": 0,
        "price_note": "Tracking is free — this is your personal case log.",
    },
    "social_media": {
        "slug": "social_media",
        "name": "Social Media Accounts",
        "icon": "at-sign",
        "description": "Log any social account you're trying to recover — one entry per platform.",
        "min_fields_required": 1,
        "fields": [
            {"key": "platform_name", "label": "Platform (e.g. Instagram, TikTok, X)", "type": "text", "required": False},
            {"key": "account_email", "label": "Associated email", "type": "email", "required": False},
            {"key": "issue_description", "label": "Brief description", "type": "textarea", "required": False},
        ],
        "price": $200,
        "price_note": "Tracking is free — this is your personal case log.",
    },
    "lost_funds": {
        "slug": "lost_funds",
        "name": "Lost Funds Report",
        "icon": "file-text",
        "description": "File a structured record of money you believe was sent to a scam or fraudulent party — for your own records or to submit to your bank, platform, or a fraud authority.",
        "min_fields_required": 1,
        "fields": [
            {"key": "send_method", "label": "How the funds were sent (bank transfer, card, crypto, cash app, etc.)", "type": "select", "required": True,
             "options": ["Bank transfer", "Debit/credit card", "Cryptocurrency", "Cash app / mobile money", "Cash", "Other"]},
            {"key": "amount_lost", "label": "Approximate amount", "type": "text", "required": False},
            {"key": "date_sent", "label": "Date sent", "type": "date", "required": False},
            {"key": "evidence", "label": "Screenshots / receipts / transaction confirmations", "type": "file", "required": False},
            {"key": "issue_description", "label": "What happened?", "type": "textarea", "required": False},
        ],
        "price": 0,
        "price_note": "Filing a report never costs anything. AVA does not move, hold, or request money on your behalf.",
    },
}

# Order services appear on the dashboard
SERVICE_ORDER = ["gmail", "icloud", "social_media", "lost_funds"]

# Global copy you may want to tweak without digging through templates
BRAND = {
    "name": "AVA",
    "tagline": "Your account recovery case file — organized, private, yours.",
    "disclaimer": (
        "AVA is a self-service tracking tool. It does not recover accounts or funds "
        "on your behalf, and never asks you to send money, gift cards, or crypto to "
        "'unlock', 'process', or 'release' anything. If anyone asks you to pay a fee "
        "to recover lost money, that is a scam — report it instead of paying it."
    ),
}
