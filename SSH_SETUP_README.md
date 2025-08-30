# SSH Key Setup for PythonAnywhere Deployment

## Overview
This document explains how to set up and maintain SSH key authentication for passwordless deployment to PythonAnywhere.

## Current SSH Keys
Your workspace already has SSH keys configured:
- **Private key**: `~/.ssh/pythonanywhere_key`
- **Public key**: `~/.ssh/pythonanywhere_key.pub`
- **SSH Config**: `~/.ssh/config` (contains host configuration)

## Quick Setup (Run at start of each AI session)
```bash
./setup_ssh_keys.sh
```

This script will:
1. ✅ Check if SSH keys exist
2. 🔐 Add keys to SSH agent
3. 🧪 Test connection to PythonAnywhere
4. 🎉 Confirm setup is working

## Manual Setup Steps
If you need to set up SSH keys from scratch:

### 1. Generate SSH Key Pair
```bash
ssh-keygen -t ed25519 -f ~/.ssh/pythonanywhere_key -C "pythonanywhere-deployment"
```

### 2. Copy Public Key to PythonAnywhere
```bash
ssh-copy-id -i ~/.ssh/pythonanywhere_key.pub JoeRyanMBA@ssh.pythonanywhere.com
```

### 3. Configure SSH Client
Add to `~/.ssh/config`:
```
Host pythonanywhere
    HostName ssh.pythonanywhere.com
    User JoeRyanMBA
    IdentityFile ~/home/JoeRyanMBA/.ssh/pythonanywhere_key
    IdentitiesOnly yes
```

### 4. Test Connection
```bash
ssh pythonanywhere "echo 'SSH connection successful'"
```

## Deployment Scripts
Once SSH is set up, you can run:
```bash
./deploy_fixes.sh     # Deploy backend files
./upload_frontend.sh  # Deploy frontend files
```

## Troubleshooting
- **Permission denied**: Run `./setup_ssh_keys.sh` to re-add keys to agent
- **Connection timeout**: Check internet connection and PythonAnywhere status
- **Keys not found**: Re-run the key generation steps above

## For AI Chat Sessions
At the start of each new AI chat session, simply run:
```bash
./setup_ssh_keys.sh
```

This will restore SSH authentication without needing to remember all the setup steps.
