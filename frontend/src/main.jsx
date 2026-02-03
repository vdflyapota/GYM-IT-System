import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
import './index.css'
import { initPerformanceOptimizations } from './utils/performance'

// Initialize performance optimizations (Phase 3)
initPerformanceOptimizations()

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
