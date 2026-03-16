"""
Storage abstraction layer supporting both local filesystem and Digital Ocean Spaces
"""
import os
from pathlib import Path
from typing import Optional, BinaryIO
import io

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


class SpacesStorage(StorageBackend):
    """Digital Ocean Spaces storage (S3-compatible)"""
    
    def __init__(self, region: str, bucket: str, access_key: str, secret_key: str,
                 cdn_endpoint: Optional[str] = None, key_prefix: Optional[str] = None):
        try:
            import boto3
            from botocore.exceptions import ClientError
            self.ClientError = ClientError
        except ImportError:
            raise ImportError("boto3 is required for Spaces storage. Install with: pip install boto3")
        
        self.region = region
        self.bucket = bucket
        self.cdn_endpoint = cdn_endpoint
        # Normalise prefix: strip leading slash, ensure trailing slash if non-empty
        if key_prefix:
            self.key_prefix = key_prefix.strip('/') + '/'
        else:
            self.key_prefix = ''
        
        # Initialize S3 client for DO Spaces
        self.s3_client = boto3.client(
            's3',
            region_name=region,
            endpoint_url=f'https://{region}.digitaloceanspaces.com',
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key
        )
        
        # Base URL for files
        if cdn_endpoint:
            self.base_url = cdn_endpoint.rstrip('/')
        else:
            self.base_url = f'https://{bucket}.{region}.digitaloceanspaces.com'
    
    def _key(self, path: str) -> str:
        """Prepend environment prefix to a storage key."""
        return f"{self.key_prefix}{path.lstrip('/')}"

    def save_file(self, file_data: bytes, path: str, content_type: Optional[str] = None) -> str:
        """Upload file to Spaces"""
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
        """Download file from Spaces"""
        response = self.s3_client.get_object(Bucket=self.bucket, Key=self._key(path))
        return response['Body'].read()

    def delete_file(self, path: str) -> bool:
        """Delete file from Spaces"""
        try:
            self.s3_client.delete_object(Bucket=self.bucket, Key=self._key(path))
            return True
        except self.ClientError:
            return False

    def file_exists(self, path: str) -> bool:
        """Check if file exists in Spaces"""
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
    # Check if Spaces is configured
    spaces_bucket = os.environ.get('SPACES_BUCKET')
    spaces_region = os.environ.get('SPACES_REGION')
    spaces_access_key = os.environ.get('SPACES_ACCESS_KEY')
    spaces_secret_key = os.environ.get('SPACES_SECRET_KEY')
    
    if all([spaces_bucket, spaces_region, spaces_access_key, spaces_secret_key]):
        # Try to use Spaces
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"🔧 Attempting to initialize Spaces storage: bucket={spaces_bucket}, region={spaces_region}")
        
        try:
            cdn_endpoint = os.environ.get('SPACES_CDN_ENDPOINT')
            key_prefix = os.environ.get('SPACES_KEY_PREFIX', '')
            storage = SpacesStorage(
                region=spaces_region,
                bucket=spaces_bucket,
                access_key=spaces_access_key,
                secret_key=spaces_secret_key,
                cdn_endpoint=cdn_endpoint,
                key_prefix=key_prefix
            )
            logger.info(f"✅ SpacesStorage initialized successfully! Base URL: {storage.base_url}")
            return storage
        except ImportError as ie:
            # boto3 not installed, fall back to local
            logger.warning(f"⚠️ boto3 not available for Spaces storage: {ie}. Falling back to local storage.")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Spaces storage: {e}. Falling back to local storage.", exc_info=True)
    
    # Fall back to local storage
    import logging
    logger = logging.getLogger(__name__)
    storage_root = os.environ.get('IMAGE_STORAGE_ROOT', '/app/backend/static/images')
    logger.warning(f"⚠️ Using LocalStorage fallback: {storage_root} (Spaces not configured or failed to initialize)")
    return LocalStorage(storage_root)
