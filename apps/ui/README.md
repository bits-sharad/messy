# MMC Job Matching UI

Angular frontend application for the MMC Job Matching Model API.

## Prerequisites

- Node.js (v18 or higher)
- npm (v9 or higher)

## Installation

1. Navigate to the UI directory:
   ```bash
   cd apps/ui
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

   **Note:** If you're behind a corporate proxy, you may need to configure npm registry settings.

## Development Server

Run the development server:

```bash
npm start
```

Or using Angular CLI:

```bash
ng serve
```

The application will be available at `http://localhost:4200/`

## Build

Build the application for production:

```bash
npm run build
```

The build artifacts will be stored in the `dist/` directory.

## API Configuration

The UI is configured to connect to the backend API at `http://localhost:8000/api/v1`.

To change the API URL, update `src/environments/environment.ts`.

## Project Structure

```
apps/ui/
├── src/
│   ├── app/
│   │   ├── pages/
│   │   │   ├── home/
│   │   │   ├── projects/
│   │   │   └── jobs/
│   │   ├── app.component.ts
│   │   └── app.routes.ts
│   ├── assets/
│   ├── environments/
│   ├── index.html
│   ├── main.ts
│   └── styles.css
├── angular.json
├── package.json
└── tsconfig.json
```

## Troubleshooting

### npm install fails

If you encounter network issues during `npm install`:

1. Check your npm registry configuration:
   ```bash
   npm config get registry
   ```

2. If needed, temporarily use the public registry:
   ```bash
   npm config set registry https://registry.npmjs.org/
   ```

3. After installation, you can revert to your corporate registry if needed.

### CORS Issues

If you see CORS errors when connecting to the API, make sure the FastAPI backend has CORS middleware configured (which it does in `apps/main.py`).

