import re

EMAIL_RE = re.compile(r'[\\w\\.-]+@[\\w\\.-]+')
PHONE_RE = re.compile(r'\\+?\\d[\\d\\-\\s]{7,}\\d')


def mask_phi(text: str | None) -> str | None:
    if text is None:
        return None
    text = EMAIL_RE.sub('[email]', text)
    text = PHONE_RE.sub('[phone]', text)
    return text
