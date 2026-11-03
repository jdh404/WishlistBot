from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def wishlist_keyboard(wishlists, action: str = "view"):
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=f"📂 {w.name}", callback_data=f"{action}:{w.id}")] for w in wishlists])


def list_keyboard(wishlist_id: int, games, page: int, pages: int, sort: str):
    game_buttons = [
        InlineKeyboardButton(
            text=f"{i + 1}{' ✅' if game.is_purchased else ''}",
            callback_data=f"toggle:{game.id}:{wishlist_id}:{page}:{sort}",
        )
        for i, game in enumerate(games)
    ]
    # Five buttons per row keeps the number and the check mark readable.
    rows = [game_buttons[i:i + 5] for i in range(0, len(game_buttons), 5)]
    rows.append([
        InlineKeyboardButton(text="Цена ↑", callback_data=f"list:{wishlist_id}:{page}:price_asc"),
        InlineKeyboardButton(text="Цена ↓", callback_data=f"list:{wishlist_id}:{page}:price_desc"),
        InlineKeyboardButton(text="А-Я", callback_data=f"list:{wishlist_id}:{page}:title"),
    ])
    if pages > 1:
        nav = []
        if page > 1: nav.append(InlineKeyboardButton(text="‹", callback_data=f"list:{wishlist_id}:{page - 1}:{sort}"))
        nav.append(InlineKeyboardButton(text=f"{page}/{pages}", callback_data="noop"))
        if page < pages: nav.append(InlineKeyboardButton(text="›", callback_data=f"list:{wishlist_id}:{page + 1}:{sort}"))
        rows.append(nav)
    rows.append([InlineKeyboardButton(text="✏️ Управление играми", callback_data=f"games:{wishlist_id}"), InlineKeyboardButton(text="↩️ Списки", callback_data="lists")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def confirm_keyboard(prefix: str, item_id: int):
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Удалить", callback_data=f"confirm_yes:{prefix}:{item_id}"), InlineKeyboardButton(text="Отмена", callback_data="noop")]])


def manage_wishlists_keyboard(wishlists):
    rows = []
    for wishlist in wishlists:
        rows.append([
            InlineKeyboardButton(text=f"✏️ {wishlist.name}", callback_data=f"rename:{wishlist.id}"),
            InlineKeyboardButton(text="🗑", callback_data=f"delete:list:{wishlist.id}"),
        ])
    rows.append([InlineKeyboardButton(text="↩️ Назад", callback_data="lists")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def manage_games_keyboard(games, wishlist_id):
    rows = []
    for game in games:
        rows.append([
            InlineKeyboardButton(text=f"✏️ {game.title[:24]}", callback_data=f"editgame:{game.id}:{wishlist_id}"),
            InlineKeyboardButton(text="↗️", callback_data=f"movegame:{game.id}:{wishlist_id}"),
            InlineKeyboardButton(text="🗑", callback_data=f"delete:game:{game.id}:{wishlist_id}"),
        ])
    rows.append([InlineKeyboardButton(text="↩️ Списки", callback_data="lists")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def move_targets_keyboard(wishlists, game_id, source_id):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"📂 {wishlist.name}", callback_data=f"move:{game_id}:{source_id}:{wishlist.id}")]
        for wishlist in wishlists if wishlist.id != source_id
    ] or [[InlineKeyboardButton(text="Отмена", callback_data="noop")]])

