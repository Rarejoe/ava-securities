"""
AVA Account Recovery Platform - Service Configuration

Field types available:
- "text"        -> single-line text input
- "email"       -> email input
- "date"        -> date picker
- "textarea"    -> multi-line box
- "select"      -> dropdown; requires "options": […]
- "file"        -> file upload, stored in Supabase Storage bucket
- "attachments" -> attachment storage

Each field requires:
- "key"       -> internal name saved in the case data JSON
- "label"     -> what the user sees
- "type"      -> field type
- "required"  -> True / False
- "options"   -> only for select fields

Service-level settings:
- "min_fields_required" -> minimum number of fields that must be filled
  before submission. Set to 0 to disable.
- "price"               -> service price in USD.
- "payment_required"    -> whether Bitcoin payment is required.
- "price_note"          -> text displayed underneath the price.

NOTE:
All services currently have payment_required=True and price=0.
Change "price" whenever you are ready to set a fee.
"""

SERVICES = {
    # ─────────────────────────────────────────────────────────────────
    # Gmail Account Recovery
    # ─────────────────────────────────────────────────────────────────
    "gmail": {
        "slug": "gmail",
        "name": "Gmail Account Recovery",
        "icon": "mail",
        "description": (
            "Track and organize the steps you're taking to regain "
            "access to a Gmail account."
        ),
        "min_fields_required": 1,
        "payment_required": True,
        "price": 500,
        "price_note": "One-time service fee.",
        "fields": [
            {
                "key": "account_email",
                "label": "Account email",
                "type": "email",
                "required": False,
            },
            {
                "key": "last_access_date",
                "label": "Last known access date",
                "type": "date",
                "required": False,
            },
            {
                "key": "issue_description",
                "label": "What happened? (brief description)",
                "type": "textarea",
                "required": False,
            },
            {
                "key": "contact_email",
                "label": "How can we reach you?",
                "type": "email",
                "placeholder": "Type in email address",
                "required": False,
            },
            {
                "key": "contact_phone",
                "label": "How can we reach you?",
                "type": "text",
                "placeholder": "Type in phone number",
                "required": False,
            },
            {
                "key": "evidence",
                "label": "Screenshots / confirmation emails",
                "type": "file",
                "required": False,
            },
        ],
    },
    # ─────────────────────────────────────────────────────────────────
    # iCloud Account Recovery
    # ─────────────────────────────────────────────────────────────────
    "icloud": {
        "slug": "icloud",
        "name": "iCloud Account Recovery",
        "icon": "cloud",
        "description": (
            "Track and organize the steps you're taking to regain "
            "access to an iCloud / Apple ID account."
        ),
        "min_fields_required": 1,
        "payment_required": True,
        "price": 0,
        "price_note": "One-time service fee.",
        "fields": [
            {
                "key": "account_email",
                "label": "Apple ID email",
                "type": "email",
                "required": False,
            },
            {
                "key": "last_access_date",
                "label": "Last known access date",
                "type": "date",
                "required": False,
            },
            {
                "key": "issue_description",
                "label": "What happened? (brief description)",
                "type": "textarea",
                "required": False,
            },
            {
                "key": "contact_email",
                "label":"How can we reach you?",
                "type": "email",
                "required": False,
            },
            {
                "key": "contact_phone",
                "label": "How can we reach you?",
                "type": "text",
                "required": False,
            },
            {
                "key": "evidence",
                "label": "Screenshots / confirmation emails",
                "type": "file",
                "required": False,
            },
        ],
    },
    # ─────────────────────────────────────────────────────────────────
    # Social Media Accounts
    # ─────────────────────────────────────────────────────────────────
    "social_media": {
        "slug": "social_media",
        "name": "Social Media Accounts",
        "icon": "at-sign",
        "description": (
            "Log any social account you're trying to recover — "
            "one entry per platform."
        ),
        "min_fields_required": 1,
        "payment_required": True,
        "price": 0,
        "price_note": "One-time service fee.",
        "fields": [
            {
                "key": "platform_name",
                "label": "Platform (e.g. Instagram, TikTok, X)",
                "type": "text",
                "required": False,
            },
            {
                "key": "account_email",
                "label": "Associated email",
                "type": "email",
                "required": False,
            },
            {
                "key": "issue_description",
                "label": "Brief description",
                "type": "textarea",
                "required": False,
            },
            {
                "key": "contact_email",
                "label": "Email address for updates",
                "type": "email",
                "required": False,
            },
            {
                "key": "contact_phone",
                "label": "Phone number for updates",
                "type": "text",
                "required": False,
            },
        ],
    },
    # ─────────────────────────────────────────────────────────────────
    # Lost Funds Report
    # ─────────────────────────────────────────────────────────────────
    "lost_funds": {
        "slug": "lost_funds",
        "name": "Lost Funds Report",
        "icon": "file-text",
        "description": (
            "File a structured record of money you believe was sent "
            "to a scam or fraudulent party — for your own records or "
            "to submit to your bank, platform, or a fraud authority."
        ),
        "min_fields_required": 1,
        "payment_required": True,
        "price": 0,
        "price_note": "One-time service fee.",
        "fields": [
            {
                "key": "send_method",
                "label": (
                    "How the funds were sent "
                    "(bank transfer, card, crypto, cash app, etc.)"
                ),
                "type": "select",
                "required": True,
                "options": [
                    "Bank transfer",
                    "Debit/credit card",
                    "Cryptocurrency",
                    "Cash app / mobile money",
                    "Cash",
                    "Other",
                ],
            },
            {
                "key": "amount_lost",
                "label": "Approximate amount",
                "type": "text",
                "required": False,
            },
            {
                "key": "date_sent",
                "label": "Date sent",
                "type": "date",
                "required": False,
            },
            {
                "key": "issue_description",
                "label": "What happened?",
                "type": "textarea",
                "required": False,
            },
            {
                "key": "contact_email",
                "label": "Email address for updates",
                "type": "email",
                "required": False,
            },
            {
                "key": "contact_phone",
                "label": "Phone number for updates",
                "type": "text",
                "required": False,
            },
            {
                "key": "evidence",
                "label": "Screenshots / receipts / transaction confirmations",
                "type": "file",
                "required": False,
            },
        ],
    },
}

# Order services appear on the dashboard
SERVICE_ORDER = [
    "gmail",
    "icloud",
    "social_media",
    "lost_funds",
]

# Global brand information
BRAND = {
    "name": "AVA",
    "tagline": "Your account recovery case file organized, private, yours.",
    "disclaimer": (
        "AVA is a trusted tracking tool for organizing account recovery "
        "and lost-funds information."
    ),
}
