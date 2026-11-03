import re
from decimal import Decimal

from .validators import parse_currency, parse_price


# Accepts both an em dash (—), an en dash (–), and a regular hyphen.
GAME_LINE = re.compile(
    r"^\s*(?:\d+[.)]\s*)?(?P<title>.+?)\s*[—–-]\s*"
    r"(?P<price>\d+(?:[.,]\d+)?)\s*(?P<currency>[A-Za-zА-Яа-я]{3})\s*$"
)


def parse_game_list(text: str) -> tuple[list[tuple[str, Decimal, str]], list[str]]:
    """Parse pasted lines in the form `Game title — 123.00 UAH`."""
    games = []
    errors = []
    for line_number, line in enumerate(text.splitlines(), 1):
        if not line.strip():
            continue
        match = GAME_LINE.match(line)
        if not match:
            errors.append(f"строка {line_number}: {line.strip()}")
            continue
        title = match.group("title").strip()
        price = parse_price(match.group("price"))
        currency = parse_currency(match.group("currency"))
        if not title or price is None or currency is None:
            errors.append(f"строка {line_number}: {line.strip()}")
            continue
        games.append((title, price, currency))
    return games, errors
