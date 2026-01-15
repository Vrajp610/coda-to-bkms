import os
import re
import requests
from dataclasses import dataclass
from datetime import date, timedelta
from typing import Dict, List


@dataclass(frozen=True)
class TelegramTarget:
    name: str
    token: str
    chat_id: str


TOKEN_RE = re.compile(r"^(?P<prefix>[A-Z0-9_]+)_TELEGRAM_TOKEN$")
CHAT_RE = re.compile(r"^(?P<prefix>[A-Z0-9_]+)_TELEGRAM_CHAT_ID$")


def build_targets_from_env(prefix_filter: str) -> List[TelegramTarget]:
    tokens: Dict[str, str] = {}
    chats: Dict[str, str] = {}

    for k, v in os.environ.items():
        m = TOKEN_RE.match(k)
        if m:
            tokens[m.group("prefix")] = v.strip()
            continue

        m = CHAT_RE.match(k)
        if m:
            chats[m.group("prefix")] = v.strip()

    prefixes = sorted((set(tokens.keys()) & set(chats.keys())))
    prefixes = [p for p in prefixes if p.startswith(prefix_filter)]

    if not prefixes:
        raise ValueError(
            f"No matching targets found for prefix '{prefix_filter}'. "
            f"Make sure you have {prefix_filter}*_TELEGRAM_TOKEN and {prefix_filter}*_TELEGRAM_CHAT_ID set."
        )

    return [TelegramTarget(name=p, token=tokens[p], chat_id=chats[p]) for p in prefixes]


def next_weekday(target_weekday: int, *, from_day: date | None = None) -> date:
    """
    Next occurrence of target_weekday (Mon=0 ... Sun=6), including today if today matches.
    """
    d = from_day or date.today()
    delta = (target_weekday - d.weekday()) % 7
    return d + timedelta(days=delta)


def format_date(d: date) -> str:
    return d.strftime("%b %d, %Y")  # e.g. "Jan 18, 2026"


def build_questions_using_sunday_date() -> List[str]:
    sunday = next_weekday(6)  # Sunday
    suffix = f"({format_date(sunday)})"
    return [
        f"Was P2 in Guju? {suffix}",
        f"Was 2 week prep cycle utilized? {suffix}",
    ]


def send_poll(token: str, chat_id: str, question: str) -> None:
    url = f"https://api.telegram.org/bot{token}/sendPoll"
    r = requests.post(
        url,
        json={
            "chat_id": chat_id,
            "question": question,
            "options": ["Yes", "No"],
            "is_anonymous": False,
            "allows_multiple_answers": False,
        },
        timeout=25,
    )
    r.raise_for_status()
    data = r.json()
    if not data.get("ok"):
        raise RuntimeError(f"Telegram API error for chat_id={chat_id}: {data}")


def send_polls_to_targets(targets: List[TelegramTarget], **kwargs) -> None:
    questions = build_questions_using_sunday_date()

    for t in targets:
        for q in questions:
            send_poll(t.token, t.chat_id, q)
        print(f"Sent 2 polls to {t.name} (chat_id={t.chat_id})")