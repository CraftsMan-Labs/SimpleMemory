"""Test auth utilities."""
from __future__ import annotations

import uuid

import pytest

from kmg_shared.auth.api_keys import generate_api_key, hash_api_key, extract_api_key
from kmg_shared.auth.scoping import RequestScope, require_workspace_access, require_scope, require_tenant_match
from kmg_shared.errors import AuthenticationError, PermissionDeniedError


class TestApiKeys:
    def test_generate_returns_raw_and_info(self):
        raw, info = generate_api_key()
        assert raw.startswith("km_")
        assert len(info.prefix) == 12
        assert len(info.key_hash) == 64  # sha256 hex

    def test_hash_is_deterministic(self):
        raw, info = generate_api_key()
        assert hash_api_key(raw) == info.key_hash

    def test_extract_valid(self):
        raw, _ = generate_api_key()
        extracted = extract_api_key(f"Bearer {raw}")
        assert extracted == raw

    def test_extract_invalid_prefix(self):
        with pytest.raises(AuthenticationError):
            extract_api_key("Bearer invalid_key")

    def test_extract_no_bearer(self):
        with pytest.raises(AuthenticationError):
            extract_api_key("Token km_something")


class TestScoping:
    def _make_scope(self, **kwargs) -> RequestScope:
        defaults = {
            "tenant_id": uuid.uuid4(),
            "workspace_id": None,
            "user_id": uuid.uuid4(),
            "auth_type": "jwt",
            "scopes": ["read", "write"],
        }
        defaults.update(kwargs)
        return RequestScope(**defaults)

    def test_require_workspace_access_ok_when_unscoped(self):
        scope = self._make_scope(workspace_id=None)
        require_workspace_access(scope, uuid.uuid4())

    def test_require_workspace_access_ok_when_matching(self):
        wid = uuid.uuid4()
        scope = self._make_scope(workspace_id=wid)
        require_workspace_access(scope, wid)

    def test_require_workspace_access_denied_when_mismatched(self):
        scope = self._make_scope(workspace_id=uuid.uuid4())
        with pytest.raises(PermissionDeniedError):
            require_workspace_access(scope, uuid.uuid4())

    def test_require_scope_ok(self):
        scope = self._make_scope(scopes=["read", "write"])
        require_scope(scope, "read")

    def test_require_scope_admin_bypasses(self):
        scope = self._make_scope(scopes=["admin"])
        require_scope(scope, "write")

    def test_require_scope_denied(self):
        scope = self._make_scope(scopes=["read"])
        with pytest.raises(PermissionDeniedError):
            require_scope(scope, "write")

    def test_require_tenant_match_ok(self):
        tid = uuid.uuid4()
        scope = self._make_scope(tenant_id=tid)
        require_tenant_match(scope, tid)

    def test_require_tenant_match_denied(self):
        scope = self._make_scope()
        with pytest.raises(PermissionDeniedError):
            require_tenant_match(scope, uuid.uuid4())
