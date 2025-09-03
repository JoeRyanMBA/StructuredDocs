# StructuredDocs

A collaborative documentation system for structured authoring, review workflows, and publication management.

## Development Environment

### Prerequisites
- Python 3.8+
- Node.js 16+
- npm

### Quick Start

1. **Install Dependencies**
   ```bash
   # Frontend dependencies
   cd frontend
   npm install
   cd ..
   
   # Backend dependencies
   cd backend
   pip install -r requirements.txt
   cd ..
   ```

2. **Start Development Environment**
   ```bash
   # Option 1: Start both frontend and backend together
   ./start_dev.sh
   
   # Option 2: Start individually
   python3 start_backend.py  # Backend on http://localhost:5000
   cd frontend && npm run dev  # Frontend on http://localhost:5173
   ```

3. **Access the Application**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:5000

### Development Notes

- The backend uses Flask with SQLite database for development
- The frontend is a Vue.js 3 application built with Vite
- Both servers support hot reloading for development

### Troubleshooting

If you encounter "stuck" processes:
1. Remove any stale PID files: `rm -f backend/backend.pid frontend/preview.pid`
2. Ensure all dependencies are installed
3. Use the provided startup scripts for proper module resolution

## Deployment

### SSH Setup for Deployment
Before deploying to PythonAnywhere, set up SSH keys:
```bash
./setup_ssh_keys.sh
```

This configures passwordless SSH authentication for deployment scripts.

📖 **Detailed SSH Setup**: See [SSH_SETUP_README.md](SSH_SETUP_README.md) for complete instructions.

### Deployment Commands
```bash
./deploy_fixes.sh     # Deploy backend changes
./upload_frontend.sh  # Deploy frontend changes
```

