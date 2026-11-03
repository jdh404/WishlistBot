from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


def main_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="📂 Мои списки"), KeyboardButton(text="➕ Новый список")],
        [KeyboardButton(text="➕ Добавить игры"), KeyboardButton(text="✏️ Управлять списками")],
        [KeyboardButton(text="📊 Статистика")],
    ], resize_keyboard=True, input_field_placeholder="Выберите действие")

