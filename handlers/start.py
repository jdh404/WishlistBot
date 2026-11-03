from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from sqlalchemy.ext.asyncio import async_sessionmaker

from database.requests import get_or_create_user
from keyboards.main_menu import main_menu

router = Router()


@router.message(Command("cancel"))
async def cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Действие отменено.", reply_markup=main_menu())


@router.message(CommandStart())
async def start(message: Message, session_factory: async_sessionmaker):
    async with session_factory() as session:
        await get_or_create_user(session, message.from_user.id, message.from_user.username)
    await message.answer("🎮 Добро пожаловать в Game Wishlist!\n\nСоздавайте списки игр, следите за ценами и отмечайте покупки.", reply_markup=main_menu())

