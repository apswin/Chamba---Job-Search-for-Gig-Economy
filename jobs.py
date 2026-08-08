"""Job search against Adzuna, with a recency filter and an offline fallback.

Two things matter here beyond "fetch some listings":

1. Recency. Hourly job boards are thick with listings that were filled months
   ago. We refuse anything older than MAX_DAYS_OLD and we always show the user
   how old a posting is, because that is the single most useful signal they are
   currently missing.

2. How to apply. We scan each posting for a phone number or an email address,
   because that determines which of the three outreach paths the user gets
   (text / email / web form). This classification is the whole product.
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, asdict, field
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

import requests

ADZUNA_BASE = "https://api.adzuna.com/v1/api/jobs/us/search/1"
MAX_DAYS_OLD = 30
RESULTS_PER_PAGE = 50
REQUEST_TIMEOUT = 12

CACHE_PATH = Path(__file__).parent / "data" / "cache_sf_jobs.json"

# Channels, in the order we prefer them: a text gets answered fastest, an email
# is next, and a web form is the fallback we help the user survive.
CHANNEL_TEXT = "text"
CHANNEL_EMAIL = "email"
CHANNEL_FORM = "form"

CHANNEL_ICON = {CHANNEL_TEXT: "📱", CHANNEL_EMAIL: "✉️", CHANNEL_FORM: "📝"}

# Deliberately loose: US formats with or without punctuation or a country code.
# We validate the digit count afterwards rather than trying to be clever here.
PHONE_RE = re.compile(
    r"(?:\+?1[\s.\-]?)?\(?([2-9]\d{2})\)?[\s.\-]?(\d{3})[\s.\-]?(\d{4})(?!\d)"
)
EMAIL_RE = re.compile(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}")

# Strings that look like phone numbers but are not a way to reach a hiring
# manager. Job postings are full of these.
PHONE_NOISE = re.compile(r"(?:job\s*id|req(?:uisition)?\s*#?|ref(?:erence)?\s*#?)", re.I)


@dataclass
class Job:
    """One listing, normalised into the only fields we actually use."""

    title: str
    company: str
    location: str
    days_ago: int
    url: str
    description: str
    channel: str
    contact_phone: Optional[str] = None
    contact_email: Optional[str] = None
    salary: Optional[str] = None
    contract_time: Optional[str] = None
    match_reason: str = ""
    source: str = "adzuna"

    @property
    def icon(self) -> str:
        return CHANNEL_ICON.get(self.channel, "📝")

    @property
    def freshness(self) -> str:
        if self.days_ago <= 0:
            return "posted today"
        if self.days_ago == 1:
            return "posted yesterday"
        return f"posted {self.days_ago} days ago"

    def to_dict(self) -> dict:
        return asdict(self)


def _days_since(created: str) -> int:
    """Adzuna returns ISO 8601. Be forgiving — a bad date must not crash a demo."""
    if not created:
        return 999
    try:
        stamp = datetime.fromisoformat(created.replace("Z", "+00:00"))
        if stamp.tzinfo is None:
            stamp = stamp.replace(tzinfo=timezone.utc)
        return max(0, (datetime.now(timezone.utc) - stamp).days)
    except (ValueError, TypeError):
        return 999


def _normalise_phone(match: re.Match) -> str:
    return f"({match.group(1)}) {match.group(2)}-{match.group(3)}"


def detect_channel(text: str) -> tuple:
    """Work out how a human is expected to respond to this posting.

    Returns (channel, phone, email). A posting that says "text Maria at
    415-555-0142" is worth far more to our user than one that points at a
    careers portal, so phone wins when both are present.
    """
    if not text:
        return CHANNEL_FORM, None, None

    email = None
    for candidate in EMAIL_RE.findall(text):
        # Skip no-reply senders and image filenames that survived the HTML strip.
        low = candidate.lower()
        if low.startswith(("noreply", "no-reply", "donotreply")):
            continue
        if low.endswith((".png", ".jpg", ".gif")):
            continue
        email = candidate
        break

    phone = None
    for match in PHONE_RE.finditer(text):
        window = text[max(0, match.start() - 40) : match.start()]
        if PHONE_NOISE.search(window):
            continue
        phone = _normalise_phone(match)
        break

    if phone:
        return CHANNEL_TEXT, phone, email
    if email:
        return CHANNEL_EMAIL, None, email
    return CHANNEL_FORM, None, None


def _parse_adzuna(raw: dict) -> Optional[Job]:
    description = (raw.get("description") or "").strip()
    days_ago = _days_since(raw.get("created", ""))
    if days_ago > MAX_DAYS_OLD:
        return None

    channel, phone, email = detect_channel(description)

    salary = None
    lo, hi = raw.get("salary_min"), raw.get("salary_max")
    if lo and hi:
        # Adzuna reports annualised figures; hourly roles are easier to read
        # converted back at roughly 2,080 hours a year.
        if lo < 200:
            salary = f"${lo:,.0f}–${hi:,.0f}/hr"
        elif lo == hi:
            salary = f"${lo/2080:,.0f}/hr (approx)"
        else:
            salary = f"${lo/2080:,.0f}–${hi/2080:,.0f}/hr (approx)"

    return Job(
        title=raw.get("title", "").strip() or "Untitled role",
        company=(raw.get("company") or {}).get("display_name", "").strip() or "Employer not listed",
        location=(raw.get("location") or {}).get("display_name", "").strip() or "San Francisco",
        days_ago=days_ago,
        url=raw.get("redirect_url", ""),
        description=description,
        channel=channel,
        contact_phone=phone,
        contact_email=email,
        salary=salary,
        contract_time=raw.get("contract_time"),
    )


def search(
    what: str,
    where: str = "San Francisco",
    distance_km: int = 25,
    limit: int = RESULTS_PER_PAGE,
) -> List[Job]:
    """Query Adzuna. Falls back to a cached snapshot on any failure.

    The fallback is not a nicety — it is the difference between a demo that
    survives hackathon wifi and one that does not.
    """
    app_id = os.getenv("ADZUNA_APP_ID", "").strip()
    app_key = os.getenv("ADZUNA_APP_KEY", "").strip()

    if not (app_id and app_key):
        return load_cache(reason="no Adzuna credentials configured")

    params = {
        "app_id": app_id,
        "app_key": app_key,
        "what": what,
        "where": where,
        "distance": distance_km,
        "max_days_old": MAX_DAYS_OLD,
        "results_per_page": limit,
        "sort_by": "date",
        "content-type": "application/json",
    }

    try:
        response = requests.get(ADZUNA_BASE, params=params, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        payload = response.json()
    except (requests.RequestException, ValueError) as exc:
        return load_cache(reason=f"Adzuna request failed: {exc}")

    jobs = [job for job in (_parse_adzuna(r) for r in payload.get("results", [])) if job]
    if not jobs:
        return load_cache(reason="Adzuna returned nothing usable")

    save_cache(jobs)
    return jobs


def save_cache(jobs: List[Job]) -> None:
    """Keep the last good result on disk so the demo always has real listings."""
    try:
        CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
        CACHE_PATH.write_text(
            json.dumps(
                {
                    "fetched_at": datetime.now(timezone.utc).isoformat(),
                    "jobs": [j.to_dict() for j in jobs],
                },
                indent=2,
            )
        )
    except OSError:
        pass  # A cache write failing must never take the bot down.


def load_cache(reason: str = "") -> List[Job]:
    if reason:
        print(f"[jobs] falling back to cache — {reason}")
    if not CACHE_PATH.exists():
        print("[jobs] no cache available; returning empty result")
        return []
    try:
        payload = json.loads(CACHE_PATH.read_text())
    except (OSError, ValueError):
        return []

    jobs = []
    for raw in payload.get("jobs", []):
        raw.pop("icon", None)
        raw.pop("freshness", None)
        jobs.append(Job(**raw))
    return jobs
