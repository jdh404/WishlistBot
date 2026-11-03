from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, KeyboardButton, Message, ReplyKeyboardMarkup
from decimal import Decimal
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker

from database.models import User, Wishlist
from handlers.wishlists import render_list
from keyboards.inline import confirm_keyboard, manage_games_keyboard, move_targets_keyboard, wishlist_keyboard
from states.forms import EditGameForm, GameForm
from utils.validators import parse_currency, parse_price
from utils.game_parser import parse_game_list

router = Router()


@router.callback_query(F.data.startswith("games:"))
async def manage_games(callback: CallbackQuery, session_factory: async_sessionmaker):
    wishlist_id = int(callback.data.split(":")[1])
    from services.game_service import games_for_list
    async with session_factory() as session:
        wishlist, games = await games_for_list(session, callback.from_user.id, wishlist_id)
    await callback.answer()
    if not wishlist:
        await callback.message.edit_text("Список не найден.")
        return
    await callback.message.edit_text(f"✏️ Игры в списке «{wishlist.name}»:", reply_markup=manage_games_keyboard(games, wishlist_id))


@router.callback_query(F.data.startswith("movegame:"))
async def move_game_start(callback: CallbackQuery, session_factory: async_sessionmaker):
    _, game_id, source_id = callback.data.split(":")
    async with session_factory() as session:
        wishlists = list((await session.scalars(select(Wishlist).join(User).where(User.telegram_id == callback.from_user.id))).all())
    await callback.answer()
    await callback.message.edit_text("Выберите список назначения:", reply_markup=move_targets_keyboard(wishlists, int(game_id), int(source_id)))


@router.callback_query(F.data.startswith("move:"))
async def move_game_finish(callback: CallbackQuery, session_factory: async_sessionmaker):
    _, game_id, source_id, target_id = callback.data.split(":")
    from services.game_service import move_game
    async with session_factory() as session:
        ok = await move_game(session, callback.from_user.id, int(game_id), int(target_id))
        wishlist, games = await __import__("services.game_service", fromlist=["games_for_list"]).games_for_list(session, callback.from_user.id, int(source_id))
    await callback.answer("Игра перемещена" if ok else "Не удалось переместить игру", show_alert=not ok)
    await callback.message.edit_text(f"✏️ Игры в списке «{wishlist.name}»:", reply_markup=manage_games_keyboard(games, int(source_id)))


@router.callback_query(F.data.startswith("delete:game:"))
async def delete_game_request(callback: CallbackQuery):
    _, _, game_id, wishlist_id = callback.data.split(":")
    await callback.answer()
    await callback.message.edit_text("Удалить эту игру?", reply_markup=confirm_keyboard(f"game:{wishlist_id}", int(game_id)))


@router.callback_query(F.data.startswith("confirm_yes:game:"))
async def delete_game_confirm(callback: CallbackQuery, session_factory: async_sessionmaker):
    _, _, wishlist_id, game_id = callback.data.split(":")
    from services.game_service import delete_game
    async with session_factory() as session:
        ok = await delete_game(session, callback.from_user.id, int(game_id))
        wishlist, games = await __import__("services.game_service", fromlist=["games_for_list"]).games_for_list(session, callback.from_user.id, int(wishlist_id))
    await callback.answer("Игра удалена" if ok else "Игра не найдена")
    await callback.message.edit_text(f"✏️ Игры в списке «{wishlist.name}»:", reply_markup=manage_games_keyboard(games, int(wishlist_id)))


@router.callback_query(F.data.startswith("editgame:"))
async def edit_game_start(callback: CallbackQuery, state: FSMContext):
    _, game_id, _ = callback.data.split(":")
    await state.update_data(game_id=int(game_id))
    await state.set_state(EditGameForm.title)
    await callback.answer()
    await callback.message.answer("Введите новое название игры:")


@router.message(EditGameForm.title)
async def edit_title(message: Message, state: FSMContext):
    await state.update_data(title=message.text.strip())
    await state.set_state(EditGameForm.price)
    await message.answer("Введите новую цену:")


@router.message(EditGameForm.price)
async def edit_price(message: Message, state: FSMContext):
    price = parse_price(message.text)
    if price is None:
        await message.answer("Введите корректную неотрицательную цену.")
        return
    await state.update_data(price=str(price))
    await state.set_state(EditGameForm.currency)
    await message.answer("Введите валюту: UAH, PLN, EUR или USD")


@router.message(EditGameForm.currency)
async def edit_currency(message: Message, state: FSMContext, session_factory: async_sessionmaker):
    currency = parse_currency(message.text)
    if currency is None:
        await message.answer("Допустимые валюты: UAH, PLN, EUR, USD.")
        return
    data = await state.get_data()
    from decimal import Decimal
    from services.game_service import update_game
    async with session_factory() as session:
        ok = await update_game(session, message.from_user.id, data["game_id"], data["title"], Decimal(data["price"]), currency)
    await state.clear()
    await message.answer("✅ Игра обновлена." if ok else "Игра не найдена.")


@router.message(F.text.startswith("/search"))
async def search_games(message: Message, session_factory: async_sessionmaker):
    query = message.text.partition(" ")[2].strip()
    if len(query) < 2:
        await message.answer("Использование: /search название игры")
        return
    async with session_factory() as session:
        rows = list((await session.scalars(select(__import__("database.models", fromlist=["Game"]).Game).join(Wishlist).join(User).where(User.telegram_id == message.from_user.id, __import__("database.models", fromlist=["Game"]).Game.title.ilike(f"%{query}%")))).all())
    if not rows:
        await message.answer("Ничего не найдено.")
        return
    await message.answer("🔎 Найдено:\n" + "\n".join(f"• {game.title} — {game.price:.2f} {game.currency}" for game in rows))


@router.message(F.text == "➕ Добавить игры")
async def choose_list(message: Message, session_factory: async_sessionmaker):
    async with session_factory() as session:
        wishlists = list((await session.scalars(select(Wishlist).join(User).where(User.telegram_id == message.from_user.id))).all())
    if wishlists:
        await message.answer("Выберите список для добавления игр:", reply_markup=wishlist_keyboard(wishlists, "add"))
    else:
        await message.answer("Сначала создайте список.")


@router.callback_query(F.data.startswith("add:"))
async def begin_add(callback: CallbackQuery, state: FSMContext):
    await state.update_data(wishlist_id=int(callback.data.split(":")[1]))
    await state.set_state(GameForm.title)
    await callback.answer()
    await callback.message.answer("Введите название игры или /cancel для отмены:")


@router.message(GameForm.title)
async def game_title(message: Message, state: FSMContext, session_factory: async_sessionmaker):
    if "\n" in message.text:
        games, errors = parse_game_list(message.text)
        if games:
            await state.update_data(bulk_games=games)
            await state.set_state(GameForm.currency)
            await message.answer("Список распознан. Добавляю игры…")
            # Reuse the normal save handler without asking for currency again.
            await save_bulk_games(message, state, session_factory)
            if errors:
                await message.answer("Не удалось распознать:\n" + "\n".join(errors))
            return
        if errors:
            await message.answer("Не удалось распознать строки. Формат: Название — 123.00 UAH")
            return
    if not message.text.strip():
        await message.answer("Название не может быть пустым.")
        return
    await state.update_data(title=message.text.strip())
    await state.set_state(GameForm.price)
    await message.answer("Введите цену, например: 124.00")


async def save_bulk_games(message: Message, state: FSMContext, session_factory):
    from services.game_service import add_game

    data = await state.get_data()
    added = []
    duplicates = []
    async with session_factory() as session:
        for title, price, currency in data["bulk_games"]:
            game, error = await add_game(session, message.from_user.id, data["wishlist_id"], title, price, currency)
            if game:
                added.append(game)
            elif error:
                duplicates.append(title)
        await session.commit()
    await state.clear()
    added.sort(key=lambda game: Decimal(game.price), reverse=True)
    lines = ["✅ Добавлено:"]
    lines.extend(f"{i}. {game.title} — {game.price:.2f} {game.currency}" for i, game in enumerate(added, 1))
    if duplicates:
        lines.append("\nУже были в списке: " + ", ".join(duplicates))
    await message.answer("\n".join(lines), reply_markup=ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="📂 Мои списки")]], resize_keyboard=True))


@router.message(GameForm.price)
async def game_price(message: Message, state: FSMContext):
    price = parse_price(message.text)
    if price is None:
        await message.answer("Введите корректную неотрицательную цену.")
        return
    await state.update_data(price=str(price))
    await state.set_state(GameForm.currency)
    await message.answer("Выберите валюту: UAH, PLN, EUR или USD", reply_markup=ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text=c) for c in ("UAH", "PLN")], [KeyboardButton(text=c) for c in ("EUR", "USD")]], resize_keyboard=True))


@router.message(GameForm.currency)
async def game_currency(message: Message, state: FSMContext, session_factory: async_sessionmaker):
    currency = parse_currency(message.text)
    if currency is None:
        await message.answer("Допустимые валюты: UAH, PLN, EUR, USD.")
        return
    data = await state.get_data()
    from decimal import Decimal
    from services.game_service import add_game
    async with session_factory() as session:
        _, error = await add_game(session, message.from_user.id, data["wishlist_id"], data["title"], Decimal(data["price"]), currency)
    if error:
        await message.answer(f"⚠️ {error}")
        return
    await state.clear()
    await message.answer("✅ Игра добавлена. Можно добавить следующую через меню.", reply_markup=ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="➕ Добавить игры")], [KeyboardButton(text="📂 Мои списки")]], resize_keyboard=True))


@router.callback_query(F.data.startswith("toggle:"))
async def toggle(callback: CallbackQuery, session_factory: async_sessionmaker):
    _, game_id, wishlist_id, page, sort = callback.data.split(":")
    from services.game_service import toggle_game
    async with session_factory() as session:
        game = await toggle_game(session, callback.from_user.id, int(game_id))
    if not game:
        await callback.answer("Игра не найдена", show_alert=True)
        return
    await callback.answer("Статус обновлён")
    await render_list(callback, session_factory, int(wishlist_id), int(page), sort)

