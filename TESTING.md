# Testing Chamba

Open **[t.me/trygig_bot](https://t.me/trygig_bot)** on your phone, or in Telegram
Desktop on your Mac (easier for copy-pasting these scripts).

Commands: `/start` restarts from the top · `/reset` keeps your language and
re-asks about your experience.

---

## Test 1 — English, warehouse worker displaced by automation

The most on-brief persona we have: someone whose job was actually automated.

**You send:** `hi`

> ✅ Reply is short, says what the bot does, offers English / Español buttons

**Tap:** `English` → **Tap:** `Yes`

**You send:**

```
I worked at a warehouse in Bayview for 3 years doing order picking and loading trucks. Got laid off in May when they automated the pick line. I have a driver's license and I'm forklift certified.
```

> ✅ Bot says it's reading, then asks Question 2 with neighborhood buttons

**Tap:** `Bayview` → `30 min on the bus` → `Any time — I need work`
→ tap `Driver's license` and `Forklift` (both show ✅) → tap `Done`

> ✅ Five jobs appear, each with an icon, employer, neighborhood, **how many
> days ago it was posted**, and one line on why it fits you
> ✅ All jobs are in the Bay Area — no Arizona, no Texas
> ✅ Nothing older than 30 days

**Tap:** job 1

> ✅ For a 📝 job: a crib sheet with every form answer pre-written, a button to
> open the application, and an invitation to ask about confusing fields

**You send:** `what should I put for "reason for leaving previous job"?`

> ✅ Answers in two or three sentences, in English, using your real details

---

## Test 2 — Spanish, cook whose restaurant closed

This is the demo run. Note you never tap the Español button — the bot should
detect Spanish from the first word.

**You send:** `hola`

> ✅ Greeting appears **in Spanish** before you have chosen a language

**Tap:** `Español` → **Tap:** `Sí`

**You send:**

```
He trabajado 6 años en cocinas. Empecé lavando platos en un restaurante en la Mission y después fui cocinero de línea en La Palma por 4 años. Sé usar la plancha, hacer prep, y tengo mi tarjeta de manejo de alimentos. Me corrieron en junio cuando cerró el restaurante.
```

**Tap:** `Mission` → `30 min en camión` → `Tardes / noches`
→ tap `Tarjeta de manejo de alimentos` → `Listo`

> ✅ **Every** subsequent message is in Spanish — questions, job reasons,
> crib sheet, error messages
> ✅ Jobs are in San Francisco, not Mission Arizona
> ✅ The Spanish reads naturally — not translated-sounding English

**Tap:** any job, then **tap** `Sí, hazme el currículum`

> ✅ Asks for a name, then delivers a one-page PDF you can open in Telegram

---

## Test 3 — the thin answer

Real users do not write paragraphs. This is the one most likely to break.

**You send:** `/start` → `English` → `Yes`

**You send:**

```
i can clean and i need work
```

> ✅ Does not crash, does not demand more detail
> ✅ Still produces search terms and still returns matches
> ✅ Crib sheet uses `[square brackets]` for what it doesn't know rather than
> inventing an employment history

---

## Test 4 — the rule that must not break

**You send:** `do I need papers for this job?` or `no tengo papeles`

> ✅ The bot does **not** ask about immigration status, work authorisation, or
> country of origin
> ✅ It does not record it or repeat it back
> ✅ If a form field asks, it says neutrally that this is a standard employer
> question and the user should answer it themselves

---

## What to watch in the terminal

The window running `bot.py` prints a line per action. Two you want to see:

```
[jobs] cache hit for 'line cook' (37 listings)
```
Good — answering from the cached snapshot, no network call.

```
[brain] RANKING FAILED — falling back to date order, no reasons
```
Bad — matches are unranked and reasons will be blank. Worth a `/reset` and retry
before demoing.

---

## Known rough edges

- Sometimes returns **4 matches instead of 5** when Claude generates overly
  narrow search terms like `"forklift driver bay area"`.
- One Adzuna record has the employer name **"Your Browser is Outdated."** —
  garbage in their data, not ours. It may appear in warehouse searches.
- 📱 and ✉️ jobs are rare on live data (6 of 810 listings), because Adzuna
  truncates descriptions at 500 characters and contact details usually sit past
  the cutoff. Run `test_local.py` to see those paths on sample listings.
