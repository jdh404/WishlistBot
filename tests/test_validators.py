from decimal import Decimal

from utils.validators import parse_currency, parse_price


def test_price_validation():
    assert parse_price("124,50") == Decimal("124.50")
    assert parse_price("-1") is None
    assert parse_price("abc") is None


def test_currency_validation():
    assert parse_currency("uah") == "UAH"
    assert parse_currency("gbp") is None

