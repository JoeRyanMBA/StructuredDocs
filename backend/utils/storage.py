"""
Storage abstraction layer supporting local filesystem and S3-compatible object storage.
"""
import os
from pathlib import Path
from typing import Optional


def resolve_local_storage_root() -> str:
    """Return the writable local image root for this environment.

    In local development or non-container runs, IMAGE_STORAGE_ROOT is often unset.
    We prefer a repo-local writable directory instead of the container-only
    /app/... paths that may not exist or be writable in this environment.
    """
    configured_root = (os.environ.get('IMAGE_STORAGE_ROOT') or '').strip()
    if configured_root:
        candidate = Path(configured_root)
        try:
            candidate.mkdir(parents=True, exist_ok=True)
            test_file = candidate / '.write_test'
            test_file.write_text('ok')
            test_file.unlink()
            return str(candidate)
        except Exception:
            pass

    candidates = [
        Path('/app/data/images'),
        Path('/app/backend/static/images'),
        Path(__file__).resolve().parents[1] / 'data' / 'images',
        Path(__file__).resolve().parents[1] / 'backend' / 'static' / 'images',
        Path.cwd() / 'data' / 'images',
        Path.cwd() / 'backend' / 'static' / 'images',
    ]

    for candidate in candidates:
        try:
            candidate.mkdir(parents=True, exist_ok=True)
            test_file = candidate / '.write_test'
            test_file.write_text('ok')
            test_file.unlink()
            return str(candidate)
        except Exception:
            continue

    fallback = Path(__file__).resolve().parents[1] / 'data' / 'images'
    fallback.mkdir(parents=True, exist_ok=True)
    return str(fallback)


class StorageBackend:
    """Abstract base for storage backends"""
    
    def save_file(self, file_data: bytes, path: str, content_type: Optional[str] = None) -> str:
        """Save file and return public URL"""
        raise NotImplementedError
    
    def read_file(self, path: str) -> bytes:
        """Read file contents"""
        raise NotImplementedError
    
    def delete_file(self, path: str) -> bool:
        """Delete file"""
        raise NotImplementedError
    
    def file_exists(self, path: str) -> bool:
        """Check if file exists"""
        raise NotImplementedError
    
    def get_url(self, path: str) -> str:
        """Get public URL for file"""
        raise NotImplementedError


class LocalStorage(StorageBackend):
    """Local filesystem storage"""
    
    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self.storage_root = str(self.base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
    
    def save_file(self, file_data: bytes, path: str, content_type: Optional[str] = None) -> str:
        file_path = self.base_path / path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_bytes(file_data)
        return f"/{path}"
    
    def read_file(self, path: str) -> bytes:
        file_path = self.base_path / path
        return file_path.read_bytes()
    
    def delete_file(self, path: str) -> bool:
        try:
            file_path = self.base_path / path
            file_path.unlink()
            return True
        except:
            return False
    
    def file_exists(self, path: str) -> bool:
        return (self.base_path / path).exists()
    
    def get_url(self, path: str) -> str:
        return f"/{path}"


class S3CompatibleStorage(StorageBackend):
    """S3-compatible object storage."""
    
    def __init__(
        self,
        bucket: str,
        access_key: str,
        secret_key: str,
        endpoint_url: str,
        region: Optional[str] = None,
        public_base_url: Optional[str] = None,
        key_prefix: Optional[str] = None,
    ):
        try:
            import boto3
            from botocore.exceptions import ClientError
            self.ClientError = ClientError
        except ImportError:
            raise ImportError("boto3 is required for object storage. Install with: pip install boto3")
        
        self.bucket = bucket
        self.region = region
        self.endpoint_url = endpoint_url.rstrip('/')
        self.public_base_url = public_base_url.rstrip('/') if public_base_url else None
        # Normalise prefix: strip leading slash, ensure trailing slash if non-empty
        if key_prefix:
            self.key_prefix = key_prefix.strip('/') + '/'
        else:
            self.key_prefix = ''
        
        # Initialize an S3-compatible client.
        self.s3_client = boto3.client(
            's3',
            region_name=region,
            endpoint_url=self.endpoint_url,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key
        )
        
        # Base URL for files
        if self.public_base_url:
            self.base_url = self.public_base_url
        else:
            self.base_url = f'{self.endpoint_url}/{bucket}'
    
    def _key(self, path: str) -> str:
        """Prepend environment prefix to a storage key."""
        return f"{self.key_prefix}{path.lstrip('/')}"

    def save_file(self, file_data: bytes, path: str, content_type: Optional[str] = None) -> str:
        """Upload file to object storage."""
        extra_args = {}
        if content_type:
            extra_args['ContentType'] = content_type
        extra_args['ACL'] = 'public-read'

        key = self._key(path)
        self.s3_client.put_object(
            Bucket=self.bucket,
            Key=key,
            Body=file_data,
            **extra_args
        )

        return f"{self.base_url}/{key}"

    def read_file(self, path: str) -> bytes:
        """Download file from object storage."""
        response = self.s3_client.get_object(Bucket=self.bucket, Key=self._key(path))
        return response['Body'].read()

    def delete_file(self, path: str) -> bool:
        """Delete file from object storage."""
        try:
            self.s3_client.delete_object(Bucket=self.bucket, Key=self._key(path))
            return True
        except self.ClientError:
            return False

    def file_exists(self, path: str) -> bool:
        """Check if file exists in object storage."""
        try:
            self.s3_client.head_object(Bucket=self.bucket, Key=self._key(path))
            return True
        except self.ClientError:
            return False

    def get_url(self, path: str) -> str:
        """Get public URL for file"""
        return f"{self.base_url}/{self._key(path)}"


def get_storage_backend() -> StorageBackend:
    """
    Factory function to get configured storage backend.
    Checks environment variables to determine which backend to use.
    Falls back gracefully if boto3 is not available.
    """
    # Allow explicit backend pinning so production can force local VPS storage.
    backend_mode = (os.environ.get('STORAGE_BACKEND') or '').strip().lower()
    import logging
    logger = logging.getLogger(__name__)

    storage_root = resolve_local_storage_root()
    if backend_mode in {'local', 'filesystem', 'vps'}:
        logger.info(f"✅ STORAGE_BACKEND={backend_mode}; using LocalStorage at {storage_root}")
        return LocalStorage(storage_root)

    storage_bucket = os.environ.get('STORAGE_BUCKET')
    storage_region = os.environ.get('STORAGE_REGION')
    storage_access_key = os.environ.get('STORAGE_ACCESS_KEY')
    storage_secret_key = os.environ.get('STORAGE_SECRET_KEY')
    storage_endpoint = os.environ.get('STORAGE_ENDPOINT')
    storage_public_base_url = os.environ.get('STORAGE_PUBLIC_BASE_URL')
    storage_key_prefix = os.environ.get('STORAGE_KEY_PREFIX', '')
    
    if all([storage_bucket, storage_access_key, storage_secret_key, storage_endpoint]):
        logger.info(
            "🔧 Attempting to initialize object storage: "
            f"bucket={storage_bucket}, endpoint={storage_endpoint}, region={storage_region or 'default'}"
        )
        
        try:
            storage = S3CompatibleStorage(
                bucket=storage_bucket,
                access_key=storage_access_key,
                secret_key=storage_secret_key,
                endpoint_url=storage_endpoint,
                region=storage_region,
                public_base_url=storage_public_base_url,
                key_prefix=storage_key_prefix
            )
            logger.info(f"✅ S3CompatibleStorage initialized successfully! Base URL: {storage.base_url}")
            return storage
        except ImportError as ie:
            # boto3 not installed, fall back to local
            logger.warning(f"⚠️ boto3 not available for object storage: {ie}. Falling back to local storage.")
        except Exception as e:
            logger.error(f"❌ Failed to initialize object storage: {e}. Falling back to local storage.", exc_info=True)
    
    # Fall back to local storage
    logger.warning(f"⚠️ Using LocalStorage fallback: {storage_root} (object storage not configured or failed to initialize)")
    return LocalStorage(storage_root)
