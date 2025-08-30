#!/bin/bash
# SSH Key Setup Script for PythonAnywhere Deployment
# Run this script at the start of each new AI chat session

echo "🔑 Setting up SSH keys for PythonAnywhere deployment..."

KEY_PATH="$HOME/.ssh/pythonanywhere_key"
PUB_PATH="$KEY_PATH.pub"

# Create .ssh dir
mkdir -p "$HOME/.ssh"
chmod 700 "$HOME/.ssh"

if [ ! -f "$KEY_PATH" ]; then
    echo "🔐 No existing PythonAnywhere key found. Generating ed25519 key at $KEY_PATH"
    ssh-keygen -t ed25519 -f "$KEY_PATH" -C "pythonanywhere-deployment" -N "" || {
        echo "❌ Failed to generate SSH key. Exiting."; exit 1
    }
    chmod 600 "$KEY_PATH"
    chmod 644 "$PUB_PATH"
    echo "✅ Key generated. Next step: copy the public key to PythonAnywhere."
fi

# Try to copy the public key to PythonAnywhere using ssh-copy-id if available
if command -v ssh-copy-id >/dev/null 2>&1; then
    echo "📤 Copying public key to PythonAnywhere (ssh-copy-id)..."
    ssh-copy-id -i "$PUB_PATH" JoeRyanMBA@ssh.pythonanywhere.com || true
else
    echo "📤 ssh-copy-id not available. Please copy the following public key to your PythonAnywhere account (Web > Account > SSH keys):"
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
echo "🧪 Testing SSH connection to PythonAnywhere..."
ssh -i "$KEY_PATH" -o IdentitiesOnly=yes -o ConnectTimeout=10 -o BatchMode=yes JoeRyanMBA@ssh.pythonanywhere.com "echo '✅ SSH connection successful!'" || {
    echo "⚠️ Passwordless SSH did not succeed. If you were prompted for a password, ensure the public key is installed in your PythonAnywhere account and that the SSH key was added to the agent."
}

echo "🎉 SSH setup script finished. If the test succeeded above you can run deployment scripts without being asked for a password."
