"""Exercise the full pipeline from the terminal, without Telegram.

Run:  .venv/bin/python test_local.py

Needs ANTHROPIC_API_KEY. If ADZUNA_APP_ID/KEY are also set it uses live
listings; otherwise it falls back to the fixtures below.

The fixtures are deliberately, visibly fake — every phone number is in the
555-01xx range reserved for fiction and every domain is example.com — so that
sample data can never be mistaken for a real employer or accidentally
contacted. They live here and NOT in the job cache, so the bot can never
silently serve them to a real user.
"""

from __future__ import annotations

import os
import sys

from dotenv import load_dotenv

load_dotenv()

import brain  # noqa: E402
import jobs as jobsearch  # noqa: E402

FIXTURES = [
    jobsearch.Job(
        title="Line Cook - Evening Shift",
        company="[SAMPLE] Mission Taqueria",
        location="Mission District, San Francisco",
        days_ago=2,
        url="https://example.com/jobs/1",
        description=(
            "Busy taqueria needs an experienced line cook for evenings. Grill and "
            "prep experience required. Food handler card required. Text Maria at "
            "415-555-0142 to set up a trial shift. Se habla espanol."
        ),
        channel=jobsearch.CHANNEL_TEXT,
        contact_phone="(415) 555-0142",
        salary="$23-26/hr",
    ),
    jobsearch.Job(
        title="Warehouse Associate",
        company="[SAMPLE] Bayview Distribution",
        location="Bayview, San Francisco",
        days_ago=5,
        url="https://example.com/jobs/2",
        description=(
            "Loading, unloading, order picking. Forklift certification a plus but "
            "we will train. Early mornings, 5am start. Send your resume to "
            "jobs@example.com."
        ),
        channel=jobsearch.CHANNEL_EMAIL,
        contact_email="jobs@example.com",
        salary="$24/hr",
    ),
    jobsearch.Job(
        title="Prep Cook",
        company="[SAMPLE] SoMa Cafe Group",
        location="SoMa, San Francisco",
        days_ago=1,
        url="https://example.com/jobs/3",
        description=(
            "Morning prep cook for a busy cafe. Knife skills, food safety, and "
            "consistency matter more than years. Apply through our careers page."
        ),
        channel=jobsearch.CHANNEL_FORM,
        salary="$22-24/hr",
    ),
    jobsearch.Job(
        title="Dishwasher / Kitchen Helper",
        company="[SAMPLE] Richmond Family Restaurant",
        location="Richmond District, San Francisco",
        days_ago=3,
        url="https://example.com/jobs/4",
        description=(
            "Evenings and weekends. No experience needed, we will train. Call or "
            "text 415-555-0177."
        ),
        channel=jobsearch.CHANNEL_TEXT,
        contact_phone="(415) 555-0177",
    ),
    jobsearch.Job(
        title="Night Janitor - Office Building",
        company="[SAMPLE] Downtown Facilities",
        location="Financial District, San Francisco",
        days_ago=8,
        url="https://example.com/jobs/5",
        description=(
            "Nightly cleaning of office floors, 6pm-2am. Reliable transportation "
            "needed. Email hiring@example.com with your availability."
        ),
        channel=jobsearch.CHANNEL_EMAIL,
        contact_email="hiring@example.com",
        salary="$25/hr",
    ),
    jobsearch.Job(
        title="Server - Full Time",
        company="[SAMPLE] Marina Bistro",
        location="Marina, San Francisco",
        days_ago=4,
        url="https://example.com/jobs/6",
        description=(
            "Full-time server for a neighborhood bistro. Prior serving experience "
            "and strong English preferred. Apply online."
        ),
        channel=jobsearch.CHANNEL_FORM,
        salary="$20/hr + tips",
    ),
]

SCENARIOS = {
    "es": (
        "es",
        "He trabajado 6 anos en cocinas. Empece lavando platos en un restaurante "
        "en la Mission y despues fui cocinero de linea en La Palma por 4 anos. "
        "Se usar la plancha, hacer prep, y tengo mi tarjeta de manejo de "
        "alimentos. Me corrieron en junio cuando cerro el restaurante.",
        {"neighborhood": "Mission", "availability": "evenings and nights"},
    ),
    "en": (
        "en",
        "I worked at a warehouse in Bayview for 3 years doing order picking and "
        "loading trucks. Got laid off in May when they automated the pick line. "
        "I have a driver's license and I'm forklift certified.",
        {"neighborhood": "Bayview", "availability": "any shift, fully open"},
    ),
}


def divider(title: str) -> None:
    print(f"\n{'=' * 68}\n{title}\n{'=' * 68}")


def run(scenario: str) -> None:
    language, story, extras = SCENARIOS[scenario]

    divider(f"1. INTAKE  ({language})")
    print(f"Worker says:\n  {story}\n")
    profile = brain.extract_experience(story, language)
    profile.update(extras)
    for key in ("summary", "roles", "years_experience", "skills",
                "certifications", "search_terms", "english_level"):
        print(f"  {key:18} {profile.get(key)}")

    divider("2. JOB SEARCH")
    live = []
    if os.getenv("ADZUNA_APP_ID", "").strip():
        for term in (profile.get("search_terms") or [])[:2]:
            live.extend(jobsearch.search(term, profile["neighborhood"]))
        print(f"  Adzuna returned {len(live)} listings within {jobsearch.MAX_DAYS_OLD} days")
    pool = live or FIXTURES
    if not live:
        print(f"  No Adzuna credentials — using {len(FIXTURES)} clearly-marked SAMPLE listings")

    divider("3. RANKING")
    matches = brain.rank_jobs(profile, pool, language)
    for i, job in enumerate(matches, 1):
        print(f"  {job.icon} {i}. {job.title} — {job.company}")
        print(f"      {job.location} · {job.freshness} · {job.salary or 'pay not listed'}")
        print(f"      ↳ {job.match_reason}\n")

    if not matches:
        print("  no matches")
        return

    divider("4. OUTREACH")
    for job in matches:
        if job.channel == jobsearch.CHANNEL_TEXT:
            draft = brain.draft_sms(profile, job, language)
            print(f"  📱 TEXT to {job.contact_phone} — {job.title}\n")
            print(f"     {draft.get('message', '')}\n")
            print(f"     note: {draft.get('note', '')}\n")
            break
    for job in matches:
        if job.channel == jobsearch.CHANNEL_EMAIL:
            draft = brain.draft_email(profile, job, language)
            print(f"  ✉️  EMAIL to {job.contact_email} — {job.title}\n")
            print(f"     Subject: {draft.get('subject', '')}\n")
            for line in draft.get("body", "").split("\n"):
                print(f"     {line}")
            print()
            break
    for job in matches:
        if job.channel == jobsearch.CHANNEL_FORM:
            sheet = brain.draft_crib_sheet(profile, job, language)
            print(f"  📝 CRIB SHEET — {job.title}\n")
            for line in sheet.split("\n"):
                print(f"     {line}")
            break


if __name__ == "__main__":
    if not os.getenv("ANTHROPIC_API_KEY", "").strip():
        sys.exit("ANTHROPIC_API_KEY is missing. Put it in .env first.")
    run(sys.argv[1] if len(sys.argv) > 1 and sys.argv[1] in SCENARIOS else "es")
