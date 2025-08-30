#!/bin/bash

set -euo pipefail

SSH_KEY="$HOME/.ssh/pythonanywhere_key"
SSH_USER="JoeRyanMBA"
SSH_HOST="ssh.pythonanywhere.com"
SSH_REMOTE_BASE="/home/${SSH_USER}/StructuredDocs"

echo "🚀 Uploading frontend and backend to PythonAnywhere..."

# Ensure ssh-agent has the key (best-effort)
if [ -f "$SSH_KEY" ]; then
	if ! ssh-add -l | grep -q "$(basename "$SSH_KEY")" 2>/dev/null; then
		echo "� Adding SSH key to agent..."
		# Start ssh-agent if needed
		if [ -z "$(pgrep -u $USER ssh-agent || true)" ]; then
			eval "$(ssh-agent -s)" >/dev/null
		fi
		ssh-add "$SSH_KEY" || true
	fi
else
	echo "❌ SSH key not found at $SSH_KEY. Run ./setup_ssh_keys.sh to generate and copy it to PythonAnywhere."
fi

# Common SSH options to force using the key and avoid interactive prompts
SSH_OPTS=( -i "$SSH_KEY" -o IdentitiesOnly=yes -o StrictHostKeyChecking=accept-new -o ConnectTimeout=10 )

echo "📁 Creating frontend directory on remote..."
ssh "${SSH_OPTS[@]}" ${SSH_USER}@${SSH_HOST} "mkdir -p ${SSH_REMOTE_BASE}/frontend"
echo "📁 Creating backend directory on remote..."
ssh "${SSH_OPTS[@]}" ${SSH_USER}@${SSH_HOST} "mkdir -p ${SSH_REMOTE_BASE}/backend"

echo "📦 Uploading frontend build files..."
scp "${SSH_OPTS[@]}" -r frontend/dist ${SSH_USER}@${SSH_HOST}:${SSH_REMOTE_BASE}/frontend/

echo "📄 Uploading backend files we changed (app.py + routes/feedback.py)..."
scp "${SSH_OPTS[@]}" backend/app.py ${SSH_USER}@${SSH_HOST}:${SSH_REMOTE_BASE}/backend/
scp "${SSH_OPTS[@]}" backend/routes/feedback.py ${SSH_USER}@${SSH_HOST}:${SSH_REMOTE_BASE}/backend/routes/

echo "✅ Upload complete!"
echo "🔄 Now reload your web app in PythonAnywhere dashboard"
echo "🌐 Visit https://structureddocs.joe-ryan.mba to see your full application!"
