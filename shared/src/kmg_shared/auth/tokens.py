from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime, timezone

import jwt

from kmg_shared.config import settings
from kmg_shared.errors import AuthenticationError


@dataclass
class TokenPayload:
    user_id: uuid.UUID
    tenant_id: uuid.UUID
    email: str
    exp: datetime


def decode_token(token: str) -> TokenPayload:
    """Decode and validate a JWT token."""
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm],
        )
    except jwt.ExpiredSignatureError as e:
        raise AuthenticationError("Token has expired") from e
    except jwt.InvalidTokenError as e:
        raise AuthenticationError(f"Invalid token: {e}") from e

    return TokenPayload(
        user_id=uuid.UUID(payload["sub"]),
        tenant_id=uuid.UUID(payload["tenant_id"]),
        email=payload.get("email", ""),
        exp=datetime.fromtimestamp(payload["exp"], tz=timezone.utc),
    )


def create_token(user_id: uuid.UUID, tenant_id: uuid.UUID, email: str) -> str:
    """Create a JWT token (for testing / internal use)."""
    now = datetime.now(tz=timezone.utc)
    payload = {
        "sub": str(user_id),
        "tenant_id": str(tenant_id),
        "email": email,
        "iat": int(now.timestamp()),
        "exp": int(now.timestamp()) + settings.jwt_expiry_minutes * 60,
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)
