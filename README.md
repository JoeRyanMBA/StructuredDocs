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
Preferred: Docker-based deployment

- Use the multi-stage `Dockerfile` (builds frontend and bundles with backend)
- Local/VPS run:
	- `docker compose -f docker-compose.prod.yml build`
	- `docker compose -f docker-compose.prod.yml up -d`
	- App listens on port 8080

Helper script:

- `./deploy_docker.sh` builds and starts the prod stack
- `./deploy_docker.sh --rebuild` for a clean rebuild
- `./deploy_docker.sh --down` to stop/remove

Legacy: PythonAnywhere

- `deploy_to_pythonanywhere.sh` and `deploy_pythonanywhere.sh` contain the old flow if needed.
./upload_frontend.sh  # Deploy frontend changes
```

