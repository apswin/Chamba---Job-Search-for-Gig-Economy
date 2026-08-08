"""Deep links that hand the send back to the worker.

We never send on someone's behalf from our own number or domain. If we did, the
employer's reply would land in our inbox instead of theirs, which is worse than
useless to someone waiting on a callback. Instead we prefill their own texting
app and their own mail app, and they press send.
"""

from __future__ import annotations

import re
from urllib.parse import quote


def _digits(phone: str) -> str:
    digits = re.sub(r"\D", "", phone or "")
    if len(digits) == 10:
        return f"+1{digits}"
    if len(digits) == 11 and digits.startswith("1"):
        return f"+{digits}"
    return f"+{digits}" if digits else ""


def sms_link(phone: str, body: str) -> str:
    """Open the user's own messaging app with the number and message filled in.

    The `?&body=` form is the one that works on both iOS and Android; iOS alone
    accepts `&body=` and Android alone accepts `?body=`.
    """
    number = _digits(phone)
    if not number:
        return ""
    return f"sms:{number}?&body={quote(body)}"


def mailto_link(address: str, subject: str, body: str) -> str:
    if not address:
        return ""
    return f"mailto:{address}?subject={quote(subject)}&body={quote(body)}"


def tel_link(phone: str) -> str:
    number = _digits(phone)
    return f"tel:{number}" if number else ""
