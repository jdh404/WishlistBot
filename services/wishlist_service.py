from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import User, Wishlist
from database.requests import owned_wishlist


async def list_wishlists(session: AsyncSession, telegram_id: int):
    return list((await session.scalars(select(Wishlist).join(User).where(User.telegram_id == telegram_id).order_by(Wishlist.created_at))).all())


async def create_wishlist(session: AsyncSession, telegram_id: int, name: str) -> Wishlist:
    user = await session.scalar(select(User).where(User.telegram_id == telegram_id))
    wishlist = Wishlist(user_id=user.id, name=name)
    session.add(wishlist)
    await session.commit()
    return wishlist


async def rename_wishlist(session: AsyncSession, telegram_id: int, wishlist_id: int, name: str) -> bool:
    wishlist = await owned_wishlist(session, wishlist_id, telegram_id)
    if not wishlist:
        return False
    wishlist.name = name
    await session.commit()
    return True


async def delete_wishlist(session: AsyncSession, telegram_id: int, wishlist_id: int) -> bool:
    wishlist = await owned_wishlist(session, wishlist_id, telegram_id)
    if not wishlist:
        return False
    await session.delete(wishlist)
    await session.commit()
    return True

