# Game Wishlist Telegram Bot

An asynchronous Telegram bot for managing personal game wishlists, tracking prices, marking purchased games, and viewing statistics.

## Features

- Multiple personal wishlists with cascade deletion.
- Game titles, prices, currencies, and purchase status.
- Supported currencies: UAH, PLN, EUR, and USD.
- Duplicate game protection within the same wishlist.
- Pagination for large wishlists.
- Sorting by price ascending, price descending, and title.
- Inline buttons for marking games as purchased.
- Statistics calculated separately for each currency.
- Wishlist renaming and deletion with confirmation.
- Game editing, deletion, searching, and moving between wishlists.
- FSM-based input validation.
- Ownership checks for every wishlist and game operation.
- SQLite database with SQLAlchemy 2.x.

## Requirements

- Python 3.12 or newer.
- A Telegram bot token created with `@BotFather`.

## Installation

Create and activate a virtual environment:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

Create the environment file:

```bash
cp .env.example .env
```

Open `.env` and replace `replace_with_telegram_bot_token` with your actual Telegram bot token:

```env
BOT_TOKEN=replace_with_telegram_bot_token
DATABASE_URL=sqlite+aiosqlite:///wishlist.db
```

Never commit `.env` or your real bot token to GitHub.

## Running

Start the bot from the project directory:

```bash
python bot.py
```

The SQLite database is created automatically on the first launch.

## Testing

Run the test suite with:

```bash
pytest
```

## User Interface

After `/start`, the bot displays a permanent reply keyboard with:

- ` My wishlists`
- ` New wishlist`
- ` Add games`
- ` Manage wishlists`
- ` Statistics`

Wishlist navigation, sorting, pagination, purchase status changes, and management actions use inline keyboards. Existing Telegram messages are edited where possible to keep the interface compact.

Use the following command to search for games:

```text
/search doom
```

## Project Structure

```text
wishlist_bot/
├── bot.py
├── config.py
├── database/
│   ├── database.py
│   ├── models.py
│   └── requests.py
├── handlers/
├── keyboards/
├── services/
├── states/
├── utils/
├── tests/
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## Deployment

For a VPS deployment, run the bot with `systemd`, Supervisor, or another process manager. Keep `.env` outside version control and use a dedicated service account with access only to the project directory.

## Security

Every database operation verifies the Telegram user who owns the wishlist or game. Callback data cannot be used to access another user's records. Prices and currencies are validated before being stored.
