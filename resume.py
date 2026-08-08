"""One-page resume PDF, generated only when a listing actually asks for one.

Most hourly roles never read a resume, so this is deliberately not the centre of
the product. When it is needed it has to be plain, one page, and printable at a
library — no columns, no colour, no icons, nothing that confuses an ATS parser.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

NAME = ParagraphStyle(
    "name", fontName="Helvetica-Bold", fontSize=17, leading=21, spaceAfter=2
)
CONTACT = ParagraphStyle(
    "contact", fontName="Helvetica", fontSize=9.5, leading=13, spaceAfter=12
)
HEADING = ParagraphStyle(
    "heading", fontName="Helvetica-Bold", fontSize=10.5, leading=14,
    spaceBefore=11, spaceAfter=4, alignment=TA_LEFT,
)
BODY = ParagraphStyle(
    "body", fontName="Helvetica", fontSize=10, leading=14, spaceAfter=3
)

LABELS = {
    "en": {
        "summary": "SUMMARY",
        "experience": "EXPERIENCE",
        "skills": "SKILLS",
        "certs": "CERTIFICATIONS",
        "availability": "AVAILABILITY",
        "languages": "LANGUAGES",
    },
    "es": {
        "summary": "RESUMEN",
        "experience": "EXPERIENCIA",
        "skills": "HABILIDADES",
        "certs": "CERTIFICACIONES",
        "availability": "DISPONIBILIDAD",
        "languages": "IDIOMAS",
    },
}


def _escape(text: str) -> str:
    return (
        str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    )


def build(profile: dict, out_dir: Path, language: str = "en") -> Optional[Path]:
    """Write a one-page PDF and return its path. Returns None if there is not
    enough in the profile to make something worth sending."""
    labels = LABELS.get(language, LABELS["en"])

    name = profile.get("name") or ""
    if not (name or profile.get("roles")):
        return None

    out_dir.mkdir(parents=True, exist_ok=True)
    safe = "".join(c for c in (name or "resume") if c.isalnum() or c in " -_").strip()
    path = out_dir / f"{safe or 'resume'}.pdf"

    doc = SimpleDocTemplate(
        str(path),
        pagesize=LETTER,
        leftMargin=0.85 * inch, rightMargin=0.85 * inch,
        topMargin=0.7 * inch, bottomMargin=0.7 * inch,
        title=f"{name} — Resume", author=name,
    )

    flow = [Paragraph(_escape(name or "—"), NAME)]

    contact_bits = [
        profile.get("phone"), profile.get("email"), profile.get("neighborhood")
    ]
    contact = "  ·  ".join(_escape(b) for b in contact_bits if b)
    if contact:
        flow.append(Paragraph(contact, CONTACT))
    else:
        flow.append(Spacer(1, 10))

    if profile.get("summary"):
        flow.append(Paragraph(labels["summary"], HEADING))
        flow.append(Paragraph(_escape(profile["summary"]), BODY))

    roles = profile.get("roles") or []
    employers = profile.get("employers") or []
    if roles:
        flow.append(Paragraph(labels["experience"], HEADING))
        for i, role in enumerate(roles[:6]):
            employer = employers[i] if i < len(employers) else ""
            line = f"<b>{_escape(role)}</b>"
            if employer:
                line += f" — {_escape(employer)}"
            flow.append(Paragraph(line, BODY))
        if profile.get("years_experience"):
            years = profile["years_experience"]
            word = "years" if language == "en" else "años"
            flow.append(Paragraph(f"{years} {word}", BODY))

    if profile.get("skills"):
        flow.append(Paragraph(labels["skills"], HEADING))
        flow.append(Paragraph(_escape(", ".join(profile["skills"][:14])), BODY))

    if profile.get("certifications"):
        flow.append(Paragraph(labels["certs"], HEADING))
        flow.append(Paragraph(_escape(", ".join(profile["certifications"][:8])), BODY))

    if profile.get("availability"):
        flow.append(Paragraph(labels["availability"], HEADING))
        flow.append(Paragraph(_escape(profile["availability"]), BODY))

    langs = []
    if profile.get("english_level"):
        langs.append(f"English ({profile['english_level']})")
    if language == "es":
        langs.append("Español")
    if langs:
        flow.append(Paragraph(labels["languages"], HEADING))
        flow.append(Paragraph(_escape(", ".join(langs)), BODY))

    doc.build(flow)
    return path
