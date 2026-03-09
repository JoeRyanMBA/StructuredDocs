# Self-Hosting StructuredDocs

This guide walks you through deploying StructuredDocs on your own server using Docker. By the end you will have a fully working instance accessible via a domain name, with a PostgreSQL database, persistent image storage, and email notifications.

---

## What You Will Need

| Requirement | Notes |
|---|---|
| A Linux VPS | Any provider works: Hetzner, DigitalOcean, Vultr, AWS Lightsail, etc. Minimum 1 GB RAM, 1 vCPU. Ubuntu 22.04 recommended. |
| A domain name | Optional but strongly recommended for SSL. |
| A PostgreSQL database | A managed service is easiest (see options below). Can also run PostgreSQL in Docker on the same server. |
| An email provider | For password resets and notifications. SendGrid free tier or any SMTP server works. |
| Git | To clone the repository on your server. |

---

## Step 1 — Provision Your Server

Spin up a VPS with at least **1 GB RAM** running **Ubuntu 22.04**. Once you have SSH access, run the following to keep the system up to date:

```bash
apt-get update && apt-get upgrade -y
```

### Install Docker

The app ships as a Docker container, so Docker is the only runtime dependency on the server.

```bash
# Install prerequisites
apt-get install -y ca-certificates curl gnupg

# Add Docker's official GPG key
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
chmod a+r /etc/apt/keyrings/docker.gpg

# Add Docker repository
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker and the Compose plugin
apt-get update
apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Start Docker and enable it on boot
systemctl start docker
systemctl enable docker
```

Verify the installation:

```bash
docker --version
docker compose version
```

---

## Step 2 — Set Up a PostgreSQL Database

Choose one of these options:

### Option A — Managed Database (Recommended)

A managed PostgreSQL service handles backups, updates, and high availability for you. Good free/cheap options:

- **[Supabase](https://supabase.com)** — free tier, generous limits
- **[Neon](https://neon.tech)** — free tier, serverless Postgres
- **[DigitalOcean Managed Databases](https://www.digitalocean.com/products/managed-databases)** — $15/month, easiest if your VPS is also on DigitalOcean
- **[Railway](https://railway.app)** — free tier with Postgres included

After creating a database, you will receive a connection string that looks like:

```
postgresql://username:password@host:5432/dbname
```

Keep this — you will need it in Step 4.

### Option B — PostgreSQL in Docker on the Same Server

If you want everything in one place, add a PostgreSQL container. Create a file at `/opt/structureddocs/docker-compose.override.yml`:

```yaml
version: '3.8'

services:
  db:
    image: postgres:16-alpine
    restart: unless-stopped
    environment:
      POSTGRES_DB: structureddocs
      POSTGRES_USER: sduser
      POSTGRES_PASSWORD: change-this-password
    volumes:
      - pgdata:/var/lib/postgresql/data

  app:
    depends_on:
      - db

volumes:
  pgdata:
```

Your `DATABASE_URL` would then be:

```
postgresql://sduser:change-this-password@db:5432/structureddocs
```

---

## Step 3 — Clone the Repository

```bash
# Create the application directory
mkdir -p /opt/structureddocs
cd /opt/structureddocs

# Clone the repository
git clone https://github.com/YOUR_ORG/StructuredDocs.git .

# Create persistent data directories
mkdir -p data/images instance

# CRITICAL: The Docker container runs as a non-root user.
# These directories must be world-writable so the container can write files.
chmod 777 data/images instance
```

---

## Step 4 — Create Your Environment File

Create a file called `.env` in `/opt/structureddocs/`. This file contains all your secrets and configuration. **Never commit this file to git.**

```bash
nano /opt/structureddocs/.env
```

Paste and fill in the following. Lines marked **REQUIRED** must be set before the app will work correctly.

```bash
# ─── Security ─────────────────────────────────────────────────────────────────
# REQUIRED: Generate these with: python3 -c "import secrets; print(secrets.token_hex(32))"
SECRET_KEY=replace-with-a-long-random-string
JWT_SECRET_KEY=replace-with-a-different-long-random-string

# ─── Database ─────────────────────────────────────────────────────────────────
# REQUIRED: Your PostgreSQL connection string from Step 2
DATABASE_URL=postgresql://username:password@host:5432/dbname

# Prevent the app from silently falling back to SQLite in production
DISABLE_SQLITE_FALLBACK=1

# ─── CORS / Frontend ──────────────────────────────────────────────────────────
# REQUIRED: The URL users will access the app on (with https:// if using SSL)
# If you are serving the frontend from the same Docker container, this is your server's URL.
FRONTEND_URL=https://yourdomain.com

# ─── Email ────────────────────────────────────────────────────────────────────
# Choose either SendGrid OR SMTP. Leave both blank to disable email.

# Option A: SendGrid
EMAIL_PROVIDER=sendgrid
SENDGRID_API_KEY=SG.xxxxxxxxxxxxxxxxxxxx
SENDGRID_VERIFIED_SENDER=no-reply@yourdomain.com
DEFAULT_FROM_EMAIL=no-reply@yourdomain.com
FROM_NAME=StructuredDocs

# Option B: SMTP (comment out the SendGrid lines above and use these)
# EMAIL_PROVIDER=smtp
# SMTP_HOST=smtp.example.com
# SMTP_PORT=587
# SMTP_USER=your-smtp-username
# SMTP_PASSWORD=your-smtp-password
# MAIL_DEFAULT_SENDER=StructuredDocs <no-reply@yourdomain.com>

# ─── App ──────────────────────────────────────────────────────────────────────
PORT=8080
FLASK_ENV=production
RUN_DB_MIGRATIONS=1

# ─── Optional: Background Jobs & Rate Limiting ────────────────────────────────
# If you add a Redis container or use a managed Redis service, set this.
# Without it, background jobs run synchronously and rate limiting is in-memory.
# REDIS_URL=redis://localhost:6379/0

# ─── Optional: Image Storage (S3 / DigitalOcean Spaces) ──────────────────────
# Without this, images are stored on disk inside the container volume (./data/images).
# SPACES_KEY=your-access-key
# SPACES_SECRET=your-secret-key
# SPACES_BUCKET=your-bucket-name
# SPACES_ENDPOINT=https://nyc3.digitaloceanspaces.com
# SPACES_CDN_ENDPOINT=https://your-bucket.nyc3.cdn.digitaloceanspaces.com

# ─── Optional: Error Tracking ─────────────────────────────────────────────────
# SENTRY_DSN=https://...@sentry.io/...
```

To generate the secret keys, run:

```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

Run it twice to get two different values — one for `SECRET_KEY` and one for `JWT_SECRET_KEY`.

---

## Step 5 — Configure Which Features to Enable

The app uses a `.enable_blueprints` file to control which API modules are loaded. Create it with the standard feature set:

```bash
cat > /opt/structureddocs/.enable_blueprints <<'EOF'
auth
collections
topics
publications
images
search
admin
imports
reviews
variables
snippets
notifications
milestones
feedback
tags
links
export
EOF
```

---

## Step 6 — Build and Start the Application

```bash
cd /opt/structureddocs

# Build the Docker image (this will take a few minutes the first time)
docker compose -f docker-compose.prod.yml up --build -d
```

The startup sequence:
1. Docker builds the image (compiles frontend + installs Python deps)
2. The container starts and runs database migrations automatically (`RUN_DB_MIGRATIONS=1`)
3. Gunicorn starts on port 8080 with 2 workers

Check that it started successfully:

```bash
# View live logs
docker logs -f structureddocs_app

# Confirm the health endpoint responds
curl http://localhost:8080/api/health
```

You should see `{"status": "ok"}` (or similar) from the health check.

---

## Step 7 — Create the Admin User

The application needs an initial admin account. Run this once after the container is up:

```bash
docker exec -it structureddocs_app python3 setup_admin.py
```

This creates:
- **Email:** `admin@example.com`
- **Password:** `admin123`

**Important:** Log in immediately and change both the email address and password via Admin → Users.

---

## Step 8 — Set Up a Reverse Proxy with SSL (Recommended)

Exposing port 8080 directly works, but for a production deployment you should put Nginx in front with SSL. [Caddy](https://caddyserver.com) is the easiest option — it provisions SSL certificates automatically.

### Option A — Caddy (Simplest)

```bash
apt-get install -y debian-keyring debian-archive-keyring apt-transport-https
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | tee /etc/apt/sources.list.d/caddy-stable.list
apt-get update && apt-get install -y caddy
```

Create `/etc/caddy/Caddyfile`:

```
yourdomain.com {
    reverse_proxy localhost:8080
}
```

Then:

```bash
systemctl reload caddy
```

Caddy will automatically obtain and renew a Let's Encrypt SSL certificate. Your app will be accessible at `https://yourdomain.com`.

### Option B — Nginx with Certbot

```bash
apt-get install -y nginx certbot python3-certbot-nginx
```

Create `/etc/nginx/sites-available/structureddocs`:

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 120s;
    }
}
```

```bash
ln -s /etc/nginx/sites-available/structureddocs /etc/nginx/sites-enabled/
nginx -t && systemctl reload nginx

# Obtain SSL certificate
certbot --nginx -d yourdomain.com
```

After setting up SSL, update `FRONTEND_URL` in your `.env` to use `https://`, then restart the container:

```bash
docker compose -f docker-compose.prod.yml restart
```

---

## Step 9 — Point Your Domain

In your domain registrar's DNS settings, create an **A record** pointing your domain to your server's IP address:

```
Type: A
Name: @  (or your subdomain, e.g. "docs")
Value: YOUR_SERVER_IP
TTL: 3600
```

DNS changes can take up to 24 hours to propagate, though usually it is much faster.

---

## Keeping the App Running

The container is configured with `restart: unless-stopped`, so it will automatically restart if it crashes or the server reboots.

### Useful commands

```bash
# View logs
docker logs -f structureddocs_app

# Stop the app
docker compose -f docker-compose.prod.yml down

# Restart the app
docker compose -f docker-compose.prod.yml restart

# Update to the latest code
cd /opt/structureddocs
git pull
docker compose -f docker-compose.prod.yml up --build -d
```

### Backups

If using local disk storage (no S3/Spaces), back up these directories regularly:

- `./instance/` — SQLite database (if not using PostgreSQL)
- `./data/images/` — uploaded images

If using a managed PostgreSQL service, use its built-in backup/snapshot feature.

---

## Troubleshooting

### The container exits immediately
Check the logs:
```bash
docker logs structureddocs_app
```
Common causes: missing `SECRET_KEY`, invalid `DATABASE_URL`, or a port already in use.

### `CORS` errors in the browser
Make sure `FRONTEND_URL` in `.env` exactly matches the URL you are accessing the app on (including `https://` and without a trailing slash).

### Images are not persisting after restart
Check that the volume directories exist and have correct permissions:
```bash
ls -la /opt/structureddocs/data/images
ls -la /opt/structureddocs/instance
# Both should show drwxrwxrwx (777)
chmod 777 /opt/structureddocs/data/images /opt/structureddocs/instance
```

### Database migration errors on startup
Run migrations manually:
```bash
docker exec -it structureddocs_app python3 run_migrations_production.py
```

### Can't log in after restart
If `SECRET_KEY` or `JWT_SECRET_KEY` are not set (or were changed), all existing JWT tokens are invalidated. Ensure these are set to fixed values in your `.env` file — not generated randomly on each start.

---

## Summary Checklist

- [ ] VPS provisioned with Docker installed
- [ ] PostgreSQL database created and connection string obtained
- [ ] Repository cloned to `/opt/structureddocs`
- [ ] `data/images` and `instance` directories created with `chmod 777`
- [ ] `.env` file created with `SECRET_KEY`, `JWT_SECRET_KEY`, `DATABASE_URL`, and `FRONTEND_URL`
- [ ] `.enable_blueprints` file created
- [ ] App built and started with `docker compose up --build -d`
- [ ] Health check passes: `curl http://localhost:8080/api/health`
- [ ] Admin user created via `setup_admin.py` and password changed
- [ ] Reverse proxy (Caddy or Nginx) configured with SSL
- [ ] DNS A record pointing domain to server IP
- [ ] `FRONTEND_URL` updated to `https://` URL and container restarted
