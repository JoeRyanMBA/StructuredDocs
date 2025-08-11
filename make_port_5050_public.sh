
#!/bin/bash
# Make Codespaces port 5050 public on restart

wait_for_port() {
  local port=$1
  local retries=30
  local wait=2
  for ((i=0; i<retries; i++)); do
    if lsof -i :$port &>/dev/null; then
      return 0
    fi
    echo "Waiting for port $port to be open... ($((retries-i)) retries left)"
    sleep $wait
  done
  return 1
}

if command -v gh &>/dev/null; then
  echo "Waiting for port 5050 to be open before making it public..."
  if wait_for_port 5050; then
    echo "Making port 5050 public in Codespaces..."
    gh codespace ports visibility 5050:public -c $CODESPACE_NAME || true
  else
    echo "Port 5050 did not open in time. Skipping making it public."
  fi
else
  echo "GitHub CLI not found. Please make port 5050 public manually if needed."
fi
