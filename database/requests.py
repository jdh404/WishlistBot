from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import Game, User, Wishlist


async def get_or_create_user(session: AsyncSession, telegram_id: int, username: str | None) -> User:
    user = await session.scalar(select(User).where(User.telegram_id == telegram_id))
    if user is None:
        user = User(telegram_id=telegram_id, username=username)
        session.add(user)
    else:
        user.username = username
    await session.commit()
    return user


async def owned_wishlist(session: AsyncSession, wishlist_id: int, telegram_id: int) -> Wishlist | None:
    return await session.scalar(select(Wishlist).join(User).where(Wishlist.id == wishlist_id, User.telegram_id == telegram_id))


async def owned_game(session: AsyncSession, game_id: int, telegram_id: int) -> Game | None:
    return await session.scalar(select(Game).join(Wishlist).join(User).where(Game.id == game_id, User.telegram_id == telegram_id))

