import pytest
from datetime import datetime, timezone, timedelta
from jose import jwt
from unittest.mock import AsyncMock, MagicMock

from app.core.config import settings
from app.bot import handlers


def make_message(text: str, user_id: int = 100, chat_id: int = 200):
    msg = MagicMock()
    msg.text = text
    msg.from_user.id = user_id
    msg.chat.id = chat_id
    msg.answer = AsyncMock()
    return msg


def make_jwt():
    now = datetime.now(timezone.utc)
    return jwt.encode(
        {"sub": "1", "role": "user", "iat": int(now.timestamp()),
         "exp": int((now + timedelta(minutes=5)).timestamp())},
        settings.JWT_SECRET, algorithm=settings.JWT_ALG,
    )


@pytest.mark.asyncio
async def test_token_saved(fake_redis):
    msg = make_message(f"/token {make_jwt()}")
    await handlers.cmd_token(msg)
    saved = await fake_redis.get("token:100")
    assert saved is not None
    msg.answer.assert_awaited()


@pytest.mark.asyncio
async def test_no_token_no_celery(fake_redis, mocker):
    delay = mocker.patch("app.bot.handlers.llm_request.delay")
    msg = make_message("Hello")
    await handlers.on_text(msg)
    delay.assert_not_called()


@pytest.mark.asyncio
async def test_with_token_calls_celery(fake_redis, mocker):
    await fake_redis.set("token:100", make_jwt())
    delay = mocker.patch("app.bot.handlers.llm_request.delay")
    msg = make_message("Hello")
    await handlers.on_text(msg)
    delay.assert_called_once_with(200, "Hello")
    msg.answer.assert_awaited()