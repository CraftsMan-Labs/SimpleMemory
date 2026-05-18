from __future__ import annotations

import hashlib
import secrets
from dataclasses import dataclass

from kmg_shared.errors import AuthenticationError


API_KEY_PREFIX = "km_"
API_KEY_LENGTH = 48


@dataclass
class ApiKeyInfo:
    prefix: str
    key_hash: str


def generate_api_key() -> tuple[str, ApiKeyInfo]:
    """Generate a new API key and return (raw_key, info_for_storage)."""
    raw = API_KEY_PREFIX + secrets.token_urlsafe(API_KEY_LENGTH)
    prefix = raw[:12]
    key_hash = hashlib.sha256(raw.encode()).hexdigest()
    return raw, ApiKeyInfo(prefix=prefix, key_hash=key_hash)


def hash_api_key(raw_key: str) -> str:
    """Hash a raw API key for lookup."""
    return hashlib.sha256(raw_key.encode()).hexdigest()


def extract_api_key(authorization: str) -> str:
    """Extract API key from Authorization header."""
    if not authorization.startswith("Bearer "):
        raise AuthenticationError("Invalid authorization header format")
    key = authorization[7:].strip()
    if not key.startswith(API_KEY_PREFIX):
        raise AuthenticationError("Invalid API key format")
    return key
