from decimal import Decimal, InvalidOperation

SUPPORTED_CURRENCIES = {"UAH", "PLN", "EUR", "USD"}


def parse_price(value: str) -> Decimal | None:
    try:
        price = Decimal(value.replace(",", "."))
    except InvalidOperation:
        return None
    return price.quantize(Decimal("0.01")) if price >= 0 else None


def parse_currency(value: str) -> str | None:
    value = value.strip().upper()
    return value if value in SUPPORTED_CURRENCIES else None

