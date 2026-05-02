from app.core.security import hash_password, verify_password, create_access_token
from app.core.exceptions import (
    UserAlreadyExistsError, InvalidCredentialsError, UserNotFoundError,
)
from app.repositories.users import UsersRepository


class AuthUseCase:
    def __init__(self, users_repo: UsersRepository):
        self.users = users_repo

    async def register(self, email: str, password: str):
        if await self.users.get_by_email(email):
            raise UserAlreadyExistsError()
        return await self.users.create(email=email, password_hash=hash_password(password))

    async def login(self, email: str, password: str) -> str:
        user = await self.users.get_by_email(email)
        if not user or not verify_password(password, user.password_hash):
            raise InvalidCredentialsError()
        return create_access_token(sub=str(user.id), role=user.role)

    async def me(self, user_id: int):
        user = await self.users.get_by_id(user_id)
        if not user:
            raise UserNotFoundError()
        return user