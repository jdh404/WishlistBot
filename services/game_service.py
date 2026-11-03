from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Game, User, Wishlist
from database.requests import owned_game, owned_wishlist


async def games_for_list(session: AsyncSession, telegram_id: int, wishlist_id: int, sort: str = "price_asc"):
    wishlist = await owned_wishlist(session, wishlist_id, telegram_id)
    if not wishlist:
        return None, []
    games = list((await session.scalars(select(Game).where(Game.wishlist_id == wishlist_id))).all())
    if sort == "price_desc":
        games.sort(key=lambda game: (game.currency, Decimal(game.price)), reverse=True)
    elif sort == "title":
        games.sort(key=lambda game: game.title.casefold())
    else:
        games.sort(key=lambda game: (game.currency, Decimal(game.price), game.title.casefold()))
    return wishlist, games


async def add_game(session: AsyncSession, telegram_id: int, wishlist_id: int, title: str, price: Decimal, currency: str) -> tuple[Game | None, str | None]:
    wishlist = await owned_wishlist(session, wishlist_id, telegram_id)
    if not wishlist:
        return None, "Список не найден"
    duplicate = await session.scalar(select(Game).where(Game.wishlist_id == wishlist_id, Game.title.ilike(title)))
    if duplicate:
        return None, "Такая игра уже есть в этом списке"
    game = Game(wishlist_id=wishlist_id, title=title, price=price, currency=currency)
    session.add(game)
    await session.commit()
    return game, None


async def toggle_game(session: AsyncSession, telegram_id: int, game_id: int) -> Game | None:
    game = await owned_game(session, game_id, telegram_id)
    if not game:
        return None
    game.is_purchased = not game.is_purchased
    await session.commit()
    return game


async def delete_game(session: AsyncSession, telegram_id: int, game_id: int) -> bool:
    game = await owned_game(session, game_id, telegram_id)
    if not game:
        return False
    await session.delete(game)
    await session.commit()
    return True


async def update_game(session: AsyncSession, telegram_id: int, game_id: int, title: str, price: Decimal, currency: str) -> bool:
    game = await owned_game(session, game_id, telegram_id)
    if not game:
        return False
    game.title, game.price, game.currency = title, price, currency
    await session.commit()
    return True


async def move_game(session: AsyncSession, telegram_id: int, game_id: int, target_wishlist_id: int) -> bool:
    game = await owned_game(session, telegram_id, game_id)
    target = await owned_wishlist(session, target_wishlist_id, telegram_id)
    if not game or not target:
        return False
    duplicate = await session.scalar(select(Game).where(Game.wishlist_id == target.id, Game.title.ilike(game.title)))
    if duplicate:
        return False
    game.wishlist_id = target.id
    await session.commit()
    return True

