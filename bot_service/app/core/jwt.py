from jose import jwt, JWTError, ExpiredSignatureError
from app.core.config import settings


class TokenError(ValueError):
    pass


def decode_and_validate(token: str) -> dict:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALG])
    except ExpiredSignatureError as e:
        raise TokenError("Token expired") from e
    except JWTError as e:
        raise TokenError("Invalid token") from e
    if "sub" not in payload:
        raise TokenError("Token has no sub")
    return payload