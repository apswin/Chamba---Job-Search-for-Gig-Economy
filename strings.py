"""All user-facing copy, in both languages.

Kept in one file so the Spanish can be read as Spanish rather than checked
line-by-line against the English. It is written to be spoken plainly — this is
read on a phone by someone who is out of work, often standing up.
"""

STRINGS = {
    "en": {
        "greet": (
            "Hi 👋 I'm Chamba.\n\n"
            "I find real jobs near you that are hiring <b>right now</b>, and I write "
            "the message you send to the employer.\n\n"
            "No account. No app. No resume needed."
        ),
        "pick_language": "First — which language?",
        "looking": "Are you looking for work?",
        "yes": "Yes",
        "no": "Not right now",
        "no_worries": (
            "No problem. Message me any time you want to look — just say hi. 👋"
        ),
        "q_experience": (
            "<b>Question 1 of 5</b>\n\n"
            "What kind of work have you done?\n\n"
            "Type it however you like — a few words is fine, or tell me the whole "
            "story. If you have an old resume, paste it in."
        ),
        "q_neighborhood": "<b>Question 2 of 5</b>\n\nWhere are you?",
        "q_distance": "<b>Question 3 of 5</b>\n\nHow far can you travel to work?",
        "q_availability": "<b>Question 4 of 5</b>\n\nWhen can you work?",
        "q_certs": (
            "<b>Question 5 of 5</b>\n\n"
            "Do you have any of these? Tap all that apply, then tap Done."
        ),
        "certs_done": "Done",
        "certs_none": "None of these",
        "thinking": "Got it. Looking for jobs that fit you… 🔎",
        "reading": "Reading what you told me… 📝",
        "no_jobs": (
            "I couldn't find fresh listings that fit right now. That happens — "
            "boards go quiet some days.\n\n"
            "Try /reset and describe your experience a little differently, or "
            "check back tomorrow."
        ),
        "results_header": "Here are your <b>{n} best matches</b>. All posted in the last 30 days:",
        "results_footer": "Tap a job to see it and get your message ready.",
        "how_to_apply": {
            "text": "📱 Apply by text",
            "email": "✉️ Apply by email",
            "form": "📝 Online application",
        },
        "drafting": "Writing your message… ✍️",
        "sms_ready": (
            "📱 <b>Text this number:</b> {phone}\n\n"
            "Here's your message — tap it to copy, then paste it into your texts:"
        ),
        "email_ready": (
            "✉️ <b>Email:</b> {email}\n\n"
            "Tap each part to copy it:"
        ),
        "email_subject": "Subject",
        "email_body": "Message",
        "crib_ready": (
            "📝 This one uses an online form. Here's the link, and every answer "
            "you'll need — tap to copy:"
        ),
        "open_application": "Open the application",
        "view_posting": "See the full posting",
        "send_reminder": (
            "⚠️ Read it before you send. Change anything that isn't right — "
            "it's your message, not mine."
        ),
        "back": "← Back to jobs",
        "resume_offer": "Want me to make you a resume PDF?",
        "resume_yes": "Yes, make my resume",
        "resume_building": "Building your resume… 📄",
        "resume_need_name": "What name should go on the resume?",
        "resume_done": (
            "Here's your resume. You can forward this to any employer, or save "
            "it and attach it to an application."
        ),
        "resume_thin": (
            "I don't have enough yet to make a resume worth sending. Tell me more "
            "about your work history first."
        ),
        "ask_anything": (
            "Stuck on a question in the form? Send it to me — type it or send a "
            "photo of the screen — and I'll tell you what to put."
        ),
        "helping": "Let me look… 🤔",
        "reset": "Starting over. What kind of work have you done?",
        "error": (
            "Something went wrong on my side. Try that again, or /reset to start over."
        ),
        "neighborhoods": [
            "Mission", "SoMa / Downtown", "Bayview", "Tenderloin",
            "Excelsior", "Richmond / Sunset", "Chinatown / North Beach",
            "Oakland", "Daly City", "Somewhere else",
        ],
        "type_neighborhood": "Type the name of your neighborhood or city:",
        "distances": [
            ("walk", "Walking distance"),
            ("transit30", "30 min on the bus"),
            ("transit60", "Up to an hour"),
            ("anywhere", "Anywhere in the Bay Area"),
        ],
        "availabilities": [
            ("mornings", "Mornings"),
            ("evenings", "Evenings / nights"),
            ("weekends", "Weekends"),
            ("anytime", "Any time — I need work"),
        ],
        "certs": [
            ("food_handler", "Food handler card"),
            ("drivers_license", "Driver's license"),
            ("own_car", "My own car"),
            ("forklift", "Forklift"),
            ("osha10", "OSHA 10"),
            ("own_tools", "My own tools"),
        ],
    },
    "es": {
        "greet": (
            "Hola 👋 Soy Chamba.\n\n"
            "Encuentro trabajos reales cerca de ti que están contratando "
            "<b>ahora mismo</b>, y escribo el mensaje que le mandas al patrón.\n\n"
            "Sin cuenta. Sin app. No necesitas currículum."
        ),
        "pick_language": "Primero — ¿en qué idioma?",
        "looking": "¿Estás buscando trabajo?",
        "yes": "Sí",
        "no": "Ahorita no",
        "no_worries": (
            "Está bien. Mándame un mensaje cuando quieras buscar — nomás di hola. 👋"
        ),
        "q_experience": (
            "<b>Pregunta 1 de 5</b>\n\n"
            "¿En qué has trabajado?\n\n"
            "Escríbelo como quieras — con pocas palabras está bien, o cuéntame todo. "
            "Si tienes un currículum viejo, pégalo aquí."
        ),
        "q_neighborhood": "<b>Pregunta 2 de 5</b>\n\n¿Dónde estás?",
        "q_distance": "<b>Pregunta 3 de 5</b>\n\n¿Qué tan lejos puedes viajar para trabajar?",
        "q_availability": "<b>Pregunta 4 de 5</b>\n\n¿Cuándo puedes trabajar?",
        "q_certs": (
            "<b>Pregunta 5 de 5</b>\n\n"
            "¿Tienes alguno de estos? Toca todos los que tengas y luego toca Listo."
        ),
        "certs_done": "Listo",
        "certs_none": "Ninguno",
        "thinking": "Perfecto. Buscando trabajos que te queden… 🔎",
        "reading": "Leyendo lo que me dijiste… 📝",
        "no_jobs": (
            "No encontré anuncios nuevos que te queden ahorita. Pasa — hay días "
            "en que no publican mucho.\n\n"
            "Prueba /reset y descríbeme tu experiencia de otra manera, o "
            "búscame mañana."
        ),
        "results_header": (
            "Aquí están tus <b>{n} mejores opciones</b>. Todas publicadas en los "
            "últimos 30 días:"
        ),
        "results_footer": "Toca un trabajo para verlo y preparar tu mensaje.",
        "how_to_apply": {
            "text": "📱 Aplicar por mensaje",
            "email": "✉️ Aplicar por correo",
            "form": "📝 Solicitud en línea",
        },
        "drafting": "Escribiendo tu mensaje… ✍️",
        "sms_ready": (
            "📱 <b>Manda un mensaje a este número:</b> {phone}\n\n"
            "Aquí está tu mensaje — tócalo para copiarlo y pégalo en tus mensajes:"
        ),
        "email_ready": (
            "✉️ <b>Correo:</b> {email}\n\n"
            "Toca cada parte para copiarla:"
        ),
        "email_subject": "Asunto",
        "email_body": "Mensaje",
        "crib_ready": (
            "📝 Este usa una solicitud en línea. Aquí está el enlace y todas las "
            "respuestas que vas a necesitar — tócalas para copiar:"
        ),
        "open_application": "Abrir la solicitud",
        "view_posting": "Ver el anuncio completo",
        "send_reminder": (
            "⚠️ Léelo antes de mandarlo. Cambia lo que no esté bien — "
            "es tu mensaje, no el mío."
        ),
        "back": "← Volver a los trabajos",
        "resume_offer": "¿Quieres que te haga un currículum en PDF?",
        "resume_yes": "Sí, hazme el currículum",
        "resume_building": "Haciendo tu currículum… 📄",
        "resume_need_name": "¿Qué nombre pongo en el currículum?",
        "resume_done": (
            "Aquí está tu currículum. Puedes reenviarlo a cualquier patrón, o "
            "guardarlo y adjuntarlo a una solicitud."
        ),
        "resume_thin": (
            "Todavía no tengo suficiente para hacerte un currículum que valga la "
            "pena mandar. Cuéntame más de tu experiencia primero."
        ),
        "ask_anything": (
            "¿Te atoraste con alguna pregunta de la solicitud? Mándamela — "
            "escríbela o mándame una foto de la pantalla — y te digo qué poner."
        ),
        "helping": "Déjame ver… 🤔",
        "reset": "Empezamos de nuevo. ¿En qué has trabajado?",
        "error": (
            "Algo falló de mi lado. Inténtalo otra vez, o usa /reset para empezar."
        ),
        "neighborhoods": [
            "Mission", "SoMa / Downtown", "Bayview", "Tenderloin",
            "Excelsior", "Richmond / Sunset", "Chinatown / North Beach",
            "Oakland", "Daly City", "Otro lugar",
        ],
        "type_neighborhood": "Escribe el nombre de tu barrio o ciudad:",
        "distances": [
            ("walk", "Caminando"),
            ("transit30", "30 min en camión"),
            ("transit60", "Hasta una hora"),
            ("anywhere", "Cualquier parte del Área de la Bahía"),
        ],
        "availabilities": [
            ("mornings", "Mañanas"),
            ("evenings", "Tardes / noches"),
            ("weekends", "Fines de semana"),
            ("anytime", "Cualquier hora — necesito trabajo"),
        ],
        "certs": [
            ("food_handler", "Tarjeta de manejo de alimentos"),
            ("drivers_license", "Licencia de manejar"),
            ("own_car", "Mi propio carro"),
            ("forklift", "Montacargas"),
            ("osha10", "OSHA 10"),
            ("own_tools", "Mis propias herramientas"),
        ],
    },
}

# Machine-readable values used for matching, kept separate from display text.
DISTANCE_KM = {"walk": 3, "transit30": 12, "transit60": 25, "anywhere": 60}

AVAILABILITY_TEXT = {
    "mornings": "mornings",
    "evenings": "evenings and nights",
    "weekends": "weekends",
    "anytime": "any shift, fully open",
}

CERT_TEXT = {
    "food_handler": "California food handler card",
    "drivers_license": "driver's license",
    "own_car": "has own car",
    "forklift": "forklift certified",
    "osha10": "OSHA 10",
    "own_tools": "has own tools",
}


def t(language: str, key: str) -> str:
    return STRINGS.get(language, STRINGS["en"]).get(key, STRINGS["en"].get(key, ""))
