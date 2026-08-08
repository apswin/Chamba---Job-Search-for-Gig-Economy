"""Every call to Claude lives here.

Design notes worth knowing before editing:

* Language is handled by passing the user's chosen language into the system
  prompt. There is no translation step — Claude writes Spanish directly, which
  reads far better than English-then-translated.
* Intake questions 2-5 are buttons, not model calls, so the conversation stays
  instant. Claude is used where it actually earns its latency: understanding a
  rambling free-text work history, ranking jobs, and writing outreach.
* Outbound employer messages are written in the language of the *posting*, not
  the language of the user. A hiring manager who posted in English should get
  English. The user always sees a translation alongside it.
"""

from __future__ import annotations

import json
import os
import re
from typing import List, Optional

from anthropic import Anthropic

MODEL = "claude-sonnet-5"  # Latency matters more than depth in a live chat.

_client: Optional[Anthropic] = None


def client() -> Anthropic:
    global _client
    if _client is None:
        _client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    return _client


LANGUAGE_NAME = {"en": "English", "es": "Spanish"}

BASE_RULES = """You are Chamba, a job-search assistant used over Telegram by \
people in the San Francisco Bay Area who have recently lost hourly work — \
restaurant, retail, warehouse, janitorial, hospitality, light construction.

Non-negotiable rules:
- NEVER ask about immigration status, work authorisation, visa, social security \
number, or country of origin. Employers verify eligibility after an offer. \
Asking here creates risk for the user and gives us nothing. If a user \
volunteers it, do not store it, repeat it, or put it in any document.
- Write at a plain, warm, sixth-grade reading level. Short sentences. No \
corporate voice, no "leverage", no "synergy", no "passionate about".
- Never invent experience, certifications, dates, or employers. If something is \
missing, leave it out or ask.
- Never promise a job, an interview, or a callback.
- Respect that this person is under financial stress. Be brief and useful, not \
chatty or falsely upbeat."""


def _text(response) -> str:
    return "".join(block.text for block in response.content if block.type == "text").strip()


def _json(response) -> dict:
    """Pull JSON out of a reply, tolerating stray prose or code fences."""
    raw = _text(response)
    fence = re.search(r"```(?:json)?\s*(.*?)```", raw, re.S)
    if fence:
        raw = fence.group(1)
    start, end = raw.find("{"), raw.rfind("}")
    if start != -1 and end != -1:
        raw = raw[start : end + 1]
    try:
        return json.loads(raw)
    except ValueError:
        return {}


# --------------------------------------------------------------------------
# Language
# --------------------------------------------------------------------------


def detect_language(message: str) -> str:
    """Cheap heuristic so a user who opens in Spanish is answered in Spanish
    before they ever tap the language button."""
    spanish_markers = (
        " hola", "buenos", "buenas", "necesito", "trabajo", "busco", "quiero",
        "ayuda", "empleo", "chamba", "gracias", "por favor", "estoy", "tengo",
        "señor", "señora", "días", "cómo", "qué", "sí",
    )
    low = f" {message.lower()} "
    return "es" if any(marker in low for marker in spanish_markers) else "en"


# --------------------------------------------------------------------------
# Intake
# --------------------------------------------------------------------------

EXPERIENCE_PROMPT = """The user was asked: "What kind of work have you done?"

They replied (this may be a few words, a long rambling story, a pasted old \
resume, or a mix of languages — handle all of it):

---
{answer}
---

Extract what is actually there. Invent nothing.

Return ONLY JSON:
{{
  "roles": ["job titles they have actually held, most recent first"],
  "years_experience": <integer or null>,
  "industries": ["restaurant" | "retail" | "warehouse" | "janitorial" | "hospitality" | "construction" | "care" | "delivery" | "other"],
  "skills": ["concrete skills they mentioned — grill, POS, forklift, prep, host, cash handling, cleaning, driving"],
  "employers": ["named employers, if any"],
  "certifications": ["food handler card, OSHA 10, forklift, driver's license, etc — ONLY if mentioned"],
  "english_level": "none" | "basic" | "conversational" | "fluent" | null,
  "search_terms": ["2-4 short job-board search phrases that would surface the right listings for this person"],
  "summary": "one plain sentence describing this worker, in {language}"
}}"""


def extract_experience(answer: str, language: str) -> dict:
    response = client().messages.create(
        model=MODEL,
        max_tokens=900,
        system=BASE_RULES,
        messages=[
            {
                "role": "user",
                "content": EXPERIENCE_PROMPT.format(
                    answer=answer, language=LANGUAGE_NAME.get(language, "English")
                ),
            }
        ],
    )
    data = _json(response)
    if not data.get("search_terms"):
        data["search_terms"] = ["general labor", "restaurant", "warehouse"]
    return data


# --------------------------------------------------------------------------
# Matching
# --------------------------------------------------------------------------

MATCH_PROMPT = """Here is a worker profile:

{profile}

Here are live job listings near them. Each has an ID.

{listings}

Pick the FIVE best matches for this specific person. Judge on:
1. Can they actually do this job with the experience they have? (heaviest weight)
2. Is it reachable given where they live and how far they can travel?
3. Does the schedule fit their stated availability?
4. How recently was it posted? Fresher is meaningfully better.
5. Prefer listings they can respond to by text or email over web forms, \
because those get answered faster — but never pick a bad job just for the channel.

Return ONLY JSON:
{{
  "matches": [
    {{
      "id": <listing id>,
      "reason": "ONE short sentence, addressed to the worker as 'you', saying \
why this fits THEM specifically. Reference their actual experience. Written in \
{language}. No more than 18 words."
    }}
  ]
}}

Exactly five, best first. If fewer than five listings are genuinely plausible, \
return only the plausible ones."""


def rank_jobs(profile: dict, jobs: list, language: str, top_n: int = 5) -> list:
    """Return the best `top_n` jobs, each with a `match_reason` filled in."""
    if not jobs:
        return []

    listings = "\n\n".join(
        f"[{i}] {j.title} — {j.company}\n"
        f"    {j.location} · {j.freshness} · {j.salary or 'pay not listed'} · apply by {j.channel}\n"
        f"    {j.description[:320]}"
        for i, j in enumerate(jobs[:40])
    )

    response = client().messages.create(
        model=MODEL,
        max_tokens=1200,
        system=BASE_RULES,
        messages=[
            {
                "role": "user",
                "content": MATCH_PROMPT.format(
                    profile=json.dumps(profile, indent=2, ensure_ascii=False),
                    listings=listings,
                    language=LANGUAGE_NAME.get(language, "English"),
                ),
            }
        ],
    )

    ranked = []
    for match in _json(response).get("matches", [])[:top_n]:
        try:
            job = jobs[int(match["id"])]
        except (ValueError, KeyError, IndexError, TypeError):
            continue
        job.match_reason = match.get("reason", "")
        ranked.append(job)

    # If the model returned nothing usable, fall back to freshest-first rather
    # than showing the user an empty screen.
    return ranked or jobs[:top_n]


# --------------------------------------------------------------------------
# Outreach
# --------------------------------------------------------------------------

SMS_PROMPT = """Write a text message this worker will send to a hiring manager \
about this job.

WORKER:
{profile}

JOB:
{title} at {company} ({location})
{description}

Rules:
- Under 320 characters. It is a text message, not a cover letter.
- First line: their name, and the exact job they are texting about.
- Then ONE concrete thing from their real experience that fits this job.
- Then their availability.
- End by asking if they can come in or talk.
- Warm and direct. No emoji. No "I am writing to express my interest".
- Write it in the language of the JOB POSTING above.
- Use only facts from the worker profile. Invent nothing.

Return ONLY JSON:
{{"message": "the text to send", "note": "one short line to the worker in {language} telling them what this says and to check it before sending"}}"""

EMAIL_PROMPT = """Write an email this worker will send from their own address \
about this job.

WORKER:
{profile}

JOB:
{title} at {company} ({location})
{description}

Rules:
- Subject line: the job title and their name. Nothing clever.
- Body: 4-6 short sentences. Who they are, the relevant experience, their \
availability, a clear ask for a conversation.
- Plain and human. No corporate filler. No "I am passionate about".
- Write it in the language of the JOB POSTING above.
- Use only facts from the worker profile. Invent nothing.

Return ONLY JSON:
{{"subject": "...", "body": "...", "note": "one short line to the worker in {language} telling them what this says and to check it before sending"}}"""

CRIB_PROMPT = """This worker has to fill out an online application form for \
this job. Those forms are the main reason people give up.

WORKER:
{profile}

JOB:
{title} at {company} ({location})
{description}

Write them a crib sheet: the answers they will need, ready to copy and paste, \
so they are never staring at a blank field.

Cover the fields these forms almost always have: full name, phone, email, \
address, position applied for, availability, years of experience, previous \
employers, why do you want to work here, and anything this specific posting \
implies.

Where you do not know the answer (their address, their phone), write a short \
placeholder in square brackets for them to fill in — do not invent it.

Write in {language}. Use short labelled lines, not paragraphs. Do NOT use \
markdown headers or bold. End with one line telling them they can send you a \
photo of any confusing question and you will explain it.

Return plain text only."""


def draft_sms(profile: dict, job, language: str) -> dict:
    response = client().messages.create(
        model=MODEL,
        max_tokens=700,
        system=BASE_RULES,
        messages=[{"role": "user", "content": SMS_PROMPT.format(
            profile=json.dumps(profile, ensure_ascii=False),
            title=job.title, company=job.company, location=job.location,
            description=job.description[:900],
            language=LANGUAGE_NAME.get(language, "English"),
        )}],
    )
    return _json(response)


def draft_email(profile: dict, job, language: str) -> dict:
    response = client().messages.create(
        model=MODEL,
        max_tokens=900,
        system=BASE_RULES,
        messages=[{"role": "user", "content": EMAIL_PROMPT.format(
            profile=json.dumps(profile, ensure_ascii=False),
            title=job.title, company=job.company, location=job.location,
            description=job.description[:900],
            language=LANGUAGE_NAME.get(language, "English"),
        )}],
    )
    return _json(response)


def draft_crib_sheet(profile: dict, job, language: str) -> str:
    response = client().messages.create(
        model=MODEL,
        max_tokens=1100,
        system=BASE_RULES,
        messages=[{"role": "user", "content": CRIB_PROMPT.format(
            profile=json.dumps(profile, ensure_ascii=False),
            title=job.title, company=job.company, location=job.location,
            description=job.description[:900],
            language=LANGUAGE_NAME.get(language, "English"),
        )}],
    )
    return _text(response)


FIELD_HELP_PROMPT = """The worker is filling out a job application for \
{title} at {company} and is stuck.

What they know about themselves:
{profile}

Their question:
{question}

Answer in {language}. Two or three short sentences. If it is a form field, tell \
them plainly what it is asking and suggest exactly what to type, using their \
real details where you have them. If the field asks about immigration or work \
authorisation, tell them neutrally that this is a standard question employers \
ask and that they should answer it themselves — do not advise them what to put."""


def answer_field_question(profile: dict, job, question: str, language: str) -> str:
    response = client().messages.create(
        model=MODEL,
        max_tokens=500,
        system=BASE_RULES,
        messages=[{"role": "user", "content": FIELD_HELP_PROMPT.format(
            title=job.title, company=job.company,
            profile=json.dumps(profile, ensure_ascii=False),
            question=question,
            language=LANGUAGE_NAME.get(language, "English"),
        )}],
    )
    return _text(response)
