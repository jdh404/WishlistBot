from dataclasses import dataclass
import os

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    bot_token: str
    database_url: str = "sqlite+aiosqlite:///wishlist.db"


def get_settings() -> Settings:
    token = os.getenv("BOT_TOKEN", "").strip()
    if not token:
        raise RuntimeError("BOT_TOKEN is not set in .env")
    return Settings(token, os.getenv("DATABASE_URL", "sqlite+aiosqlite:///wishlist.db"))

