from __future__ import annotations

from pathlib import Path


class LocalObjectStorage:
    """ObjectStorage implementation using the local filesystem (dev/test only)."""

    def __init__(self, base_path: Path) -> None:
        self._base_path = base_path
        self._base_path.mkdir(parents=True, exist_ok=True)

    async def put(self, key: str, data: bytes, content_type: str = "application/octet-stream") -> None:
        target = self._base_path / key
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)

    async def get(self, key: str) -> bytes:
        target = self._base_path / key
        return target.read_bytes()

    async def delete(self, key: str) -> None:
        target = self._base_path / key
        target.unlink(missing_ok=True)

    async def exists(self, key: str) -> bool:
        return (self._base_path / key).exists()

    async def presigned_url(self, key: str, expires_in: int = 3600) -> str:
        return f"file://{self._base_path / key}"
