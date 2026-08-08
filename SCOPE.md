# Chamba — MVP Scope

A Telegram bot that takes a displaced hourly worker from "hola" to a sent job
application in under five minutes, in the language they actually speak.

*Working name. Change it.*

---

## 1. The problem, stated precisely

Displaced hourly workers in San Francisco do not have a job *discovery* problem.
Listings are everywhere. They have three other problems, in this order:

1. **Verification.** Hourly job boards are thick with stale posts, duplicate
   staffing-agency reposts, and scams. A worker spends their week applying to
   jobs that were filled in March.
2. **Application friction.** Where a real employer uses an ATS (Workday, Taleo,
   iCIMS), applying means creating an account, verifying an email, and re-typing
   a resume into thirty form fields. Forty-five minutes, on a phone, in a second
   language, after a shift.
3. **Language and self-presentation.** The step that stops people cold is not
   "find a job," it is "write about yourself, in English, persuasively."

The resume is *not* the primary bottleneck. Most hourly roles never read one.
We build a resume only where a listing demands one.

---

## 2. ICP

**Primary user**

- Bay Area, 25–55, lost a job or lost hours in the last six months
- Hourly service or trade work: restaurant front and back of house, retail,
  warehouse, hospitality, janitorial, light construction, delivery
- Primary language Spanish or English
- Smartphone yes; laptop unlikely; printer no
- Messaging apps daily. Email rarely, and often only to receive
- No current resume, or a 2019 Word file on a laptop they no longer have
- Has abandoned at least one online application partway through

**Explicitly not our user (MVP)**

- Tech and white-collar displaced workers — already well served
- Gig-platform-native drivers — different discovery loop entirely
- Licensed professionals (RN, electrician with C-10) — credential-gated hiring
- Students and first-time job seekers — different intake, different matching

**Jobs to be done, in the user's words**

- "Tell me which of these are real and hiring *now*, close to me."
- "Get me past the part where I have to write about myself in English."
- "Don't make me create another account."

---

## 3. Product principles

1. **Never ask for immigration or work-authorization status.** Employers verify
   via I-9 after an offer. Collecting it here creates risk for the user and no
   value for us. We ask about *certifications* only. This is non-negotiable.
2. **The worker sends, we draft.** Messages go from the worker's own phone and
   email so replies reach them. We never send on their behalf without an
   explicit, per-message confirmation.
3. **Never claim a job is real when we can't tell.** Show the posting date. If
   we can't verify freshness, say so.
4. **No account, no app, no password.** If a step needs one, we have failed.
5. **Nothing stored beyond the session** for MVP. Say this to the user, and say
   it on stage.

---

## 4. User stories

Each is written so it can be demoed and either passes or fails.

### US-1 — Cold start
**As** a worker who was sent this bot by a friend,
**I want** to say "hi" and immediately understand what this is,
**so that** I don't abandon in the first ten seconds.

- **Given** a user opens the bot for the first time and sends any message
- **When** the bot replies
- **Then** the reply is under 40 words, states what the bot does in one line,
  and ends with a single yes/no question
- **And** two tappable buttons are offered, never a free-text-only prompt

### US-2 — Language
**As** a Spanish-dominant worker,
**I want** the whole conversation in Spanish,
**so that** I'm not translating in my head while making decisions about my income.

- **Given** the first turn
- **When** the bot greets the user
- **Then** it offers "English / Español" as buttons
- **And** if the user's first message is in Spanish, the bot mirrors Spanish
  without waiting for the button
- **And** every subsequent message — including job titles, drafted SMS, drafted
  email, and resume — is produced in the chosen language, except the outbound
  employer message, which is produced in the language of the job posting

### US-3 — Intake
**As** a worker with no resume,
**I want** to answer a few plain questions instead of filling a form,
**so that** I can get to matches without writing anything long.

- **Given** the user says they're looking for work
- **When** the bot runs intake
- **Then** it asks **at most five questions**, one at a time:
  1. What kind of work have you done? *(free text, any length, any language)*
  2. What neighborhood are you in, and how far can you travel?
     *(offers transit-distance options, not just miles — many users don't drive)*
  3. When can you work? *(mornings / nights / weekends / open — availability is
     the single strongest filter in hourly hiring)*
  4. Do you have any of these? *(food handler card, driver's license, forklift,
     OSHA 10, own tools, English level — **never** immigration status)*
  5. How soon do you need to start?
- **And** any question can be skipped
- **And** if the user pastes an old resume or describes their history in one
  long message, the bot extracts what it can and asks only what's missing

### US-4 — Matches
**As** a worker who has wasted weeks on dead listings,
**I want** five jobs that are real and recent,
**so that** my effort goes somewhere.

- **Given** a completed profile
- **When** the bot searches
- **Then** it returns **exactly five** jobs, ranked by relevance × recency
- **And** each shows: title, employer, neighborhood, pay if listed, **how many
  days ago it was posted**, and one line on why it matched *this* worker
- **And** anything posted more than 30 days ago is excluded
- **And** each job is labeled with how to apply: 📱 text · ✉️ email · 📝 form

### US-5 — Apply by text
**As** a worker looking at a listing that says "text this number,"
**I want** the message written for me,
**so that** I send it in one tap instead of staring at an empty text box.

- **Given** the user taps a 📱 job
- **When** the bot responds
- **Then** it drafts a short SMS in the language of the posting, mentioning the
  specific role and the user's relevant experience and availability
- **And** it provides a tappable `sms:` link that opens the user's own messaging
  app with the number and body prefilled
- **And** the message is also shown as copy-ready text as a fallback
- **And** the bot never sends the message itself

### US-6 — Apply by email
**As** a worker applying to a listing that wants an email,
**I want** a finished email I can send from my own address,
**so that** the employer's reply comes to me.

- **Given** the user taps an ✉️ job
- **When** the bot responds
- **Then** it drafts a subject line and body, attaches a resume if the listing
  asks for one, and provides a `mailto:` link plus copy-ready text
- **And** the user sends it from their own account

### US-7 — Resume on demand
**As** a worker whose listing demands a resume,
**I want** one generated from what I already told the bot,
**so that** I don't rebuild my history from scratch.

- **Given** a matched job requires a resume
- **When** the user confirms
- **Then** the bot generates a one-page PDF from the intake profile
- **And** asks for **at most two** missing pieces before generating
- **And** delivers it as a Telegram file the user can forward or attach

### US-8 — Survive the form
**As** a worker stuck on question 19 of an ATS,
**I want** to ask what a field means and what to put,
**so that** I don't abandon the application.

- **Given** the user taps a 📝 job
- **When** the bot responds
- **Then** it gives the direct application link and a **crib sheet**: every
  answer we already know, pre-written, ready to paste
- **And** it invites the user to photograph or describe any confusing field
- **And** it answers field questions in their language for the rest of the session

---

## 5. Explicitly out of scope

Naming these is how we finish on time.

- Auto-submitting applications, creating accounts, solving CAPTCHAs — prohibited
  by the platforms' terms and by our own rules. We compress 45 minutes into 4;
  we don't fake the last click.
- Sending SMS or email from our own number or domain
- WhatsApp (needs Meta business verification — days, not hours)
- Voice note transcription *(stretch goal, not MVP)*
- Languages beyond English and Spanish
- Persistence across sessions, accounts, login
- Employer side, interview scheduling, follow-up nudges, payments
- Job sources beyond the one free API + curated fallback

---

## 6. Success metrics

### Demo day — what we prove in the room

| # | Metric | Target |
|---|---|---|
| D1 | Cold "hola" → five real matches | **under 3 minutes** |
| D2 | Full run in Spanish, no English typed by the user | **passes** |
| D3 | Jobs shown that are genuinely live, with visible post dates | **5 of 5** |
| D4 | Taps from match to a prefilled outbound message | **1** |
| D5 | Accounts created by the user | **0** |

### If this were live — what we'd actually measure

**North star:** applications *sent* per worker per week. Not matches shown, not
sessions — sent.

| Type | Metric | Why |
|---|---|---|
| Leading | Intake completion rate | Measures whether five questions is genuinely few enough |
| Leading | Time from first message to first application sent | Baseline is ~45 min per ATS application; target under 5 |
| Leading | Match → apply conversion | If they see five and act on none, our matching is wrong |
| Lagging | Employer reply rate per application sent | The only proof the drafted messages actually work |
| Lagging | Self-reported interviews and offers | The real outcome |
| Counter | "This job wasn't real" reports | Guards against optimizing for volume over verification |
| Counter | Share of sessions ending mid-intake | Guards against an intake that quietly grew |

---

## 7. Architecture

```
Telegram (long polling — no server, no webhook, no tunnel)
   │
   ├─ conversation.py   state machine + Claude for every user-facing turn
   ├─ jobs.py           free-tier job API + recency filter + fallback snapshot
   ├─ match.py          profile × listings → ranked 5, single Claude call
   ├─ outreach.py       SMS / email / crib sheet drafts + sms: and mailto: links
   └─ resume.py         profile → one-page PDF
```

Language is handled by one line in the system prompt, not a translation layer.

**Load-bearing risk:** the job API. Free tiers with real location and category
filtering are limited — Indeed and LinkedIn are closed to public use. Mitigation:
verify the source **first**, and cache a snapshot of real SF listings so the demo
survives both a rate limit and hackathon wifi.

---

## 8. Build order

Ship in this sequence. Each step is demoable on its own; stopping anywhere after
step 4 still gives a complete story.

1. Verify the job API, cache a real SF snapshot — *nothing else matters if this fails*
2. Telegram bot skeleton, echo round-trip working end to end
3. Language selection + five-question intake → structured profile
4. Match + recency filter → five jobs, formatted, in-language ← **minimum viable demo**
5. SMS draft + `sms:` deep link
6. Email draft + `mailto:` link
7. Resume PDF
8. ATS crib sheet
