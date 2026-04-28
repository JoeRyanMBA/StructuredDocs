"""
Quick test to verify S3CompatibleStorage can be initialized.
Run this in production to see what's failing.
"""
import os
import sys

print("=" * 80)
print("OBJECT STORAGE INITIALIZATION TEST")
print("=" * 80)

# Check environment variables
print("\n1. Environment Variables:")
print(f"   STORAGE_BUCKET: {os.environ.get('STORAGE_BUCKET', 'NOT SET')}")
print(f"   STORAGE_REGION: {os.environ.get('STORAGE_REGION', 'NOT SET')}")
print(f"   STORAGE_ACCESS_KEY: {'SET' if os.environ.get('STORAGE_ACCESS_KEY') else 'NOT SET'}")
print(f"   STORAGE_SECRET_KEY: {'SET' if os.environ.get('STORAGE_SECRET_KEY') else 'NOT SET'}")
print(f"   STORAGE_ENDPOINT: {os.environ.get('STORAGE_ENDPOINT', 'NOT SET')}")
print(f"   STORAGE_PUBLIC_BASE_URL: {os.environ.get('STORAGE_PUBLIC_BASE_URL', 'NOT SET')}")

# Try importing boto3
print("\n2. Boto3 Import Test:")
try:
    import boto3
    print(f"   ✅ boto3 available (version {boto3.__version__})")
except ImportError as e:
    print(f"   ❌ boto3 NOT available: {e}")
    sys.exit(1)

# Try initializing S3CompatibleStorage directly
print("\n3. S3CompatibleStorage Initialization Test:")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

try:
    from backend.utils.storage import S3CompatibleStorage
    
    storage = S3CompatibleStorage(
        region=os.environ.get('STORAGE_REGION'),
        bucket=os.environ.get('STORAGE_BUCKET'),
        access_key=os.environ.get('STORAGE_ACCESS_KEY'),
        secret_key=os.environ.get('STORAGE_SECRET_KEY'),
        endpoint_url=os.environ.get('STORAGE_ENDPOINT'),
        public_base_url=os.environ.get('STORAGE_PUBLIC_BASE_URL')
    )
    print(f"   ✅ S3CompatibleStorage initialized successfully!")
    print(f"   ✅ Base URL: {storage.base_url}")
    print(f"   ✅ Bucket: {storage.bucket}")
    print(f"   ✅ Region: {storage.region}")
    
except Exception as e:
    print(f"   ❌ S3CompatibleStorage initialization FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Try get_storage_backend
print("\n4. get_storage_backend() Test:")
try:
    from backend.utils.storage import get_storage_backend
    
    backend = get_storage_backend()
    backend_type = type(backend).__name__
    print(f"   Backend type: {backend_type}")
    
    if backend_type == 'S3CompatibleStorage':
        print(f"   ✅ Using remote object storage! Base URL: {backend.base_url}")
    else:
        print(f"   ❌ Using LocalStorage (should be remote object storage!)")
        print(f"   Storage root: {backend.base_path if hasattr(backend, 'base_path') else 'N/A'}")
        
except Exception as e:
    print(f"   ❌ get_storage_backend() FAILED: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
