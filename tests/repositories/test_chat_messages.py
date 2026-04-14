import asyncio
from typing import List
from unittest import IsolatedAsyncioTestCase

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker, AsyncEngine

from app.db.base import Base
from app.db.models import ChatMessage, User
from app.repositories.chat_messages import ChatMessageRepository
from app.repositories.users import UserRepository


class TestChatMessageRepository(IsolatedAsyncioTestCase):
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

        cls.msg_txts = [
            """Алиса, напиши письмо на всех с приглашением на олхенц митинг.""",
            """Алиса, олхенц - это не то. Поищи определение в статье хэйч-би-ар, что ты вчера мне подсунула.""",
            """Алиса, не надо переводить "олхенц" просто так и напиши."""
        ]

    async def asyncSetUp(self):
        self.async_session = async_sessionmaker(self.engine,
                                                class_=AsyncSession,
                                                expire_on_commit=False)

        self.session = self.async_session()
        self.chat_message_repo = ChatMessageRepository(self.session)
        self.user_repo = UserRepository(self.session)

        self.email = "ceo@yandex.ru"
        self.role = "user"
        self.password_hash = "хэш_стойкого_пароля_сео"

        self.user: User = await self.user_repo.create(self.email, self.password_hash)

    async def asyncTearDown(self):
        await self.session.rollback()
        await self.session.execute(delete(User))
        await self.session.execute(delete(ChatMessage))
        await self.session.commit()
        await self.session.close()

    @classmethod
    def tearDownClass(cls):
        async def dispose_engine():
            await cls.engine.dispose()

        asyncio.run(dispose_engine())

    async def test_add_message(self):
        msg = await self.chat_message_repo.add(user_id=self.user.id,
                                               role=self.role,
                                               content=self.msg_txts[0])

        self.assertIsNotNone(msg.id)
        self.assertIsNotNone(msg.created_at)
        self.assertEqual("user", msg.role)
        self.assertEqual(self.msg_txts[0], msg.content)

    async def test_get_recent_nothing(self):
        msgs = await self.chat_message_repo.get_recent(user_id=self.user.id, limit=10)

        self.assertIsInstance(msgs, list)
        self.assertEqual(0, len(msgs))

    async def test_get_recent_gt_lim(self):
        for msg in self.msg_txts:
            await self.chat_message_repo.add(user_id=self.user.id, role=self.role, content=msg)

        msgs: List[ChatMessage] = await self.chat_message_repo.get_recent(user_id=self.user.id, limit=10)

        self.assertIsInstance(msgs, list)
        self.assertEqual(len(self.msg_txts), len(msgs))
        self.assertEqual(self.msg_txts[-1], msgs[0].content)
        self.assertEqual(self.msg_txts[0], msgs[-1].content)

    async def test_get_recent_lt_lim(self):
        lim = 2
        for msg in self.msg_txts:
            await self.chat_message_repo.add(user_id=self.user.id, role=self.role, content=msg)

        msgs: List[ChatMessage] = await self.chat_message_repo.get_recent(user_id=self.user.id, limit=lim)

        self.assertIsInstance(msgs, list)
        self.assertEqual(lim, len(msgs))
        self.assertEqual(self.msg_txts[-1], msgs[0].content)
        self.assertEqual(self.msg_txts[1], msgs[-1].content)

    async def test_delete_all_for_user(self):
        for msg in self.msg_txts:
            await self.chat_message_repo.add(user_id=self.user.id, role=self.role, content=msg)

        msgs: List[ChatMessage] = await self.chat_message_repo.get_recent(user_id=self.user.id, limit=10)

        self.assertIsInstance(msgs, list)
        self.assertEqual(len(self.msg_txts), len(msgs))
        self.assertEqual(self.msg_txts[-1], msgs[0].content)
        self.assertEqual(self.msg_txts[0], msgs[-1].content)

        await self.chat_message_repo.delete_all_for_user(user_id=self.user.id)

        msgs = await self.chat_message_repo.get_recent(user_id=self.user.id, limit=10)

        self.assertIsInstance(msgs, list)
        self.assertEqual(0, len(msgs))
