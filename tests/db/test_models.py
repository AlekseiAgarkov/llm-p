from datetime import datetime
from time import sleep
from typing import Optional, List
from unittest import TestCase
from uuid import UUID

from sqlalchemy import create_engine, Engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.base import Base
from app.db.models import User, ChatMessage


class BaseTestClass(TestCase):
    user: User
    session: Session
    engine: Engine

    @classmethod
    def setUpClass(cls):
        cls.engine: Engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(cls.engine)

    @classmethod
    def tearDownClass(cls):
        Base.metadata.drop_all(cls.engine)
        cls.engine.dispose()

    def setUp(self):
        self.session = Session(self.engine)
        self.user = User(email="user@example.com", password_hash="hash")
        self.session.add(self.user)
        self.session.commit()

    def tearDown(self):
        self.session.rollback()
        self.session.query(ChatMessage).delete()
        self.session.query(User).delete()
        self.session.commit()
        self.session.close()


class TestUser(BaseTestClass):

    def setUp(self):
        self.session = Session(self.engine)

    def tearDown(self):
        self.session.rollback()
        self.session.close()

    def test_create_user(self):
        user = User(
            email="new_user@example.com",
            password_hash="hashed_password",
            role="admin"
        )
        self.session.add(user)
        self.session.commit()

        self.assertIsNotNone(user.id)
        self.assertIsInstance(user.id, UUID)
        self.assertEqual("new_user@example.com", user.email)
        self.assertEqual("hashed_password", user.password_hash)
        self.assertEqual("admin", user.role)
        self.assertIsInstance(user.created_at, datetime)

    def test_email_unique_constraint(self):
        user1 = User(email="unique_email@example.com", password_hash="hash1")
        user2 = User(email="unique_email@example.com", password_hash="hash2")

        self.session.add(user1)
        self.session.commit()

        self.session.add(user2)
        with self.assertRaises(Exception):
            self.session.commit()

    def test_email_case_insensitive_uniqueness(self):
        user1 = User(email="UPPER_CASE_EMAIL@Example.com", password_hash="hash1")
        user2 = User(email="upper_case_email@example.com", password_hash="hash2")

        self.session.add(user1)
        self.session.commit()

        self.session.add(user2)
        with self.assertRaises(IntegrityError):
            self.session.commit()

    def test_find_user_by_email_case_insensitive(self):
        user = User(email="User@Example.com", password_hash="hash")
        self.session.add(user)
        self.session.commit()

        found: Optional[User] = self.session.query(User).filter(User.email.ilike("user@example.com")).first()
        self.assertEqual(user.id, found.id)


class TestChatMessage(BaseTestClass):

    def test_create_message(self):
        message = ChatMessage(
            user_id=self.user.id,
            role="user",
            content="Hello, world!"
        )
        self.session.add(message)
        self.session.commit()

        self.assertIsNotNone(message.id)
        self.assertIsInstance(message.id, UUID)
        self.assertEqual(self.user.id, message.user_id)
        self.assertEqual("user", message.role)
        self.assertEqual("Hello, world!", message.content)
        self.assertIsInstance(message.created_at, datetime)

    def test_message_requires_user(self):
        message = ChatMessage(
            user_id="non-existent-id",
            role="user",
            content="Test"
        )
        self.session.add(message)

        with self.assertRaises(Exception):
            self.session.commit()


class TestUserChatMessageRelationship(BaseTestClass):

    def test_user_messages_relationship(self):
        message1 = ChatMessage(user_id=self.user.id, role="user", content="Message 1")
        message2 = ChatMessage(user_id=self.user.id, role="assistant", content="Message 2")
        self.session.add_all([message1, message2])
        self.session.commit()

        self.assertEqual(2, len(self.user.chat_messages))
        self.assertEqual("Message 1", self.user.chat_messages[0].content)
        self.assertEqual("Message 2", self.user.chat_messages[1].content)

    def test_message_user_relationship(self):
        message = ChatMessage(user_id=self.user.id, role="user", content="Test")
        self.session.add(message)
        self.session.commit()

        self.assertEqual(self.user.id, message.user.id)
        self.assertEqual(self.user.email, message.user.email)

    def test_cascade_delete(self):
        message = ChatMessage(user_id=self.user.id, role="user", content="Test")
        self.user.chat_messages.append(message)
        self.session.commit()

        self.session.delete(self.user)
        self.session.commit()

        self.assertEqual(0, self.session.query(ChatMessage).count())

    def test_get_user_messages_ordered(self):
        msg1 = ChatMessage(user_id=self.user.id, role="user", content="First")
        self.session.add(msg1)
        self.session.commit()

        sleep(0.01)
        msg2 = ChatMessage(user_id=self.user.id, role="assistant", content="Second")
        self.session.add(msg2)
        self.session.commit()

        # noinspection PyTypeChecker
        messages: List[ChatMessage] = self.session.query(ChatMessage).filter(
            ChatMessage.user_id == self.user.id
        ).order_by(ChatMessage.created_at).all()

        self.assertEqual("First", messages[0].content)
        self.assertEqual("Second", messages[1].content)

    def test_bulk_message_creation(self):
        messages: List[ChatMessage] = [
            ChatMessage(user_id=self.user.id, role="user", content=f"Bulk Message {i}")
            for i in range(10)
        ]
        self.session.add_all(messages)
        self.session.commit()

        self.assertEqual(10, len(self.user.chat_messages))
        self.assertEqual(10, self.session.query(ChatMessage).count())
