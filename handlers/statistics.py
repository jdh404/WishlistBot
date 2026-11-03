from aiogram import F, Router
from aiogram.types import Message
from sqlalchemy.ext.asyncio import async_sessionmaker

from services.statistics_service import statistics

router = Router()


def money(value):
    return f"{value:,.2f}".replace(",", " ")


@router.message(F.text == "📊 Статистика")
async def stats(message: Message, session_factory: async_sessionmaker):
    async with session_factory() as session:
        data = await statistics(session, message.from_user.id)
    total = data["total"]
    purchased = data["purchased"]
    lines = ["📊 Статистика", "", f"🎮 Всего игр: {total}", f"✅ Куплено: {purchased}", f"🛒 Осталось: {total - purchased}", ""]
    for currency, values in sorted(data["by_currency"].items()):
        lines += [f"💰 {currency}:", f"  Всего: {money(values['total'])}", f"  Потрачено: {money(values['purchased'])}", f"  Осталось: {money(values['total'] - values['purchased'])}"]
    percent = round(purchased / total * 100) if total else 0
    lines += ["", f"📈 Выполнение: {percent}%"]
    if data["max"]: lines.append(f"🏆 Самая дорогая: {data['max'].title} — {data['max'].price:.2f} {data['max'].currency}")
    if data["min"]: lines.append(f"💎 Самая дешёвая: {data['min'].title} — {data['min'].price:.2f} {data['min'].currency}")
    await message.answer("\n".join(lines))

