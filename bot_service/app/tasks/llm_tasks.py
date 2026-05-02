import asyncio
from aiogram import Bot
from app.infra.celery_app import celery_app
from app.services.openrouter_client import call_openrouter
from app.core.config import settings


async def _run(tg_chat_id: int, prompt: str) -> None:
    answer = await call_openrouter(prompt)
    bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
    try:
        await bot.send_message(chat_id=tg_chat_id, text=answer)
    finally:
        await bot.session.close()


@celery_app.task(name="llm_request")
def llm_request(tg_chat_id: int, prompt: str) -> str:
    try:
        asyncio.run(_run(tg_chat_id, prompt))
        return "ok"
    except Exception as e:
        bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
        try:
            asyncio.run(bot.send_message(chat_id=tg_chat_id, text=f"Ошибка: {e}"))
        finally:
            asyncio.run(bot.session.close())
        return f"error: {e}"