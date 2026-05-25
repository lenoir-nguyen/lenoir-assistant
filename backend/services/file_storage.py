"""
File storage abstraction layer supporting local disk and AWS S3.

This allows easy switching between local development (local disk) and
production (AWS S3) without changing document processor code.
"""

from abc import ABC, abstractmethod
import os
from pathlib import Path
import asyncio
from config import get_settings

settings = get_settings()


class FileStorageBase(ABC):
    """Abstract base class for file storage implementations."""

    @abstractmethod
    async def upload(self, file_bytes: bytes, storage_path: str) -> str:
        """
        Upload file to storage.

        Args:
            file_bytes: Raw file content
            storage_path: Where to store (e.g., "documents/uuid/filename.pdf")

        Returns:
            Storage location/key for later retrieval
        """
        pass

    @abstractmethod
    async def download(self, storage_path: str) -> bytes:
        """
        Download file from storage.

        Args:
            storage_path: Location returned by upload()

        Returns:
            Raw file content
        """
        pass

    @abstractmethod
    async def delete(self, storage_path: str) -> bool:
        """
        Delete file from storage.

        Args:
            storage_path: Location returned by upload()

        Returns:
            True if deleted, False if not found
        """
        pass


class LocalFileStorage(FileStorageBase):
    """Store files on local disk (development)."""

    def __init__(self, upload_dir: str = None):
        """
        Initialize local file storage.

        Args:
            upload_dir: Directory to store files (default: from config)
        """
        self.upload_dir = upload_dir or settings.DOCUMENT_UPLOAD_DIR
        Path(self.upload_dir).mkdir(parents=True, exist_ok=True)

    async def upload(self, file_bytes: bytes, storage_path: str) -> str:
        """Upload file to local disk."""
        full_path = os.path.join(self.upload_dir, storage_path)

        # Create parent directories
        Path(full_path).parent.mkdir(parents=True, exist_ok=True)

        # Write file asynchronously (using executor to avoid blocking)
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None,
            lambda: open(full_path, 'wb').write(file_bytes)
        )

        return storage_path

    async def download(self, storage_path: str) -> bytes:
        """Download file from local disk."""
        full_path = os.path.join(self.upload_dir, storage_path)

        if not os.path.exists(full_path):
            raise FileNotFoundError(f"File not found: {storage_path}")

        # Read file asynchronously
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            lambda: open(full_path, 'rb').read()
        )

    async def delete(self, storage_path: str) -> bool:
        """Delete file from local disk."""
        full_path = os.path.join(self.upload_dir, storage_path)

        if not os.path.exists(full_path):
            return False

        # Delete file asynchronously
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None,
            lambda: os.remove(full_path)
        )

        return True


class S3FileStorage(FileStorageBase):
    """Store files on AWS S3 (production)."""

    def __init__(
        self,
        bucket: str = None,
        access_key: str = None,
        secret_key: str = None,
        region: str = None
    ):
        """
        Initialize S3 file storage.

        Args:
            bucket: S3 bucket name (default: from config)
            access_key: AWS access key (default: from config)
            secret_key: AWS secret key (default: from config)
            region: AWS region (default: from config)
        """
        self.bucket = bucket or settings.AWS_S3_BUCKET
        self.access_key = access_key or settings.AWS_ACCESS_KEY_ID
        self.secret_key = secret_key or settings.AWS_SECRET_ACCESS_KEY
        self.region = region or settings.AWS_S3_REGION

        # Lazy import boto3 (only needed if using S3)
        try:
            import boto3
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=self.access_key,
                aws_secret_access_key=self.secret_key,
                region_name=self.region
            )
        except ImportError:
            raise ImportError("boto3 required for S3 storage. Install with: pip install boto3")

    async def upload(self, file_bytes: bytes, storage_path: str) -> str:
        """Upload file to S3."""
        loop = asyncio.get_event_loop()

        await loop.run_in_executor(
            None,
            lambda: self.s3_client.put_object(
                Bucket=self.bucket,
                Key=storage_path,
                Body=file_bytes
            )
        )

        return storage_path

    async def download(self, storage_path: str) -> bytes:
        """Download file from S3."""
        loop = asyncio.get_event_loop()

        try:
            response = await loop.run_in_executor(
                None,
                lambda: self.s3_client.get_object(
                    Bucket=self.bucket,
                    Key=storage_path
                )
            )
            return response['Body'].read()
        except self.s3_client.exceptions.NoSuchKey:
            raise FileNotFoundError(f"File not found in S3: {storage_path}")

    async def delete(self, storage_path: str) -> bool:
        """Delete file from S3."""
        loop = asyncio.get_event_loop()

        try:
            await loop.run_in_executor(
                None,
                lambda: self.s3_client.delete_object(
                    Bucket=self.bucket,
                    Key=storage_path
                )
            )
            return True
        except Exception:
            return False


def get_file_storage() -> FileStorageBase:
    """
    Factory function to get appropriate file storage implementation.

    Returns:
        FileStorageBase: LocalFileStorage or S3FileStorage based on config
    """
    storage_type = settings.STORAGE_TYPE.lower()

    if storage_type == 's3':
        return S3FileStorage()
    else:
        # Default to local storage
        return LocalFileStorage()
