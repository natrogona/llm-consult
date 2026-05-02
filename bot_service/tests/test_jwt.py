import pytest
from jose import jwt
from datetime import datetime, timezone, timedelta
from app.core.config import settings
from app.core.jwt import decode_and_validate, TokenError


def test_valid_token():
    now = datetime.now(timezone.utc)
    token = jwt.encode(
        {"sub": "1", "role": "user", "iat": int(now.timestamp()),
         "exp": int((now + timedelta(minutes=5)).timestamp())},
        settings.JWT_SECRET, algorithm=settings.JWT_ALG,
    )
    payload = decode_and_validate(token)
    assert payload["sub"] == "1"


def test_garbage_rejected():
    with pytest.raises(TokenError):
        decode_and_validate("not-a-token")