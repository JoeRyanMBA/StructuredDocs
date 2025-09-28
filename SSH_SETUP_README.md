# SSH Key Setup for StructuredDocs Deployments

## Overview

StructuredDocs now deploys to a DigitalOcean droplet (backend) and Vercel (frontend). When you need direct SSH access to the droplet—for example to upload `.env` files or inspect logs—use an SSH key instead of passwords. This guide walks through creating and reusing that key.

## Quick Setup

Run the helper script (it’s idempotent and safe to re-run):

```bash
./setup_ssh_keys.sh
```

Environment variables influence the script:

- `REMOTE_USER` (default `root`)
- `REMOTE_HOST` (e.g. `203.0.113.10`)
- `KEY_PATH` (defaults to `~/.ssh/structureddocs_deploy`)

Example:

```bash
REMOTE_HOST=203.0.113.10 REMOTE_USER=root ./setup_ssh_keys.sh
```

The script will:

1. Generate an ed25519 key if one doesn’t exist.
2. Offer to copy the public key to the server (via `ssh-copy-id` if available).
3. Add the key to your local `ssh-agent`.
4. Test an SSH connection using the configured host.

## Manual Setup (if you can’t run the script)

### 1. Generate a key pair

```bash
ssh-keygen -t ed25519 -f ~/.ssh/structureddocs_deploy -C "structureddocs-deployment"
```

### 2. Install the public key on the server

```bash
ssh-copy-id -i ~/.ssh/structureddocs_deploy.pub root@203.0.113.10
```

If `ssh-copy-id` isn’t available, copy the public key contents into `/root/.ssh/authorized_keys` (or the appropriate user directory).

### 3. (Optional) Add an SSH config entry

```sshconfig
Host structureddocs-do
    HostName 203.0.113.10
    User root
    IdentityFile ~/.ssh/structureddocs_deploy
    IdentitiesOnly yes
```

This lets you connect with `ssh structureddocs-do`.

### 4. Test the connection

```bash
ssh root@203.0.113.10 "echo 'SSH connection successful'"
```

## After Connecting

- Keep your `KEY_PATH` secure (permissions `600`).
- Rotate the key if your infrastructure changes (regenerate and update the server’s `authorized_keys`).
- Remove the key from the agent with `ssh-add -d <key>` if needed.

## Troubleshooting

- **Permission denied**: ensure the public key is present on the server and the SSH config references the correct `IdentityFile`.
- **Connection timeout**: verify the droplet’s firewall allows SSH (port 22) and the host/IP is correct.
- **Key generation errors**: make sure `~/.ssh` exists and has permissions `700`.

Once SSH works, use Ansible, rsync, or manual commands to manage the droplet. Frontend deployments should continue through Vercel; backend updates can be shipped via Docker/Compose or the DigitalOcean console as described in `README.md`.
