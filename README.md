# Chamba

**A Telegram bot that takes a laid-off hourly worker from "hola" to a finished job application in under five minutes — in the language they actually speak.**

👉 **Try it: [t.me/trygig_bot](https://t.me/trygig_bot)** — send it `hi` or `hola`. No account, no app, no resume needed.

> *Chamba* is Mexican and Central American slang for a job or a gig — the word people actually use.

Built at the **Claude Impact Lab**, San Francisco, 8 August 2026.

---

## The problem statement we took

From the three the community surfaced, we took the third:

> **REPRESENTATION — Not everyone is in the room.**
> *Build something for a San Franciscan who isn't in this room — a care worker, a city employee, a restaurant owner — that they'd actually open on Monday.*

We considered two other ideas first and rejected both, for the same reason. A tool for creators with 100–500k followers is a tool for people who are very much *in* the room. And a consumer marketing tool needs us to supply demand, which is a distribution and capital problem, not a software one.

So we set a rule: **build something where the input is already in the user's pocket.** Don't generate leads. Fix what happens to the ones they already get.

---

## Who this is for

Bay Area, 25–55, lost a job or lost hours in the last six months. Restaurant, retail, warehouse, janitorial, hospitality, light construction. Spanish or English. A smartphone, no laptop, no printer. No current resume — or a 2019 Word file on a laptop they no longer have. Has already abandoned at least one online application partway through.

Explicitly **not**: tech-displaced white-collar workers, gig-platform drivers, licensed professionals. Those groups are well served already.

---

## What we learned about the actual problem

The resume is **not** the bottleneck. Most hourly roles never read one. Three other things are:

1. **Verification.** Job boards are thick with stale listings, duplicate staffing-agency reposts, and scams. People spend their week applying to jobs filled in March. So every match we show carries its posting date, and nothing older than 30 days is ever shown.

2. **Application friction.** Where a real employer uses an ATS — Workday, Taleo, iCIMS — applying means creating an account, verifying an email, and re-typing everything into thirty form fields. Forty-five minutes, on a phone, in a second language, after a shift. **This is the wall.**

3. **Language and self-presentation.** What stops people cold isn't finding a job. It's writing about yourself, in English, persuasively.

---

## How it works

```
"hola"
   ↓
Language — English or Español (it also detects and mirrors your first message)
   ↓
Five questions, one at a time — most are buttons, not typing
   experience · neighborhood · how far you can travel · availability · certifications
   ↓
Live search across the Bay Area, nothing older than 30 days
   ↓
Your five best matches, each with one line on why it fits YOU
   ↓
Per job, whichever applies:
   📱  a text message written for you, to the number in the posting
   ✉️  an email written for you, to send from your own address
   📝  a CRIB SHEET — every answer the online form will ask for,
       pre-written, ready to paste — plus "send me a photo of any
       question you're stuck on and I'll tell you what to put"
```

The crib sheet is the heart of it. It turns a 45-minute application into about four minutes.

---

## What's real, and what isn't

We think being precise about this matters more than a clean demo.

**Real:**
- Live job listings from Adzuna, genuinely posted in the last 30 days, genuinely in the Bay Area
- Matching, drafting and crib sheets generated live by Claude Haiku 4.5
- Full Spanish, written directly by the model — not English run through a translator
- The resume PDF
- The bot itself — anyone can message it right now

**Not real, deliberately:**
- **We do not auto-submit applications.** That would mean creating accounts, entering credentials and defeating CAPTCHAs on sites whose terms prohibit exactly that. We compress the 45 minutes into 4; we don't fake the last click.
- **We never send from our own number or domain.** The worker sends from their own phone and their own email, so the employer's reply reaches *them* and not us. Sending from a Twilio number would put the callback in a dead inbox.
- **Sample listings in `test_local.py` are visibly fake** — every phone number is in the 555-01xx range reserved for fiction, every domain is `example.com`, every employer is prefixed `[SAMPLE]`. They live in the test file and never touch the job cache, so they cannot reach a real user.

**A limitation we found and could not engineer around:** Adzuna's free tier truncates every job description at exactly 500 characters. Contact details usually sit past that cutoff. One listing we pulled literally reads *"...Want to apply to this job via text mes…"* and stops one character before the phone number. Across 810 cached listings, only 6 exposed a phone number. So in practice almost every live job routes to the crib sheet. We could have scraped the full postings to recover the numbers — we chose not to, because it violates those boards' terms.

---

## A rule we set and did not break

**The bot never asks about immigration status, work authorisation, visas, or country of origin.**

Employers verify eligibility via I-9 *after* an offer. Collecting it in a chatbot creates real risk for the user and gives the product nothing. It's written into the system prompt as a hard rule, and if a user volunteers it, it is not stored, repeated, or written into any document. If a form asks, the bot tells them neutrally that it's a standard question and that they should answer it themselves.

---

## APIs and services integrated

| Service | What it does here | Tier |
|---|---|---|
| **[Anthropic Claude API](https://docs.claude.com/en/api/)** — Haiku 4.5 | Intake extraction, job ranking, SMS/email drafting, crib sheets, live form help. All six call sites use Haiku. | Paid, pennies per session |
| **[Telegram Bot API](https://core.telegram.org/bots/api)** | The entire interface. Long polling — no server, no webhook, no public URL. | Free |
| **[Adzuna Jobs API](https://developer.adzuna.com/)** | Live Bay Area listings, filtered by `max_days_old` and sorted by date. | Free, 1,000 calls/month |
| **ReportLab** | One-page resume PDF, generated only when a listing demands one. | Open source |

Telegram offers three APIs — we use the **Bot API**, not TDLib and not the MTProto client API. It needs only a BotFather token.

---

## The process we followed

1. **Rejected two ideas before writing code.** Both failed the same test: they required us to supply demand. Naming that early saved the day.
2. **Wrote [SCOPE.md](SCOPE.md) before building** — ICP, anti-ICP, eight user stories with Given/When/Then acceptance criteria, and success metrics split into demo-day proofs and real product metrics. Every story is written to pass or fail, not to be argued about.
3. **Verified the load-bearing risk first.** Before anything else we confirmed the job API worked, because nothing downstream mattered if it didn't. It threw up two problems immediately — see below.
4. **Built the offline cache before the demo needed it.** Adzuna throttled us into generic HTML error pages after about fifteen rapid calls. We added a per-query disk cache, a minimum interval between calls, and bounded retries, then pulled a snapshot of **810 real listings across 20 queries** — 205 posted today, 323 within the week. The bot now answers from cache and never touches the network mid-demo.
5. **Fixed two bugs the first end-to-end run exposed.** Passing the neighborhood `"Mission"` to the job API returned jobs in Mission, *Arizona* — the API resolves at city level, so neighborhoods are now collapsed before they go near it. And a silent fallback was serving date-sorted results as "best matches" whenever a parse failed, with nothing to indicate it. Silent degradation is worse than a crash; it now salvages what it can and says so loudly when it can't.
6. **Tuned matching against a real failure.** The first good run ranked a $31/hr job in Walnut Creek above a San Francisco one, for a worker in the Mission with no car. Reachability is now a hard filter, not a preference — a wage you cannot physically get to is worth zero.

---

## Success metrics

**What we set out to prove today**

| | Target | Status |
|---|---|---|
| Cold "hola" → five real matches | under 3 min | ✅ |
| Full run in Spanish, no English typed | passes | ✅ |
| Listings genuinely live, post dates visible | 5 of 5 | ✅ |
| Accounts the user must create | 0 | ✅ |

**What we'd measure if this ran for real**

North star: **applications *sent* per worker per week** — not matches shown, not sessions. Leading indicators: intake completion rate, time from first message to first application sent (baseline ~45 min, target under 5). Counter-metric: *"this job wasn't real"* reports, so we never optimise volume over verification.

---

## Architecture

```
Telegram Bot API  (long polling — no server, no webhook, no tunnel)
   │
   ├─ bot.py         conversation state machine, all eight user stories
   ├─ strings.py     every user-facing line, English and Spanish
   ├─ brain.py       all six Claude calls — the only file touching the API
   ├─ jobs.py        Adzuna client, recency filter, channel detection, cache
   ├─ outreach.py    sms: and mailto: deep links
   └─ resume.py      one-page PDF
```

Language is one line in the system prompt, not a translation layer.

---

## Run it yourself

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
```

Copy `.env.example` to `.env` and fill in four values — an [Anthropic key](https://console.anthropic.com), a Telegram token from [@BotFather](https://t.me/botfather), and an Adzuna app ID and key from [developer.adzuna.com](https://developer.adzuna.com/signup).

Warm the cache once, so a demo never depends on the network:

```bash
.venv/bin/python build_snapshot.py
```

Then start it:

```bash
.venv/bin/python bot.py
```

While that process runs, the bot is live worldwide. Stop it and it stops.

To see the whole pipeline in the terminal without Telegram:

```bash
.venv/bin/python test_local.py es
```

`.env` is gitignored. No keys are in this repository.

---

## What's next

- **WhatsApp.** Telegram was the demo surface; WhatsApp is where this audience actually is. It needs Meta business verification — days, not hours.
- **Voice notes.** Typing a work history is the highest-friction step left. Speaking it is natural for this user.
- **A better job source.** The "text Maria at 415-…" jobs live on Craigslist and in neighborhood Facebook groups, not on aggregators. Reaching them legitimately means partnerships, not scraping.
- **Follow-up.** Right now we help you apply once. The people who get hired are the ones who follow up on day three.
