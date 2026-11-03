from decimal import Decimal

from utils.validators import parse_currency, parse_price
from utils.game_parser import parse_game_list


def test_price_validation():
    assert parse_price("124,50") == Decimal("124.50")
    assert parse_price("-1") is None
    assert parse_price("abc") is None


def test_currency_validation():
    assert parse_currency("uah") == "UAH"
    assert parse_currency("gbp") is None


def test_parse_pasted_game_list():
    games, errors = parse_game_list("NieR Replicant - 559 UAH\nPotion Craft: Alchemist Simulator — 166.00 UAH")
    assert errors == []
    assert games == [("NieR Replicant", Decimal("559.00"), "UAH"), ("Potion Craft: Alchemist Simulator", Decimal("166.00"), "UAH")]

