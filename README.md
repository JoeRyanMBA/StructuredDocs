# StructuredDocs

## Quick Start

### SSH Setup for Deployment
Before deploying to PythonAnywhere, set up SSH keys:
```bash
./setup_ssh_keys.sh
```

This configures passwordless SSH authentication for deployment scripts.

📖 **Detailed SSH Setup**: See [SSH_SETUP_README.md](SSH_SETUP_README.md) for complete instructions.

### Deployment
```bash
./deploy_fixes.sh     # Deploy backend changes
./upload_frontend.sh  # Deploy frontend changes
```

