from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import async_sessionmaker

from keyboards.inline import list_keyboard, wishlist_keyboard
from keyboards.main_menu import main_menu
from services.game_service import games_for_list
from services.wishlist_service import create_wishlist, list_wishlists
from states.forms import WishlistForm

router = Router()


@router.message(F.text == "➕ Новый список")
async def new_list(message: Message, state: FSMContext):
    await state.set_state(WishlistForm.name)
    await message.answer("Введите название нового списка:")


@router.message(WishlistForm.name)
async def create_list(message: Message, state: FSMContext, session_factory: async_sessionmaker):
    name = message.text.strip()
    if not 1 <= len(name) <= 120:
        await message.answer("Название должно содержать от 1 до 120 символов.")
        return
    async with session_factory() as session:
        try:
            await create_wishlist(session, message.from_user.id, name)
        except Exception:
            await session.rollback()
            await message.answer("Такой список уже существует.")
            return
    await state.clear()
    await message.answer(f"✅ Список «{name}» создан.", reply_markup=main_menu())


async def show_lists(message: Message, session_factory: async_sessionmaker):
    async with session_factory() as session:
        wishlists = await list_wishlists(session, message.from_user.id)
    if not wishlists:
        await message.answer("📂 Списков пока нет. Создайте первый через «➕ Новый список».", reply_markup=main_menu())
    else:
        await message.answer("📂 Ваши списки:", reply_markup=wishlist_keyboard(wishlists))


@router.message(F.text == "📂 Мои списки")
async def my_lists(message: Message, session_factory: async_sessionmaker):
    await show_lists(message, session_factory)


@router.callback_query(F.data == "lists")
async def back_lists(callback: CallbackQuery, session_factory: async_sessionmaker):
    await callback.answer()
    async with session_factory() as session:
        wishlists = await list_wishlists(session, callback.from_user.id)
    await callback.message.edit_text("📂 Ваши списки:", reply_markup=wishlist_keyboard(wishlists))


@router.callback_query(F.data.startswith("view:"))
async def view_list(callback: CallbackQuery, session_factory: async_sessionmaker):
    await callback.answer()
    await render_list(callback, session_factory, int(callback.data.split(":")[1]), 1, "price_asc")


@router.callback_query(F.data.startswith("list:"))
async def sorted_list(callback: CallbackQuery, session_factory: async_sessionmaker):
    _, wid, page, sort = callback.data.split(":")
    await callback.answer()
    await render_list(callback, session_factory, int(wid), int(page), sort)


async def render_list(callback, session_factory, wishlist_id: int, page: int, sort: str):
    async with session_factory() as session:
        wishlist, games = await games_for_list(session, callback.from_user.id, wishlist_id, sort)
    if wishlist is None:
        await callback.message.edit_text("Список не найден.")
        return
    size = 10
    pages = max(1, (len(games) + size - 1) // size)
    page = max(1, min(page, pages))
    shown = games[(page - 1) * size: page * size]
    lines = [f"📂 {wishlist.name}", ""]
    lines += [f"{(page - 1) * size + i}. {'✅' if game.is_purchased else '⬜'} {game.title} — {game.price:.2f} {game.currency}" for i, game in enumerate(shown, 1)]
    if not shown: lines.append("В списке пока нет игр.")
    await callback.message.edit_text("\n".join(lines), reply_markup=list_keyboard(wishlist.id, shown, page, pages, sort))

