# Bellweaver Frontend

React-based dashboard for viewing school calendar events and user details from the Bellweaver API.

## Structure

```
frontend/
├── src/
│   ├── components/       # React components
│   │   ├── Dashboard.jsx # Main dashboard component
│   │   └── Dashboard.css # Dashboard styles
│   ├── services/         # API service layer
│   │   └── api.js        # API client for backend
│   ├── App.jsx           # Root component
│   ├── App.css           # App styles
│   ├── main.jsx          # Entry point
│   └── index.css         # Global styles
├── index.html            # HTML template
├── vite.config.js        # Vite configuration
└── package.json          # Dependencies
```

## Features

- Displays user details from Compass
- Shows first 10 upcoming calendar events
- Responsive design with dark/light mode support
- Error handling and loading states
- Proxied API requests to Flask backend

## Getting Started

### Prerequisites

- Node.js 18+ and npm
- Bellweaver backend API running on port 5000

### Installation

```bash
cd frontend
npm install
```

### Development

1. Start the backend API server (from the `backend/` directory):
   ```bash
   cd ../backend
   poetry run bellweaver api serve
   ```

2. In a new terminal, start the frontend dev server:
   ```bash
   cd frontend
   npm run dev
   ```

3. Open http://localhost:3000 in your browser

The Vite dev server includes:
- Hot module replacement (HMR) for instant updates
- Proxy to backend API at `http://localhost:5000`
- Automatic reload on file changes

### Build for Production

```bash
npm run build
npm run preview
```

## API Integration

The frontend connects to two backend endpoints:

- **GET /user** - Returns user details from latest Compass sync
- **GET /events** - Returns calendar events from latest Compass sync

API requests are proxied through Vite dev server (configured in `vite.config.js`).
