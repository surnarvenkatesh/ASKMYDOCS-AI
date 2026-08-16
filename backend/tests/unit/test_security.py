"""
Unit tests for app.core.security — no database, no network.
"""
import uuid
from datetime import timedelta

import pytest

from app.core.security import (
    TokenError,
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)


@pytest.mark.unit
class TestPasswordHashing:
    def test_hash_is_not_plaintext(self):
        hashed = hash_password("supersecret123")
        assert hashed != "supersecret123"

    def test_verify_correct_password(self):
        hashed = hash_password("supersecret123")
        assert verify_password("supersecret123", hashed) is True

    def test_verify_incorrect_password(self):
        hashed = hash_password("supersecret123")
        assert verify_password("wrongpassword", hashed) is False

    def test_same_password_produces_different_hashes(self):
        h1 = hash_password("supersecret123")
        h2 = hash_password("supersecret123")
        assert h1 != h2  # bcrypt salts each hash


@pytest.mark.unit
class TestTokens:
    def test_access_token_round_trip(self):
        user_id = uuid.uuid4()
        token = create_access_token(user_id)
        payload = decode_token(token, expected_type="access")
        assert payload["sub"] == str(user_id)
        assert payload["type"] == "access"

    def test_refresh_token_round_trip(self):
        user_id = uuid.uuid4()
        token = create_refresh_token(user_id)
        payload = decode_token(token, expected_type="refresh")
        assert payload["type"] == "refresh"

    def test_wrong_token_type_rejected(self):
        user_id = uuid.uuid4()
        access = create_access_token(user_id)
        with pytest.raises(TokenError):
            decode_token(access, expected_type="refresh")

    def test_garbage_token_rejected(self):
        with pytest.raises(TokenError):
            decode_token("not-a-real-token", expected_type="access")

    def test_expired_token_rejected(self, monkeypatch):
        from app.core import security

        # Force an already-expired token by monkeypatching the expiry window.
        monkeypatch.setattr(security.settings, "ACCESS_TOKEN_EXPIRE_MINUTES", -1)
        token = create_access_token(uuid.uuid4())
        with pytest.raises(TokenError):
            decode_token(token, expected_type="access")
