import React, { lazy, Suspense } from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Layout from './components/Layout/Layout'
import LoadingSpinner from './components/UI/LoadingSpinner'

// Lazy load pages for performance (Phase 3 requirement)
const Dashboard = lazy(() => import('./pages/Dashboard'))
const Leaderboard = lazy(() => import('./pages/Leaderboard'))
const Tournaments = lazy(() => import('./pages/Tournaments'))
const Login = lazy(() => import('./pages/Login'))
const Register = lazy(() => import('./pages/Register'))
const Home = lazy(() => import('./pages/Home'))

function App() {
  return (
    <Router>
      <Suspense fallback={<LoadingSpinner />}>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route element={<Layout />}>
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/leaderboard" element={<Leaderboard />} />
            <Route path="/tournaments" element={<Tournaments />} />
          </Route>
        </Routes>
      </Suspense>
    </Router>
  )
}

export default App
