# Quick Setup Guide

## Step 1: Configure npm Registry (if needed)

If you encounter network errors, you may need to temporarily use the public npm registry:

```bash
# Check current registry
npm config get registry

# If needed, switch to public registry temporarily
npm config set registry https://registry.npmjs.org/

# After installation completes, you can revert if needed
# npm config set registry https://mgti-dal-so-art.mrshmc.com/artifactory/api/npm/npm/
```

## Step 2: Install Dependencies

Navigate to the UI directory and install:

```bash
cd apps/ui
npm install
```

This will install all Angular dependencies. It may take a few minutes.

## Step 3: Run the Development Server

```bash
npm start
```

Or:

```bash
ng serve
```

The UI will be available at: **http://localhost:4200**

## Step 4: Run the Backend API (if not already running)

Make sure your FastAPI backend is running on `http://localhost:8000`:

```bash
# From the project root
cd /f/Mercer/mecy_api
# Run your FastAPI server (adjust command as needed)
uvicorn apps.main:app --reload
```

## Troubleshooting

### npm install fails with registry error

Try using the public registry as shown in Step 1, or configure your corporate proxy settings.

### Port 4200 already in use

Angular CLI will prompt you to use a different port. Press 'y' to accept, or specify a port:

```bash
ng serve --port 4201
```

### CORS errors

The backend already has CORS configured to allow all origins in development. If you still see CORS errors, check that the backend is running and accessible.

