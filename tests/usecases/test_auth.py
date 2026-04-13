import asyncio
import uuid
from typing import Dict, Any
from unittest import IsolatedAsyncioTestCase

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine, async_sessionmaker, create_async_engine

from app.core.config import Settings
from app.core.errors import EmailAlreadyRegisteredError, UnauthorizedError, NotFoundError
from app.core.security import decode_token, JWTTokenType
from app.db.base import Base
from app.db.models import User
from app.repositories.users import UserRepository
from app.usecases.auth import AuthUseCase
from schemas.user import UserPublic


class TestUserAuthUsecase(IsolatedAsyncioTestCase):
    engine: AsyncEngine
    async_session: async_sessionmaker[AsyncSession]
    session: AsyncSession
    settings: Settings

    @classmethod
    def setUpClass(cls):
        cls.settings = Settings(_env_file=".env.example")
        cls.engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)

        async def create_tables():
            async with cls.engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)

        asyncio.run(create_tables())

    async def asyncSetUp(self):
        self.async_session = async_sessionmaker(self.engine,
                                                class_=AsyncSession,
                                                expire_on_commit=False)

        self.session = self.async_session()
        user_repo = UserRepository(self.session)

        self.registered_user_email = "ceo@yandex.ru"
        self.registered_user_password = "стойкий_пароль_сео"
        self.registered_user_password_hash = "$2b$12$ceLY5tP4bbpvHRRPqSHflO4BEXqQK7SA.vil89ktIhaUYTWW3ORUS"

        registered_user: User = await user_repo.create(self.registered_user_email, self.registered_user_password_hash)
        self.registered_user_id: uuid.UUID = registered_user.id

        self.non_existent_email = "404@yandex.ru"
        self.non_existent_id = uuid.uuid4()

        self.auth_use_case = AuthUseCase(user_repository=user_repo, settings=self.settings)

    async def asyncTearDown(self):
        await self.session.rollback()
        await self.session.execute(delete(User))
        await self.session.commit()
        await self.session.close()

    @classmethod
    def tearDownClass(cls):
        async def dispose_engine():
            await cls.engine.dispose()

        asyncio.run(dispose_engine())

    async def test_register(self):
        new_profile = await self.auth_use_case.register(email=self.non_existent_email,
                                                    password="str0ng_password")

        self.assertIsInstance(new_profile.id, uuid.UUID)
        self.assertEqual(self.non_existent_email, new_profile.email)
        self.assertEqual("user", new_profile.role)

    async def test_register_existing(self):
        with self.assertRaises(EmailAlreadyRegisteredError):
            await self.auth_use_case.register(email=self.registered_user_email,
                                              password=self.registered_user_password)

    async def test_login(self):
        token: str = await self.auth_use_case.login(email=self.registered_user_email,
                                                    password=self.registered_user_password)
        decoded_token: Dict[str, Any] = decode_token(token=token,
                                                     jwt_secret=self.settings.JWT_SECRET,
                                                     jwt_algorithm=self.settings.JWT_ALG)
        self.assertEqual(str(self.registered_user_id), decoded_token["sub"])
        self.assertEqual(JWTTokenType.access.name, decoded_token["type"])

    async def test_login_non_existent_user(self):
        with self.assertRaises(UnauthorizedError):
            await self.auth_use_case.login(email=self.non_existent_email,
                                           password=self.registered_user_password)

    async def test_login_wrong_password(self):
        with self.assertRaises(UnauthorizedError):
            await self.auth_use_case.login(email=self.registered_user_email,
                                           password="соскочил палец")

    async def test_get_profile(self):
        profile: UserPublic = await self.auth_use_case.get_profile(user_id=self.registered_user_id)

        self.assertEqual(self.registered_user_id, profile.id)
        self.assertEqual(self.registered_user_email, profile.email)
        self.assertEqual("user", profile.role)

    async def test_get_profile_non_existent(self):
        with self.assertRaises(NotFoundError):
            await self.auth_use_case.get_profile(user_id=self.non_existent_id)
