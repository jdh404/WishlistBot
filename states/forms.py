from aiogram.fsm.state import State, StatesGroup


class WishlistForm(StatesGroup):
    name = State()


class GameForm(StatesGroup):
    wishlist_id = State()
    title = State()
    price = State()
    currency = State()


class RenameForm(StatesGroup):
    wishlist_id = State()
    name = State()


class EditGameForm(StatesGroup):
    game_id = State()
    title = State()
    price = State()
    currency = State()

