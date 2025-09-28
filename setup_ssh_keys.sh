#!/bin/bash
# SSH key helper for StructuredDocs deployments.

set -euo pipefail

REMOTE_USER="${REMOTE_USER:-root}"
REMOTE_HOST="${REMOTE_HOST:-your.server.example.com}"
KEY_PATH="${KEY_PATH:-$HOME/.ssh/structureddocs_deploy}"
PUB_PATH="$KEY_PATH.pub"

echo "🔑 Preparing SSH key at $KEY_PATH for ${REMOTE_USER}@${REMOTE_HOST}"

# Create .ssh dir
mkdir -p "$HOME/.ssh"
chmod 700 "$HOME/.ssh"

if [ ! -f "$KEY_PATH" ]; then
    echo "🔐 Generating ed25519 key at $KEY_PATH"
    ssh-keygen -t ed25519 -f "$KEY_PATH" -C "structureddocs-deployment" -N "" || {
        echo "❌ Failed to generate SSH key. Exiting."; exit 1
    }
    chmod 600 "$KEY_PATH"
    chmod 644 "$PUB_PATH"
    echo "✅ Key generated. Upload the public key to your remote host."
fi

# Try to copy the public key automatically if ssh-copy-id is available
if command -v ssh-copy-id >/dev/null 2>&1; then
    echo "📤 Copying public key with ssh-copy-id..."
    ssh-copy-id -i "$PUB_PATH" "${REMOTE_USER}@${REMOTE_HOST}" || true
else
    echo "📤 ssh-copy-id not available. Copy the public key below to your server (e.g. append to ~/.ssh/authorized_keys):"
    echo "------- BEGIN KEY -------"
    cat "$PUB_PATH"
    echo "-------- END KEY --------"
fi

# Add key to agent
if ! ssh-add -l | grep -q "$(basename "$KEY_PATH")" 2>/dev/null; then
    echo "🔐 Adding SSH key to ssh-agent..."
    # Start ssh-agent if needed
    if [ -z "$(pgrep -u $USER ssh-agent || true)" ]; then
        eval "$(ssh-agent -s)" >/dev/null
    fi
    ssh-add "$KEY_PATH" || true
fi

# Test connection (non-interactive if key works)
echo "🧪 Testing SSH connection to ${REMOTE_USER}@${REMOTE_HOST}..."
ssh -i "$KEY_PATH" -o IdentitiesOnly=yes -o ConnectTimeout=10 -o BatchMode=yes "${REMOTE_USER}@${REMOTE_HOST}" "echo '✅ SSH connection successful!'" || {
    echo "⚠️ Passwordless SSH did not succeed. Ensure the public key is installed on the server and the ssh-agent contains the key."
}

echo "🎉 SSH setup complete. If the test succeeded you can deploy without password prompts."
