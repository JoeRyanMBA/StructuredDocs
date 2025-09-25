# StructuredDocs

## Quick Start

### Frontend (Vercel)
- Repo root contains `frontend/` linked to your Vercel project.
- On push to `main`, Vercel builds the frontend with Vite.
- Ensure `VITE_API_BASE_URL` is set in Vercel Project Settings → Environment Variables to your DigitalOcean backend URL, e.g. `https://api.yourdomain.com`.

### Backend (DigitalOcean)
Use whichever DO target you’ve set up:

- App Platform: push to `main` triggers a deploy. Otherwise, click Redeploy in the dashboard.
- Droplet + systemd + Gunicorn:
	- SSH into the Droplet and pull/restart:
		```bash
		ssh <user>@<droplet-ip>
		cd /srv/StructuredDocs  # your project directory
		git pull origin main
		sudo systemctl restart structureddocs.service
		sudo systemctl status structureddocs.service --no-pager
		```
- Droplet + Docker Compose:
	- Build and start the production stack:
		```bash
		docker compose -f docker-compose.prod.yml build
		docker compose -f docker-compose.prod.yml up -d
		docker ps --filter name=structureddocs_app
		```

### Environment variables
- Frontend (Vercel): `VITE_API_BASE_URL=https://your-backend-domain`
- Backend (DO): `DATABASE_URL`, `JWT_SECRET_KEY`, and any email/SMTP settings required.

See `.env.example` and `EMAIL_SENDING_README.md` for email provider configuration and DMARC alignment guidance.

### Legacy

PythonAnywhere artifacts and scripts have been removed. Docker-based deployment remains available via `docker-compose.prod.yml` and `deploy_docker.sh` for servers you control.

