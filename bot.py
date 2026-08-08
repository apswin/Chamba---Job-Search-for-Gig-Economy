"""Chamba — a Telegram bot that takes a displaced hourly worker from "hola" to
a sent job application.

Run it:  .venv/bin/python bot.py

Uses long polling, so there is no server, no webhook and no public URL. While
this process is running the bot is live worldwide; when you stop it, it stops.
"""

from __future__ import annotations

import asyncio
import html
import logging
import os
from pathlib import Path

from dotenv import load_dotenv
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update,
)
from telegram.constants import ChatAction, ParseMode
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

import brain
import jobs as jobsearch
import resume as resume_builder
from strings import AVAILABILITY_TEXT, CERT_TEXT, DISTANCE_KM, STRINGS, t

load_dotenv()

logging.basicConfig(
    format="%(asctime)s  %(name)s  %(levelname)s  %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)
log = logging.getLogger("chamba")

(
    LANG,
    CONFIRM,
    EXPERIENCE,
    NEIGHBORHOOD,
    NEIGHBORHOOD_TEXT,
    DISTANCE,
    AVAILABILITY,
    CERTS,
    BROWSING,
    RESUME_NAME,
) = range(10)

OUT_DIR = Path(__file__).parent / "out"


# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------


def lang(context: ContextTypes.DEFAULT_TYPE) -> str:
    return context.user_data.get("lang", "en")


def esc(text) -> str:
    return html.escape(str(text or ""))


def keyboard(rows) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton(label, callback_data=data) for label, data in row]
         for row in rows]
    )


async def say(update: Update, text: str, markup=None):
    """Reply, whether the trigger was a message or a button tap."""
    target = update.effective_message
    return await target.reply_text(
        text, parse_mode=ParseMode.HTML, reply_markup=markup,
        disable_web_page_preview=True,
    )


async def typing(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await context.bot.send_chat_action(
            chat_id=update.effective_chat.id, action=ChatAction.TYPING
        )
    except Exception:
        pass


# --------------------------------------------------------------------------
# intake
# --------------------------------------------------------------------------


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Entry point — any message at all lands here."""
    context.user_data.clear()

    first = (update.effective_message.text or "").strip()
    guess = brain.detect_language(first) if first else "en"
    context.user_data["lang"] = guess

    await say(update, t(guess, "greet"))
    await say(
        update,
        t(guess, "pick_language"),
        keyboard([[("English", "lang:en"), ("Español", "lang:es")]]),
    )
    return LANG


async def set_language(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    chosen = query.data.split(":", 1)[1]
    context.user_data["lang"] = chosen

    await say(
        update,
        t(chosen, "looking"),
        keyboard([[(t(chosen, "yes"), "look:yes"), (t(chosen, "no"), "look:no")]]),
    )
    return CONFIRM


async def confirm_looking(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    language = lang(context)

    if query.data.endswith("no"):
        await say(update, t(language, "no_worries"))
        return ConversationHandler.END

    await say(update, t(language, "q_experience"))
    return EXPERIENCE


async def got_experience(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    language = lang(context)
    answer = update.effective_message.text or ""

    await say(update, t(language, "reading"))
    await typing(update, context)

    try:
        extracted = await asyncio.to_thread(brain.extract_experience, answer, language)
    except Exception:
        log.exception("experience extraction failed")
        await say(update, t(language, "error"))
        return EXPERIENCE

    context.user_data["profile"] = extracted
    context.user_data["profile"]["raw_experience"] = answer

    hoods = STRINGS[language]["neighborhoods"]
    rows = [
        [(hoods[i], f"hood:{i}"), (hoods[i + 1], f"hood:{i + 1}")]
        for i in range(0, len(hoods) - 1, 2)
    ]
    await say(update, t(language, "q_neighborhood"), keyboard(rows))
    return NEIGHBORHOOD


async def got_neighborhood(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    language = lang(context)
    index = int(query.data.split(":", 1)[1])
    hoods = STRINGS[language]["neighborhoods"]

    if index == len(hoods) - 1:  # "Somewhere else"
        await say(update, t(language, "type_neighborhood"))
        return NEIGHBORHOOD_TEXT

    context.user_data["profile"]["neighborhood"] = hoods[index]
    return await ask_distance(update, context)


async def got_neighborhood_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["profile"]["neighborhood"] = (
        update.effective_message.text or ""
    ).strip()
    return await ask_distance(update, context)


async def ask_distance(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    language = lang(context)
    rows = [[(label, f"dist:{key}")] for key, label in STRINGS[language]["distances"]]
    await say(update, t(language, "q_distance"), keyboard(rows))
    return DISTANCE


async def got_distance(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    language = lang(context)
    context.user_data["profile"]["distance_key"] = query.data.split(":", 1)[1]

    rows = [[(label, f"avail:{key}")] for key, label in STRINGS[language]["availabilities"]]
    await say(update, t(language, "q_availability"), keyboard(rows))
    return AVAILABILITY


async def got_availability(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    language = lang(context)
    key = query.data.split(":", 1)[1]
    context.user_data["profile"]["availability"] = AVAILABILITY_TEXT.get(key, key)
    context.user_data.setdefault("certs", set())

    await say(update, t(language, "q_certs"), certs_keyboard(context))
    return CERTS


def certs_keyboard(context: ContextTypes.DEFAULT_TYPE) -> InlineKeyboardMarkup:
    language = lang(context)
    chosen = context.user_data.get("certs", set())
    rows = [
        [(("✅ " if key in chosen else "") + label, f"cert:{key}")]
        for key, label in STRINGS[language]["certs"]
    ]
    rows.append([
        (t(language, "certs_none"), "cert:none"),
        (t(language, "certs_done"), "cert:done"),
    ])
    return keyboard(rows)


async def toggle_cert(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    key = query.data.split(":", 1)[1]
    chosen = context.user_data.setdefault("certs", set())

    if key == "none":
        chosen.clear()
        return await run_search(update, context)
    if key == "done":
        return await run_search(update, context)

    chosen.symmetric_difference_update({key})
    try:
        await query.edit_message_reply_markup(reply_markup=certs_keyboard(context))
    except Exception:
        pass
    return CERTS


# --------------------------------------------------------------------------
# search and results
# --------------------------------------------------------------------------


async def run_search(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    language = lang(context)
    profile = context.user_data["profile"]

    chosen = context.user_data.get("certs", set())
    existing = profile.get("certifications") or []
    profile["certifications"] = sorted(
        set(existing) | {CERT_TEXT[k] for k in chosen if k in CERT_TEXT}
    )

    await say(update, t(language, "thinking"))
    await typing(update, context)

    # The neighborhood stays on the profile for ranking, but the API only
    # understands cities — see jobs.city_for.
    where = jobsearch.city_for(profile.get("neighborhood", ""))
    distance = DISTANCE_KM.get(profile.get("distance_key", "transit60"), 25)
    terms = profile.get("search_terms") or ["general labor"]

    found: list = []
    seen_urls = set()
    try:
        for term in terms[:3]:
            batch = await asyncio.to_thread(jobsearch.search, term, where, distance)
            for job in batch:
                if job.url not in seen_urls:
                    seen_urls.add(job.url)
                    found.append(job)
    except Exception:
        log.exception("job search failed")

    if not found:
        await say(update, t(language, "no_jobs"))
        return BROWSING

    try:
        matches = await asyncio.to_thread(brain.rank_jobs, profile, found, language)
    except Exception:
        log.exception("ranking failed")
        matches = found[:5]

    context.user_data["matches"] = matches
    await show_results(update, context)
    return BROWSING


async def show_results(update: Update, context: ContextTypes.DEFAULT_TYPE):
    language = lang(context)
    matches = context.user_data.get("matches", [])

    lines = [t(language, "results_header").format(n=len(matches)), ""]
    for i, job in enumerate(matches, 1):
        bits = [esc(job.location), job.freshness]
        if job.salary:
            bits.append(esc(job.salary))
        lines.append(
            f"{job.icon} <b>{i}. {esc(job.title)}</b>\n"
            f"    {esc(job.company)}\n"
            f"    <i>{' · '.join(bits)}</i>"
        )
        if job.match_reason:
            lines.append(f"    ↳ {esc(job.match_reason)}")
        lines.append("")

    lines.append(t(language, "results_footer"))

    rows = [
        [(f"{job.icon} {i}. {job.title[:28]}", f"job:{i - 1}")]
        for i, job in enumerate(matches, 1)
    ]
    rows.append([(t(language, "resume_yes"), "resume:make")])

    await say(update, "\n".join(lines), keyboard(rows))


async def open_job(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    language = lang(context)
    index = int(query.data.split(":", 1)[1])

    matches = context.user_data.get("matches", [])
    if index >= len(matches):
        await say(update, t(language, "error"))
        return BROWSING

    job = matches[index]
    context.user_data["current_job"] = index
    profile = context.user_data["profile"]

    await say(update, t(language, "drafting"))
    await typing(update, context)

    try:
        if job.channel == jobsearch.CHANNEL_TEXT:
            await deliver_sms(update, context, job, profile, language)
        elif job.channel == jobsearch.CHANNEL_EMAIL:
            await deliver_email(update, context, job, profile, language)
        else:
            await deliver_crib(update, context, job, profile, language)
    except Exception:
        log.exception("drafting failed")
        await say(update, t(language, "error"))

    return BROWSING


async def deliver_sms(update, context, job, profile, language):
    draft = await asyncio.to_thread(brain.draft_sms, profile, job, language)
    message = draft.get("message", "")

    await say(update, t(language, "sms_ready").format(phone=esc(job.contact_phone)))
    await say(update, f"<code>{esc(message)}</code>")
    await say(update, t(language, "send_reminder"), back_keyboard(job, language))


async def deliver_email(update, context, job, profile, language):
    draft = await asyncio.to_thread(brain.draft_email, profile, job, language)

    await say(update, t(language, "email_ready").format(email=esc(job.contact_email)))
    await say(
        update,
        f"<b>{t(language, 'email_subject')}</b>\n<code>{esc(draft.get('subject', ''))}</code>",
    )
    await say(
        update,
        f"<b>{t(language, 'email_body')}</b>\n<code>{esc(draft.get('body', ''))}</code>",
    )
    await say(update, t(language, "send_reminder"), back_keyboard(job, language))


async def deliver_crib(update, context, job, profile, language):
    sheet = await asyncio.to_thread(brain.draft_crib_sheet, profile, job, language)

    await say(update, t(language, "crib_ready"))
    await say(update, f"<code>{esc(sheet)}</code>")
    await say(update, t(language, "ask_anything"), back_keyboard(job, language))


def back_keyboard(job, language) -> InlineKeyboardMarkup:
    rows = []
    if job.url:
        label = (
            t(language, "open_application")
            if job.channel == jobsearch.CHANNEL_FORM
            else t(language, "view_posting")
        )
        rows.append([InlineKeyboardButton(label, url=job.url)])
    rows.append([InlineKeyboardButton(t(language, "back"), callback_data="back")])
    return InlineKeyboardMarkup(rows)


async def go_back(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.callback_query.answer()
    context.user_data.pop("current_job", None)
    await show_results(update, context)
    return BROWSING


# --------------------------------------------------------------------------
# resume
# --------------------------------------------------------------------------


async def make_resume(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.callback_query.answer()
    language = lang(context)
    profile = context.user_data.get("profile", {})

    if not profile.get("roles"):
        await say(update, t(language, "resume_thin"))
        return BROWSING

    if not profile.get("name"):
        await say(update, t(language, "resume_need_name"))
        return RESUME_NAME

    return await build_resume(update, context)


async def got_resume_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["profile"]["name"] = (update.effective_message.text or "").strip()
    return await build_resume(update, context)


async def build_resume(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    language = lang(context)
    await say(update, t(language, "resume_building"))
    await typing(update, context)

    try:
        path = await asyncio.to_thread(
            resume_builder.build, context.user_data["profile"], OUT_DIR, language
        )
    except Exception:
        log.exception("resume build failed")
        path = None

    if not path:
        await say(update, t(language, "resume_thin"))
        return BROWSING

    with open(path, "rb") as handle:
        await update.effective_message.reply_document(
            document=handle, filename=path.name, caption=t(language, "resume_done")
        )
    return BROWSING


# --------------------------------------------------------------------------
# free-form help while browsing
# --------------------------------------------------------------------------


async def field_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    language = lang(context)
    question = update.effective_message.text or ""
    index = context.user_data.get("current_job")
    matches = context.user_data.get("matches", [])

    if index is None or index >= len(matches):
        await show_results(update, context)
        return BROWSING

    await say(update, t(language, "helping"))
    await typing(update, context)

    try:
        answer = await asyncio.to_thread(
            brain.answer_field_question,
            context.user_data["profile"], matches[index], question, language,
        )
        await say(update, esc(answer))
    except Exception:
        log.exception("field help failed")
        await say(update, t(language, "error"))

    return BROWSING


async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    language = lang(context)
    context.user_data.pop("profile", None)
    context.user_data.pop("matches", None)
    context.user_data.pop("certs", None)
    await say(update, t(language, "reset"))
    return EXPERIENCE


async def on_error(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    log.error("unhandled error", exc_info=context.error)


# --------------------------------------------------------------------------


def main() -> None:
    token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    if not token:
        raise SystemExit(
            "TELEGRAM_BOT_TOKEN is missing. Copy .env.example to .env and fill it in."
        )
    if not os.getenv("ANTHROPIC_API_KEY", "").strip():
        raise SystemExit(
            "ANTHROPIC_API_KEY is missing. Copy .env.example to .env and fill it in."
        )

    app = Application.builder().token(token).build()

    conversation = ConversationHandler(
        entry_points=[
            CommandHandler("start", start),
            MessageHandler(filters.TEXT & ~filters.COMMAND, start),
        ],
        states={
            LANG: [CallbackQueryHandler(set_language, pattern=r"^lang:")],
            CONFIRM: [CallbackQueryHandler(confirm_looking, pattern=r"^look:")],
            EXPERIENCE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, got_experience)
            ],
            NEIGHBORHOOD: [CallbackQueryHandler(got_neighborhood, pattern=r"^hood:")],
            NEIGHBORHOOD_TEXT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, got_neighborhood_text)
            ],
            DISTANCE: [CallbackQueryHandler(got_distance, pattern=r"^dist:")],
            AVAILABILITY: [CallbackQueryHandler(got_availability, pattern=r"^avail:")],
            CERTS: [CallbackQueryHandler(toggle_cert, pattern=r"^cert:")],
            BROWSING: [
                CallbackQueryHandler(open_job, pattern=r"^job:"),
                CallbackQueryHandler(go_back, pattern=r"^back$"),
                CallbackQueryHandler(make_resume, pattern=r"^resume:"),
                MessageHandler(filters.TEXT & ~filters.COMMAND, field_help),
            ],
            RESUME_NAME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, got_resume_name)
            ],
        },
        fallbacks=[CommandHandler("reset", reset), CommandHandler("start", start)],
        # allow_reentry MUST stay False. The entry points include a catch-all
        # text handler so that any first message ("hi", "hola") starts the bot.
        # With reentry enabled, that same handler also swallows every later
        # message, restarting the greeting instead of advancing the state —
        # the conversation can never get past question 1.
        allow_reentry=False,
    )

    app.add_handler(conversation)
    app.add_error_handler(on_error)

    log.info("Chamba is live. Press Ctrl-C to stop.")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
