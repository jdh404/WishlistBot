from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import async_sessionmaker

from keyboards.inline import confirm_keyboard, manage_wishlists_keyboard
from services.wishlist_service import delete_wishlist, list_wishlists, rename_wishlist
from states.forms import RenameForm

router = Router()


@router.message(F.text == "✏️ Управлять списками")
async def management(message: Message, session_factory: async_sessionmaker):
    async with session_factory() as session:
        wishlists = await list_wishlists(session, message.from_user.id)
    await message.answer("✏️ Управление списками:", reply_markup=manage_wishlists_keyboard(wishlists))


@router.callback_query(F.data.startswith("rename:"))
async def rename_start(callback: CallbackQuery, state: FSMContext):
    await state.update_data(wishlist_id=int(callback.data.split(":")[1]))
    await state.set_state(RenameForm.name)
    await callback.answer()
    await callback.message.answer("Введите новое название списка:")


@router.message(RenameForm.name)
async def rename_finish(message: Message, state: FSMContext, session_factory: async_sessionmaker):
    name = message.text.strip()
    if not 1 <= len(name) <= 120:
        await message.answer("Название должно содержать от 1 до 120 символов.")
        return
    data = await state.get_data()
    async with session_factory() as session:
        try:
            ok = await rename_wishlist(session, message.from_user.id, data["wishlist_id"], name)
        except Exception:
            await session.rollback()
            ok = False
    await state.clear()
    await message.answer("✅ Список переименован." if ok else "Не удалось переименовать список.")


@router.callback_query(F.data.startswith("delete:list:"))
async def delete_request(callback: CallbackQuery):
    wishlist_id = int(callback.data.split(":")[2])
    await callback.answer()
    await callback.message.edit_text("Удалить список вместе со всеми играми?", reply_markup=confirm_keyboard("list", wishlist_id))


@router.callback_query(F.data.startswith("confirm_yes:list:"))
async def delete_confirm(callback: CallbackQuery, session_factory: async_sessionmaker):
    wishlist_id = int(callback.data.split(":")[2])
    async with session_factory() as session:
        ok = await delete_wishlist(session, callback.from_user.id, wishlist_id)
        wishlists = await list_wishlists(session, callback.from_user.id)
    await callback.answer("Список удалён" if ok else "Список не найден")
    await callback.message.edit_text("✏️ Управление списками:", reply_markup=manage_wishlists_keyboard(wishlists))


@router.callback_query(F.data == "noop")
async def noop(callback: CallbackQuery):
    await callback.answer()

