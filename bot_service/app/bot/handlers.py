from aiogram import Router, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

from app.core.jwt import decode_and_validate, TokenError
from app.infra.redis import get_redis
from app.tasks.llm_tasks import llm_request

router = Router()
TOKEN_KEY = "token:{}"
TOKEN_TTL_SECONDS = 60 * 60


@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(
        "Привет. Это бот с доступом к большой языковой модели по JWT-токену.\n" 
        "Сначала пройдите регистрацию в Auth Service и получите JWT.\n"
        "Затем отправьте мне команду:\n/token <ваш_jwt>"
    )


@router.message(Command("token"))
async def cmd_token(message: Message):
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("Использование: /token <jwt>")
        return
    token = parts[1].strip()
    try:
        decode_and_validate(token)
    except TokenError as e:
        await message.answer(f"Токен отклонён: {e}")
        return
    redis = get_redis()
    await redis.set(TOKEN_KEY.format(message.from_user.id), token, ex=TOKEN_TTL_SECONDS)
    await message.answer("Токен принят и сохранён. Можете задавать вопросы.")


@router.message(F.text)
async def on_text(message: Message):
    redis = get_redis()
    token = await redis.get(TOKEN_KEY.format(message.from_user.id))
    if not token:
        await message.answer("Нет токена. Пройдите авторизацию и пришлите /token <jwt>.")
        return
    try:
        decode_and_validate(token)
    except TokenError as e:
        await message.answer(f"Токен невалиден ({e}). Пришлите новый /token <jwt>.")
        return
    llm_request.delay(message.chat.id, message.text)
    await message.answer("Запрос принят, обрабатываю…")