# Build script for reliable asset copying
#!/bin/bash

echo "Building frontend..."
cd frontend
npm run build

echo "Verifying build output..."
if [ ! -f "dist/index.html" ]; then
    echo "ERROR: Frontend build failed - index.html not found"
    exit 1
fi

if [ ! -f "dist/assets/index-*.js" ]; then
    echo "ERROR: Frontend build failed - main JS bundle not found"
    exit 1
fi

echo "Build verification passed!"
ls -la dist/assets/ | grep -E "\.(js|css)$" | wc -l
cd ..

echo "Building Docker image..."
docker build -t structureddocs:latest .

echo "Build complete!"
