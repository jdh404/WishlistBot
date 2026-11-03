from collections import defaultdict
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Game, User, Wishlist


async def statistics(session: AsyncSession, telegram_id: int) -> dict:
    games = list((await session.scalars(select(Game).join(Wishlist).join(User).where(User.telegram_id == telegram_id))).all())
    by_currency = defaultdict(lambda: {"total": Decimal("0"), "purchased": Decimal("0")})
    for game in games:
        by_currency[game.currency]["total"] += Decimal(game.price)
        if game.is_purchased:
            by_currency[game.currency]["purchased"] += Decimal(game.price)
    return {"total": len(games), "purchased": sum(g.is_purchased for g in games), "by_currency": dict(by_currency), "max": max(games, key=lambda g: g.price, default=None), "min": min(games, key=lambda g: g.price, default=None)}

