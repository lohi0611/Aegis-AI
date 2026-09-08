"""
AEGIS — Unit Tests for User Authentication & Security
Tests PBKDF2 hashing, user registration, authentication validation, and demo seeding.
"""

from datetime import datetime

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from src.database.models import Base, User
from src.database.repository import (
    authenticate_user,
    hash_password,
    register_user,
    verify_password,
)


def make_test_engine():
    engine = create_engine(
        "sqlite:///:memory:", connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(bind=engine)
    return engine


def make_test_session(engine):
    return scoped_session(
        sessionmaker(bind=engine, autocommit=False, autoflush=False)
    )


class TestPasswordSecurity:
    def test_hash_and_verify_correct_password(self):
        """Valid password matches hash and salt."""
        pwd = "SecurePassword@123"
        pwd_hash, salt = hash_password(pwd)
        assert pwd_hash is not None
        assert salt is not None
        assert verify_password(pwd, pwd_hash, salt) is True

    def test_verify_incorrect_password(self):
        """Invalid password fails verification."""
        pwd_hash, salt = hash_password("CorrectPassword")
        assert verify_password("WrongPassword", pwd_hash, salt) is False


class TestUserModel:
    def setup_method(self):
        self.engine = make_test_engine()
        self.Session = make_test_session(self.engine)

    def teardown_method(self):
        self.Session.remove()
        self.engine.dispose()

    def test_create_user(self):
        db = self.Session()
        pwd_hash, salt = hash_password("TestPass@123")
        u = User(
            email="test@safety.org",
            full_name="Jane Doe",
            password_hash=pwd_hash,
            salt=salt,
            role="Safety Inspector",
            created_at=datetime.utcnow(),
        )
        db.add(u)
        db.commit()
        assert u.user_id is not None
        assert u.email == "test@safety.org"

        d = u.to_dict()
        assert d["email"] == "test@safety.org"
        assert d["full_name"] == "Jane Doe"
        assert d["role"] == "Safety Inspector"
        db.close()
