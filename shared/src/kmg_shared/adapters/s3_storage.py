from __future__ import annotations

import asyncio
import functools

import boto3
from botocore.config import Config as BotoConfig
from botocore.exceptions import ClientError

from kmg_shared.resilience import retry_transient


class S3ObjectStorage:
    """ObjectStorage implementation backed by S3-compatible storage (AWS S3, R2, MinIO)."""

    def __init__(
        self,
        bucket: str,
        endpoint_url: str,
        access_key: str,
        secret_key: str,
        region: str = "us-east-1",
    ) -> None:
        self._bucket = bucket
        self._client = boto3.client(
            "s3",
            endpoint_url=endpoint_url,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region,
            config=BotoConfig(
                connect_timeout=10,
                read_timeout=30,
                retries={"max_attempts": 0},
            ),
        )

    async def _run(self, func, *args, **kwargs):
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, functools.partial(func, *args, **kwargs))

    @retry_transient
    async def put(self, key: str, data: bytes, content_type: str = "application/octet-stream") -> None:
        await self._run(
            self._client.put_object,
            Bucket=self._bucket,
            Key=key,
            Body=data,
            ContentType=content_type,
        )

    @retry_transient
    async def get(self, key: str) -> bytes:
        response = await self._run(self._client.get_object, Bucket=self._bucket, Key=key)
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, response["Body"].read)

    async def delete(self, key: str) -> None:
        await self._run(self._client.delete_object, Bucket=self._bucket, Key=key)

    @retry_transient
    async def exists(self, key: str) -> bool:
        try:
            await self._run(self._client.head_object, Bucket=self._bucket, Key=key)
            return True
        except ClientError as e:
            if e.response["Error"]["Code"] == "404":
                return False
            raise

    @retry_transient
    async def presigned_url(self, key: str, expires_in: int = 3600) -> str:
        url: str = await self._run(
            self._client.generate_presigned_url,
            ClientMethod="put_object",
            Params={"Bucket": self._bucket, "Key": key},
            ExpiresIn=expires_in,
        )
        return url
