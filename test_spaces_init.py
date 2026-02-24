"""
Quick test to verify SpacesStorage can be initialized
Run this in production to see what's failing
"""
import os
import sys

print("=" * 80)
print("SPACES STORAGE INITIALIZATION TEST")
print("=" * 80)

# Check environment variables
print("\n1. Environment Variables:")
print(f"   SPACES_BUCKET: {os.environ.get('SPACES_BUCKET', 'NOT SET')}")
print(f"   SPACES_REGION: {os.environ.get('SPACES_REGION', 'NOT SET')}")
print(f"   SPACES_ACCESS_KEY: {'SET' if os.environ.get('SPACES_ACCESS_KEY') else 'NOT SET'}")
print(f"   SPACES_SECRET_KEY: {'SET' if os.environ.get('SPACES_SECRET_KEY') else 'NOT SET'}")
print(f"   SPACES_CDN_ENDPOINT: {os.environ.get('SPACES_CDN_ENDPOINT', 'NOT SET')}")

# Try importing boto3
print("\n2. Boto3 Import Test:")
try:
    import boto3
    print(f"   ✅ boto3 available (version {boto3.__version__})")
except ImportError as e:
    print(f"   ❌ boto3 NOT available: {e}")
    sys.exit(1)

# Try initializing SpacesStorage directly
print("\n3. SpacesStorage Initialization Test:")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

try:
    from backend.utils.storage import SpacesStorage
    
    storage = SpacesStorage(
        region=os.environ.get('SPACES_REGION'),
        bucket=os.environ.get('SPACES_BUCKET'),
        access_key=os.environ.get('SPACES_ACCESS_KEY'),
        secret_key=os.environ.get('SPACES_SECRET_KEY'),
        cdn_endpoint=os.environ.get('SPACES_CDN_ENDPOINT')
    )
    print(f"   ✅ SpacesStorage initialized successfully!")
    print(f"   ✅ Base URL: {storage.base_url}")
    print(f"   ✅ Bucket: {storage.bucket}")
    print(f"   ✅ Region: {storage.region}")
    
except Exception as e:
    print(f"   ❌ SpacesStorage initialization FAILED: {e}")
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
    
    if backend_type == 'SpacesStorage':
        print(f"   ✅ Using Spaces! Base URL: {backend.base_url}")
    else:
        print(f"   ❌ Using LocalStorage (should be Spaces!)")
        print(f"   Storage root: {backend.base_path if hasattr(backend, 'base_path') else 'N/A'}")
        
except Exception as e:
    print(f"   ❌ get_storage_backend() FAILED: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
