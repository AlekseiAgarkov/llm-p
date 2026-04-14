import asyncio
import uuid
from typing import Optional
from unittest import IsolatedAsyncioTestCase

from sqlalchemy import select, delete, Result, Row
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker, AsyncEngine

from app.db.base import Base
from app.db.models import User
from app.repositories.users import UserRepository


class TestUserRepository(IsolatedAsyncioTestCase):
    engine: AsyncEngine
    async_session: async_sessionmaker[AsyncSession]
    session: AsyncSession

    @classmethod
    def setUpClass(cls):
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
        self.user_repo = UserRepository(self.session)

        self.email = "ceo@yandex.ru"
        self.password_hash = "хэш_стойкого_пароля_сео"
        self.non_existent_email = "404@yandex.ru"
        self.non_existent_id = uuid.uuid4()

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

    async def test_create_user(self):
        user: User = await self.user_repo.create(self.email, self.password_hash)

        self.assertIsNotNone(user.id)
        self.assertEqual(self.email, user.email)
        self.assertEqual(self.password_hash, user.password_hash)
        self.assertEqual("user", user.role)
        self.assertIsNotNone(user.created_at)

        stmt: Result[tuple[User]] = await self.session.execute(select(User).where(User.email == self.email))

        db_user: Optional[Row[tuple[User]]] = stmt.first()
        self.assertIsNotNone(db_user)

    async def test_create_user_duplicate_email(self):
        user = User(email=self.email, password_hash=self.password_hash)
        self.session.add(user)
        await self.session.commit()

        with self.assertRaises(IntegrityError):
            await self.user_repo.create(self.email, password_hash="поперчим" + self.password_hash + "посолим")

    async def test_get_by_email_existing(self):
        user = User(email=self.email, password_hash=self.password_hash)
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)

        found: Optional[User] = await self.user_repo.get_by_email(self.email)

        self.assertIsNotNone(found)
        self.assertEqual(user.id, found.id)
        self.assertEqual(self.email, found.email)
        self.assertEqual(self.password_hash, found.password_hash)

    async def test_get_by_id_existing(self):
        user: User = User(email=self.email, password_hash=self.password_hash)
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)

        found: Optional[User] = await self.user_repo.get_by_id(user.id)

        self.assertIsNotNone(found)
        self.assertEqual(user.id, found.id)
        self.assertEqual(self.email, found.email)

    async def test_get_by_email_nonexistent(self):
        found: Optional[User] = await self.user_repo.get_by_email(self.non_existent_email)
        self.assertIsNone(found)

    async def test_get_by_id_nonexistent(self):
        found: Optional[User] = await self.user_repo.get_by_id(self.non_existent_id)
        self.assertIsNone(found)
