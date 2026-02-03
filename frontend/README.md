# HealthGYM Frontend

React-based frontend application for the HealthGYM System.

**Owned by: Yeldana Kadenova**

## Features

- **Phase 1**: React app with shared Layout (Sidebar/Header) and Design System
- **Phase 2**: Live Leaderboard UI with auto-refresh
- **Phase 3**: Lazy Loading and performance optimizations (MCP < 1s)
- **Phase 4**: UX polish with max 2 clicks for key flows

## Setup

```bash
cd frontend
npm install
npm run dev
```

The app will run on `http://localhost:3000` with API proxy to `http://localhost:8000`.

## Build

```bash
npm run build
```

Build output will be in `frontend/dist/`. Backend is API-only; dev server runs separately (see root README).

## Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── Layout/          # Shared layout components
│   │   └── UI/               # Reusable UI components
│   ├── pages/                # Page components
│   ├── utils/                # Utility functions (performance, etc.)
│   ├── App.jsx               # Main app component with routing
│   ├── main.jsx              # Entry point
│   └── index.css             # Design system CSS
├── package.json
└── vite.config.js
```

## Design System

The design system is defined in `src/index.css` with CSS variables for:
- Colors (primary, secondary, accent)
- Typography (fonts, sizes, weights)
- Spacing (consistent margins/padding)
- Shadows and transitions

## Performance

- Lazy loading for all route components
- Image lazy loading with Intersection Observer
- Performance monitoring (LCP, FCP)
- Optimized font loading

## Key Flows (Max 2 Clicks)

1. Home → Register/Login → Dashboard (2 clicks)
2. Dashboard → Leaderboard (1 click)
3. Dashboard → Tournaments (1 click)
4. Dashboard → Quick Actions (1 click)
