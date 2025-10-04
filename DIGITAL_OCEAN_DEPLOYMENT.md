# Digital Ocean Deployment Guide

## Prerequisites

1. Digital Ocean account

2. GitHub repository connected to Digital Ocean

## Deployment Steps

### 1. Connect GitHub Repository

1. Go to [Digital Ocean Dashboard](https://cloud.digitalocean.com/)

2. Navigate to Apps

3. Click "Create App"

4. Choose "GitHub" as source

5. Connect your GitHub account and select the `JoeRyanMBA/StructuredDocs` repository

6. Select the `main` branch

### 2. Configure App Settings

- **Service Name**: `api`

- **Source Directory**: `/`

- **Run Command**: `./start.sh`

- **Environment**: Python

- **Instance Size**: Basic XXS (for development) or Basic XS (for production)

- **Instance Count**: 1

### 3. Environment Variables

Set these environment variables in the App settings:

```

PORT = ${PORT}  # This will be set automatically by DO

ENABLE_BLUEPRINTS_FILE = .enable_blueprints
DATABASE_URL = ${database_url}  # Will be created automatically

FLASK_ENV = production
SECRET_KEY = your-secret-key-here  # Generate a secure random key

```

### 4. Database Setup

The app spec includes an automatic PostgreSQL database setup:

- **Engine**: PostgreSQL 15

- **Size**: Basic

- **Nodes**: 1

### 5. Deploy

1. Click "Create Resources" to deploy

2. Wait for the build and deployment to complete

3. Your app will be available at the generated URL

## Post-Deployment Steps

### 1. Database Migration

Once deployed, you may need to run database migrations. You can do this by:

1. Accessing the app's console in Digital Ocean

2. Running: `python3 run_migrations_production.py`

### 2. Environment Variables

Make sure to set the `SECRET_KEY` environment variable to a secure random value.

### 3. Custom Domain (Optional)

You can add a custom domain in the Digital Ocean App settings.

## Troubleshooting

### Build Failures

- Check the build logs in Digital Ocean

- Ensure all dependencies are listed in `requirements.txt`

- Verify the `start.sh` script has execute permissions

### Runtime Issues

- Check the app logs in Digital Ocean

- Verify database connectivity

- Ensure frontend files are built and copied correctly

### Health Check Failures

- The app includes a `/api/health` endpoint for monitoring

- Check that the database connection is working

- Verify all required environment variables are set

## File Structure

```

/
├── .do/app.yaml          # Digital Ocean app specification

├── Dockerfile            # Container configuration

├── requirements.txt      # Python dependencies

├── start.sh             # Startup script

├── backend/             # Flask backend code

├── frontend/dist/       # Built frontend files

└── .enable_blueprints   # Blueprint configuration

```
