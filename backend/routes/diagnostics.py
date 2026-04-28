"""
Diagnostics endpoint for troubleshooting storage and environment issues
"""
import os
from flask import Blueprint, jsonify
from backend.utils.storage import get_storage_backend

diagnostics_bp = Blueprint('diagnostics', __name__)


@diagnostics_bp.route('/diagnostics/storage', methods=['GET'])
def check_storage():
    """Check storage backend configuration"""
    
    # Check environment variables
    env_vars = {
        'STORAGE_BUCKET': os.environ.get('STORAGE_BUCKET', 'NOT SET'),
        'STORAGE_REGION': os.environ.get('STORAGE_REGION', 'NOT SET'),
        'STORAGE_ACCESS_KEY': '***' if os.environ.get('STORAGE_ACCESS_KEY') else 'NOT SET',
        'STORAGE_SECRET_KEY': '***' if os.environ.get('STORAGE_SECRET_KEY') else 'NOT SET',
        'STORAGE_ENDPOINT': os.environ.get('STORAGE_ENDPOINT', 'NOT SET'),
        'STORAGE_PUBLIC_BASE_URL': os.environ.get('STORAGE_PUBLIC_BASE_URL', 'NOT SET'),
        'IMAGE_STORAGE_ROOT': os.environ.get('IMAGE_STORAGE_ROOT', 'NOT SET'),
    }
    
    # Check which storage backend is active
    try:
        storage = get_storage_backend()
        storage_type = type(storage).__name__
        storage_details = {}
        
        if storage_type == 'S3CompatibleStorage':
            storage_details = {
                'type': 'S3-compatible object storage',
                'bucket': storage.bucket,
                'region': storage.region,
                'endpoint_url': storage.endpoint_url,
                'base_url': storage.base_url,
                'public_base_url': storage.public_base_url if storage.public_base_url else 'Not configured (using endpoint-derived URL)'
            }
        elif storage_type == 'LocalStorage':
            storage_details = {
                'type': 'Local Filesystem',
                'storage_root': storage.storage_root,
                'is_ephemeral': 'likely YES (container storage)' if '/app/' in storage.storage_root else 'possibly NO'
            }
        else:
            storage_details = {'type': 'Unknown', 'class': storage_type}
            
    except Exception as e:
        storage_type = 'ERROR'
        storage_details = {'error': str(e)}
    
    # Check boto3 availability
    try:
        import boto3
        boto3_available = True
        boto3_version = boto3.__version__
    except ImportError:
        boto3_available = False
        boto3_version = 'Not installed'
    
    # Check pandoc
    import subprocess
    try:
        result = subprocess.run(['pandoc', '--version'], capture_output=True, text=True, timeout=5)
        pandoc_available = result.returncode == 0
        pandoc_version = result.stdout.split('\n')[0] if pandoc_available else 'Error'
    except FileNotFoundError:
        pandoc_available = False
        pandoc_version = 'Not found in PATH'
    except Exception as e:
        pandoc_available = False
        pandoc_version = f'Error: {str(e)}'
    
    return jsonify({
        'storage_backend': {
            'active_type': storage_type,
            'details': storage_details
        },
        'environment_variables': env_vars,
        'dependencies': {
            'boto3': {
                'available': boto3_available,
                'version': boto3_version
            },
            'pandoc': {
                'available': pandoc_available,
                'version': pandoc_version
            }
        },
        'recommendations': _get_recommendations(env_vars, storage_type, boto3_available)
    })


def _get_recommendations(env_vars, storage_type, boto3_available):
    """Generate recommendations based on current configuration"""
    recommendations = []
    
    # Check if using local storage when remote object storage should be used.
    if storage_type == 'LocalStorage':
        if env_vars['STORAGE_BUCKET'] == 'NOT SET':
            recommendations.append({
                'severity': 'HIGH',
                'issue': 'Using ephemeral local storage - images will be lost on redeployment',
                'solution': 'Either mount persistent VPS storage or configure remote object storage with STORAGE_* environment variables'
            })
        if not boto3_available:
            recommendations.append({
                'severity': 'HIGH',
                'issue': 'boto3 not installed - cannot use remote object storage',
                'solution': 'Ensure boto3>=1.34.0 is in requirements.txt and redeploy'
            })
    
    # Check if required object storage vars are only partially configured.
    storage_vars = [
        env_vars['STORAGE_BUCKET'],
        env_vars['STORAGE_ACCESS_KEY'],
        env_vars['STORAGE_SECRET_KEY'],
        env_vars['STORAGE_ENDPOINT'],
    ]
    storage_set_count = sum(1 for v in storage_vars if v != 'NOT SET')
    if 0 < storage_set_count < 4:
        recommendations.append({
            'severity': 'HIGH',
            'issue': f'Only {storage_set_count}/4 required object storage variables configured - storage will fall back to local',
            'solution': 'Set STORAGE_BUCKET, STORAGE_ACCESS_KEY, STORAGE_SECRET_KEY, and STORAGE_ENDPOINT'
        })
    
    # Check if IMAGE_STORAGE_ROOT is set when using object storage.
    if storage_type == 'S3CompatibleStorage' and env_vars['IMAGE_STORAGE_ROOT'] != 'NOT SET':
        recommendations.append({
            'severity': 'MEDIUM',
            'issue': 'IMAGE_STORAGE_ROOT is set but not used with remote object storage',
            'solution': 'Remove IMAGE_STORAGE_ROOT if you do not need local filesystem storage'
        })
    
    if not recommendations:
        recommendations.append({
            'severity': 'INFO',
            'issue': 'Configuration looks good!',
            'solution': 'No issues detected'
        })
    
    return recommendations
