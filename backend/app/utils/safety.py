SAFETY_MESSAGES = [
    # "Decision support only",
    # "Doctor verification required",
    # "Seek emergency help if red flags",
]


def ensure_safety(items: list[str] | None) -> list[str]:
    items = list(items or [])
    for msg in SAFETY_MESSAGES:
        if msg not in items:
            items.append(msg)
    return items


def safety_footer_text() -> str:
    return " | ".join(SAFETY_MESSAGES)
