import pytest
import respx
import httpx
from app.core.config import settings
from app.services.openrouter_client import call_openrouter


@pytest.mark.asyncio
@respx.mock
async def test_openrouter_call():
    url = f"{settings.OPENROUTER_BASE_URL}/chat/completions"
    respx.post(url).mock(return_value=httpx.Response(
        200, json={"choices": [{"message": {"content": "Hi there"}}]}
    ))
    answer = await call_openrouter("hello")
    assert answer == "Hi there"