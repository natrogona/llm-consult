from app.core.security import hash_password, verify_password, create_access_token
from jose import jwt
from app.core.config import settings


def test_hash_is_not_plain():
    h = hash_password("secret")
    assert h != "secret"
    assert verify_password("secret", h)
    assert not verify_password("wrong", h)


def test_jwt_payload():
    token = create_access_token(sub="42", role="user")
    payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALG])
    assert payload["sub"] == "42"
    assert payload["role"] == "user"
    assert "iat" in payload and "exp" in payload